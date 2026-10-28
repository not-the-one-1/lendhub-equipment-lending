import tkinter as tk
from ui.components.widgets import *

class LoginPage(tk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent,bg=C['bg']); self.app=app
        self.columnconfigure(0,weight=1,uniform='login'); self.columnconfigure(1,weight=1,uniform='login'); self.rowconfigure(0,weight=1)
        hero=frame(self,C['sidebar']); hero.grid(row=0,column=0,sticky='nsew')
        brand=frame(hero); brand.pack(fill='x',padx=50,pady=(34,15))
        label(brand,'◈',32,color=C['blue']).pack(side='left',padx=(0,12))
        label(brand,'LendHub',26,bold=True).pack(side='left')
        content=frame(hero); content.pack(fill='both',expand=True,padx=50)
        label(content,'Big ideas.\nShared equipment.',32,bold=True,justify='left').pack(anchor='w',pady=(10,15))
        label(content,'The tools you need,\nfrom a campus you can count on.',14,color=C['muted'],justify='left').pack(anchor='w',pady=(0,16))
        art=tk.Canvas(content,height=190,bg=C['sidebar'],highlightthickness=0); art.pack(fill='x',pady=(0,16))
        art.create_oval(100,0,315,205,fill=C['blue_bg'],outline='')
        art.create_rectangle(90,35,295,160,fill=C['panel'],outline=C['blue'],width=3)
        art.create_rectangle(102,48,283,147,fill=C['raised'],outline='')
        art.create_line(65,177,320,177,fill=C['blue'],width=9)
        art.create_text(193,95,text='CREATE. LEARN. SHARE.',fill=C['text'],font=(FONT,12,'bold'))
        art.create_oval(295,15,355,75,fill=C['green_bg'],outline=C['green'],width=2)
        art.create_text(325,45,text='✓',fill=C['green'],font=(FONT,25,'bold'))
        for text in ('40 equipment types across campus','Fair access through a transparent trust system','One place for requests, approvals and returns'):
            label(content,'✓  '+text,10,color=C['muted'],wraplength=470,justify='left').pack(anchor='w',pady=4)
        right=frame(self); right.grid(row=0,column=1,sticky='nsew')
        card=Card(right,width=430,height=630); card.place(relx=.5,rely=.5,anchor='center'); card.pack_propagate(False)
        inner=frame(card); inner.pack(fill='both',expand=True,padx=34,pady=26)
        pill(inner,'CAMPUS EQUIPMENT PORTAL','blue').pack(anchor='w',pady=(0,16))
        label(inner,'Welcome back',27,bold=True).pack(anchor='w')
        label(inner,'Sign in to your campus account.',11,color=C['muted']).pack(anchor='w',pady=(7,12))
        self.email=tk.StringVar(); self.password=tk.StringVar(); self.error=tk.StringVar(); self.show=tk.BooleanVar()
        self.email_entry=field(inner,'Email address',self.email)
        self.password_entry=field(inner,'Password',self.password,show='•')
        tk.Checkbutton(inner,text='Show password',variable=self.show,command=lambda:self.password_entry.configure(show='' if self.show.get() else '•'),bg=C['panel'],fg=C['muted'],activebackground=C['panel'],selectcolor=C['input'],font=(FONT,10)).pack(anchor='w',pady=(10,12))
        button(inner,'Sign in  →',self.submit).pack(fill='x')
        label(inner,'',10,color=C['red'],textvariable=self.error,wraplength=350,justify='left').pack(anchor='w',pady=(8,0))
        divider(inner)
        label(inner,'EXPLORE THE DEMO',9,color=C['muted'],bold=True).pack(anchor='w',pady=(0,9))
        row=frame(inner); row.pack(fill='x')
        for role,email in [('Student','student'),('Technician','tech'),('Admin','admin')]:
            button(row,role,lambda e=email:self.demo(e),'secondary',padx=0).pack(side='left',expand=True,fill='x',padx=(0,5))
        label(inner,'Demo password: LendHub123!',9,color=C['muted']).pack(anchor='w',pady=(10,0))
        self.email_entry.bind('<Return>',lambda e:self.password_entry.focus_set()); self.password_entry.bind('<Return>',lambda e:self.submit())
        self.email_entry.focus_set()
    def demo(self,name):
        self.email.set(name+'@lendhub.local'); self.password.set('LendHub123!'); self.error.set(''); self.password_entry.focus_set()
    def submit(self):
        from services.errors import ValidationError
        try:
            self.app.auth.login(self.email.get(),self.password.get()); self.app.show_shell()
        except ValidationError as exc: self.error.set(str(exc))
