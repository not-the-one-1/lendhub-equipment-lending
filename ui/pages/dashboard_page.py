import tkinter as tk
from config.rules import TRUST_BANDS
from ui.pages.base import Page
from ui.components.widgets import *
from ui.components.dialogs import BorrowDialog,ProfileDialog

class DashboardPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.stats=app.stats.dashboard()
        label(self.content,'CAMPUS AT A GLANCE',9,color=C['muted'],bold=True).pack(anchor='w',pady=(0,12))
        stats=frame(self.content); stats.pack(fill='x',pady=(0,18))
        definitions=[('total','Total equipment','▦','yellow'),('available','Available','✓','green'),('lent','Currently lent','⇄','blue'),('overdue','Overdue','◷','red'),('at_risk','At-risk students','!','red')]
        for i,(key,title,icon,tone) in enumerate(definitions):
            stats.columnconfigure(i,weight=1,uniform='stats')
            card=Card(stats,height=98); card.grid(row=0,column=i,sticky='nsew',padx=(0 if i==0 else 10,0)); card.pack_propagate(False)
            label(card,icon,28,color=C[tone],bold=True).place(x=16,y=25)
            label(card,title,10,color=C['muted']).place(x=62,y=20)
            label(card,str(self.stats[key]),28,bold=True).place(x=60,y=40)
        row=frame(self.content); row.pack(fill='x',pady=(0,18))
        for i,weight in enumerate((4,2,2)): row.columnconfigure(i,weight=weight,uniform='dash')
        equipment=Card(row,'Available equipment',height=390); equipment.grid(row=0,column=0,sticky='nsew',padx=(0,12)); equipment.pack_propagate(False)
        tools=frame(equipment); tools.pack(fill='x',padx=14,pady=(0,10))
        self.query=tk.StringVar(); search=entry(tools,self.query); search.pack(fill='x',ipady=8)
        label(tools,'Search by name, category or equipment code',9,color=C['muted']).pack(anchor='w',pady=(4,0))
        self.table=Table(equipment,[('code','ID',55),('name','EQUIPMENT',190),('stock','STOCK',55)],height=3)
        self.table.pack(fill='both',expand=True,padx=10)
        foot=frame(equipment); foot.pack(fill='x',padx=14,pady=12)
        button(foot,'View catalogue',lambda:app.navigate('Borrow Equipment'),'secondary').pack(side='left')
        button(foot,'Borrow',self.borrow).pack(side='right')
        self.query.trace_add('write',self.refresh_equipment); self.refresh_equipment()
        student=Card(row,'Student information',height=390); student.grid(row=0,column=1,sticky='nsew',padx=(0,12)); student.pack_propagate(False)
        self.students=app.trust.list_students(); self.student_map={f"{u['code']} · {u['name']}":u for u in self.students}
        self.student=tk.StringVar(value=next((k for k,u in self.student_map.items() if u['code']=='STU001'),next(iter(self.student_map),'')))
        combo(student,self.student,list(self.student_map),24).pack(fill='x',padx=14,pady=(0,8))
        self.student_area=frame(student); self.student_area.pack(fill='both',expand=True,padx=16,pady=4)
        self.student.trace_add('write',self.refresh_student); self.refresh_student()
        guide=Card(row,'Trust level guide',height=390); guide.grid(row=0,column=2,sticky='nsew'); guide.pack_propagate(False)
        ranges=['80–100','60–79','40–59','20–39','0–19']
        for (threshold,name,description,tone),number in zip(TRUST_BANDS,ranges):
            item=frame(guide); item.pack(fill='x',padx=16,pady=8)
            heading=frame(item); heading.pack(fill='x')
            label(heading,number,9,color=C[tone],bold=True).pack(side='left')
            label(heading,name,10,bold=True).pack(side='left',padx=(8,0))
            label(item,description,9,color=C['muted'],wraplength=210,justify='left').pack(anchor='w')
        lower=frame(self.content); lower.pack(fill='x')
        for i in range(3): lower.columnconfigure(i,weight=1,uniform='lower')
        top=Card(lower,'Most borrowed equipment'); top.grid(row=0,column=0,sticky='nsew',padx=(0,12)); bar_chart(top,self.stats['top_items'],height=210).pack(fill='x')
        monthly=Card(lower,'Loans per month'); monthly.grid(row=0,column=1,sticky='nsew',padx=(0,12)); bar_chart(monthly,self.stats['monthly'],'green',210).pack(fill='x')
        recent=Card(lower,'Recent activity'); recent.grid(row=0,column=2,sticky='nsew')
        for loan in self.stats['recent'][:4]:
            item=frame(recent); item.pack(fill='x',padx=15,pady=7)
            tone='green' if loan['score_delta']>=0 else 'red'
            label(item,f"{loan['score_delta']:+}",13,color=C[tone],bold=True).pack(side='right',padx=(7,0))
            label(item,loan['condition'].title()+' return',10,bold=True).pack(anchor='w')
            label(item,f"{loan['student_code']} · {loan['returned_at']}",9,color=C['muted']).pack(anchor='w',pady=(2,0))
        label(self.content,f"{self.stats['pending']} requests awaiting approval   ·   {self.stats['maintenance']} units in maintenance   ·   {self.stats['lost']} units lost",10,color=C['muted']).pack(anchor='w',pady=(14,0))
    def refresh_equipment(self,*args):
        rows=self.app.equipment.list_equipment(self.query.get(),available_only=True)
        self.table.set_rows([(e['id'],(e['code'],e['name'],e['available']),'green') for e in rows])
    def refresh_student(self,*args):
        for w in self.student_area.winfo_children(): w.destroy()
        u=self.student_map.get(self.student.get())
        if not u: return
        limits=u['limits']; p=self.student_area
        initials=''.join(part[0] for part in u['name'].split()[:2])
        label(p,initials,18,color=C['blue'],bold=True,padx=10,pady=0).pack(anchor='w')
        label(p,u['name'],12,bold=True,wraplength=220,justify='left').pack(anchor='w',pady=(3,2))
        label(p,u['department'],10,color=C['muted']).pack(anchor='w')
        pill(p,f"Score {u['score']} · {limits['label']}",limits['color']).pack(anchor='w',pady=8)
        for title,value in [('Open loans',f"{u['open_loans']} / {limits['loans']}"),('Max duration',f"{limits['days']} days"),('Privilege',limits['privilege'].title())]:
            line=frame(p); line.pack(fill='x',pady=3); label(line,title,10,color=C['muted']).pack(side='left'); label(line,value,10).pack(side='right')
        button(p,'View profile',lambda:ProfileDialog(self.app,u['id']),'secondary',pady=6).pack(fill='x',side='bottom',pady=6)
    def borrow(self):
        ident=self.table.selected()
        if not ident: return self.app.toast('Select equipment from the table.','yellow')
        user=self.student_map.get(self.student.get())
        BorrowDialog(self.app,ident,user['id'] if user else None)

class ReportsPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.section('Lending insights','Live metrics calculated from the local loan records.')
        stats=app.stats.dashboard()
        actions=frame(self.content); actions.pack(fill='x',pady=(0,20))
        button(actions,'Export loans CSV',lambda:app.export_file('loans')).pack(side='left',padx=(0,10))
        button(actions,'Export equipment CSV',lambda:app.export_file('equipment'),'secondary').pack(side='left')
        summary=Card(self.content); summary.pack(fill='x',pady=(0,18))
        label(summary,f"{stats['late_rate']}% late-return rate",24,bold=True,color=C['yellow']).pack(anchor='w',padx=20,pady=(18,5))
        label(summary,'Returned loans with one or more late days / all returned loans.',11,color=C['muted']).pack(anchor='w',padx=20,pady=(0,18))
        row=frame(self.content); row.pack(fill='x')
        for i,(title,items,tone) in enumerate([('Top borrowed items',stats['top_items'],'blue'),('Monthly borrowing',stats['monthly'],'green'),('Student privileges',stats['privileges'],'yellow')]):
            row.columnconfigure(i,weight=1,uniform='reports'); card=Card(row,title); card.grid(row=0,column=i,sticky='nsew',padx=(0,12 if i<2 else 0)); bar_chart(card,items,tone,240).pack(fill='x')
