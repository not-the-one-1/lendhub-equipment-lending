import json
import logging
import queue
import threading
import tkinter as tk
from tkinter import filedialog
from datetime import date
from config.settings import APP_NAME,PREFERENCES_PATH,ROOT
from services.auth_service import AuthService
from services.equipment_service import EquipmentService
from services.loan_service import LoanService
from services.trust_service import TrustService
from services.stats_service import StatsService
from services.export_service import ExportService
from services.errors import ValidationError
from ui.theme import C,apply_theme
from ui.components.widgets import frame,label,button,Toast
from ui.pages.login_page import LoginPage
from ui.pages.dashboard_page import DashboardPage,ReportsPage
from ui.pages.student_home import StudentHome
from ui.pages.catalogue_page import CataloguePage
from ui.pages.my_loans_page import MyLoansPage
from ui.pages.approvals_page import ApprovalsPage
from ui.pages.returns_page import ReturnsPage
from ui.pages.users_page import UsersPage
from ui.pages.risky_users_page import RiskyUsersPage
from ui.pages.settings_page import SettingsPage

PAGES={'Dashboard':DashboardPage,'Home':StudentHome,'Borrow Equipment':CataloguePage,'Equipment':CataloguePage,'My Loans':MyLoansPage,'Approvals':ApprovalsPage,'Returns':ReturnsPage,'Students':UsersPage,'Risky Users':RiskyUsersPage,'Reports':ReportsPage,'Settings':SettingsPage}
ICONS={'Dashboard':'◈','Home':'⌂','Borrow Equipment':'⇄','My Loans':'▤','Equipment':'▦','Approvals':'✓','Returns':'↩','Students':'◎','Risky Users':'!','Reports':'▥','Settings':'⚙'}
DESCRIPTIONS={'Dashboard':'Your equipment desk, at a glance.','Home':'Everything you need for your next project.','Borrow Equipment':'Discover, request, and create.','Equipment':'Manage the campus equipment collection.','My Loans':'Keep every request and return in view.','Approvals':'Review requests and prepare equipment for collection.','Returns':'Close the loop. Keep equipment moving.','Students':'Fair access starts with a clear picture.','Risky Users':'Support students who need a fresh start.','Reports':'Understand how your campus borrows.','Settings':'Your LendHub preferences.'}

class App(tk.Tk):
    def __init__(self,db,preferences_path=PREFERENCES_PATH):
        super().__init__(); self.db=db; self.preferences_path=preferences_path
        self.title(APP_NAME+' — Campus Equipment Lending')
        try: self.iconbitmap(str(ROOT/'assets'/'icons'/'lendhub.ico'))
        except tk.TclError: pass
        width=min(1500,self.winfo_screenwidth()-60); height=min(940,self.winfo_screenheight()-90)
        self.geometry(f'{width}x{height}+30+25'); self.minsize(1120,620)
        try: self.theme=json.loads(preferences_path.read_text(encoding='utf-8')).get('theme','dark')
        except (OSError,ValueError): self.theme='dark'
        apply_theme(self,self.theme)
        self.auth=AuthService(db); self.equipment=EquipmentService(db,self.auth); self.loans=LoanService(db,self.auth); self.trust=TrustService(db,self.auth); self.stats=StatsService(db,self.auth); self.exports=ExportService(self.auth,self.loans,self.equipment)
        self.current_page='Dashboard'; self.collapsed=False; self.busy=False; self.completed=queue.Queue()
        self.show_login(); self.after(100,self.poll_jobs)
    def clear(self):
        for widget in self.winfo_children(): widget.destroy()
    def show_login(self):
        self.auth.logout(); self.clear(); self.login_page=LoginPage(self,self); self.login_page.pack(fill='both',expand=True)
    def allowed_pages(self):
        if self.auth.current_user['role']=='student': return ['Home','Borrow Equipment','My Loans','Settings']
        return ['Dashboard','Borrow Equipment','Approvals','Returns','Equipment','Students','Risky Users','Reports','Settings']
    def show_shell(self,page=None):
        self.clear(); user=self.auth.current_user
        self.sidebar=frame(self,C['sidebar'],width=78 if self.collapsed else 215); self.sidebar.pack(side='left',fill='y'); self.sidebar.pack_propagate(False)
        brand=frame(self.sidebar); brand.pack(fill='x',padx=18,pady=(24,24))
        label(brand,'◈',27,color=C['blue'],bold=True).pack(side='left')
        if not self.collapsed: label(brand,'LendHub',22,bold=True).pack(side='left',padx=(8,0))
        if not self.collapsed: label(self.sidebar,'CAMPUS WORKSPACE',9,color=C['muted'],bold=True).pack(anchor='w',padx=22,pady=(0,14))
        self.nav_buttons={}
        for name in self.allowed_pages():
            b=button(self.sidebar,ICONS[name]+('   '+name if not self.collapsed else ''),lambda n=name:self.navigate(n),'secondary',anchor='w',padx=14)
            b.configure(bg=C['sidebar'],font=('Segoe UI',10),pady=6); b.pack(fill='x',padx=10,pady=2); self.nav_buttons[name]=b
        bottom=frame(self.sidebar); bottom.pack(side='bottom',fill='x',padx=16,pady=20)
        button(bottom,'↪' if self.collapsed else 'Sign out',self.show_login,'secondary').pack(fill='x',pady=(16,0),side='bottom')
        if not self.collapsed:
            label(bottom,user['name'],11,bold=True,wraplength=175,justify='left').pack(anchor='w')
            label(bottom,user['role'].title(),10,color=C['muted']).pack(anchor='w',pady=(4,10))
            label(bottom,'BORROW · USE · RESPECT',8,color=C['muted']).pack(anchor='w')
        self.main=frame(self); self.main.pack(side='left',fill='both',expand=True)
        self.topbar=frame(self.main,C['panel'],height=91); self.topbar.pack(fill='x'); self.topbar.pack_propagate(False)
        button(self.topbar,'≡',self.toggle_sidebar,'secondary',padx=12).pack(side='left',padx=(22,17))
        titles=frame(self.topbar); titles.pack(side='left',fill='y',pady=16)
        self.title_label=label(titles,'',20,bold=True); self.title_label.pack(anchor='w')
        self.subtitle_label=label(titles,'',10,color=C['muted']); self.subtitle_label.pack(anchor='w',pady=(3,0))
        status=frame(self.topbar); status.pack(side='right',padx=24)
        label(status,date.today().strftime('%a, %d %b %Y'),10,color=C['muted']).pack(anchor='e')
        self.job_status=label(status,'●  Local workspace',10,color=C['green']); self.job_status.pack(anchor='e',pady=(5,0))
        frame(self.main,C['border'],height=1).pack(fill='x')
        self.page_area=frame(self.main); self.page_area.pack(fill='both',expand=True)
        self.navigate(page or ('Home' if user['role']=='student' else 'Dashboard'))
    def navigate(self,name):
        if name not in self.allowed_pages(): return self.toast('This page is not available for your role.','red')
        self.current_page=name
        for widget in self.page_area.winfo_children(): widget.destroy()
        for title,b in self.nav_buttons.items(): b.configure(bg=C['blue_bg'] if title==name else C['sidebar'],fg=C['text'] if title==name else C['muted'])
        self.title_label.configure(text=name); self.subtitle_label.configure(text=DESCRIPTIONS[name])
        self.page=PAGES[name](self.page_area,self); self.page.pack(fill='both',expand=True)
    def toggle_sidebar(self):
        self.collapsed=not self.collapsed; self.show_shell(self.current_page)
    def set_theme(self,mode):
        self.theme=mode; self.preferences_path.parent.mkdir(parents=True,exist_ok=True)
        self.preferences_path.write_text(json.dumps({'theme':mode}),encoding='utf-8')
        apply_theme(self,mode); self.show_shell(self.current_page)
    def toast(self,text,tone='green'): Toast(self,text,tone)
    def perform(self,fn,message=None):
        try:
            result=fn()
            if message: self.navigate(self.current_page); self.toast(message)
            return result
        except (ValidationError,ValueError,OSError) as exc: self.toast(str(exc),'red')
    def run_job(self,fn,message):
        if self.busy: return self.toast('Please wait for the current export or import.','yellow')
        self.busy=True; self.job_status.configure(text='Working…',fg=C['yellow'])
        def work():
            try: self.completed.put((True,fn(),message))
            except Exception as exc: self.completed.put((False,str(exc),message))
        threading.Thread(target=work,daemon=True).start()
    def poll_jobs(self):
        try:
            ok,result,message=self.completed.get_nowait(); self.busy=False
            if self.auth.current_user:
                self.navigate(self.current_page); self.job_status.configure(text='●  Local workspace',fg=C['green'])
            self.toast(message if ok else str(result),'green' if ok else 'red')
        except queue.Empty: pass
        self.after(100,self.poll_jobs)
    def export_file(self,kind,ident=None):
        folder=ROOT/'exports'; folder.mkdir(exist_ok=True)
        extension='pdf' if kind=='pdf' else 'png' if kind=='qr' else 'csv'
        initial=f'loan-L{ident:04}.pdf' if kind=='pdf' else f'equipment-{ident}-qr.png' if kind=='qr' else f'lendhub-{kind}-{date.today()}.csv'
        path=filedialog.asksaveasfilename(parent=self,title='Save '+kind.upper(),initialdir=str(folder),initialfile=initial,defaultextension='.'+extension,filetypes=[(extension.upper(),'*.'+extension)])
        if not path: return
        fn={'loans':lambda:self.exports.loans_csv(path),'equipment':lambda:self.exports.equipment_csv(path),'pdf':lambda:self.exports.loan_pdf(path,ident),'qr':lambda:self.exports.equipment_qr(path,ident)}[kind]
        self.run_job(fn,'Saved '+path)
    def import_equipment(self):
        path=filedialog.askopenfilename(parent=self,title='Import equipment CSV',filetypes=[('CSV files','*.csv')])
        if path: self.run_job(lambda:self.equipment.import_csv(path),'Equipment imported successfully.')
    def report_callback_exception(self,exc_type,exc_value,traceback):
        logging.error('UI callback failed',exc_info=(exc_type,exc_value,traceback))
        self.toast('An unexpected error occurred. Details are in data/lendhub.log.','red')
