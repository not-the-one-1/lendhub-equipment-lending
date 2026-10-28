import tkinter as tk
from ui.pages.base import Page
from ui.components.widgets import *
from ui.components.dialogs import UserDialog,ProfileDialog

class UsersPage(Page):
    def __init__(self,parent,app,risky=False):
        super().__init__(parent,app); self.risky=risky
        self.section('Students needing attention' if risky else 'Student directory','Review trust scores, lending privileges and account history.')
        toolbar=frame(self.content); toolbar.pack(fill='x',pady=(0,16))
        self.query=tk.StringVar(); entry(toolbar,self.query).pack(side='left',fill='x',expand=True,ipady=10,padx=(0,12))
        if app.auth.current_user['role']=='admin' and not risky: button(toolbar,'+ Add student',lambda:UserDialog(app)).pack(side='right')
        card=Card(self.content); card.pack(fill='both',expand=True)
        self.table=Table(card,[('code','STUDENT ID',100),('name','NAME',180),('department','DEPARTMENT',180),('score','SCORE',70),('level','TRUST LEVEL',130),('privilege','PRIVILEGE',100),('loans','LOANS',70)],height=13)
        self.table.pack(fill='both',expand=True,padx=12,pady=12)
        self.table.tree.bind('<Double-1>',lambda e:self.profile())
        button(self.content,'View profile & history',self.profile).pack(anchor='w',pady=18)
        self.query.trace_add('write',self.refresh); self.refresh()
    def refresh(self,*args):
        rows=self.app.trust.list_students(self.risky); query=self.query.get().casefold()
        rows=[u for u in rows if query in f"{u['code']} {u['name']} {u['department']} {u['email']}".casefold()]
        self.table.set_rows([(u['id'],(u['code'],u['name'],u['department'],u['score'],'Blocked' if u['limits']['blocked'] else u['limits']['label'],u['limits']['privilege'].title(),f"{u['open_loans']}/{u['limits']['loans']}"),'red' if u['limits']['blocked'] or u['score']<60 else 'green' if u['score']>=80 else 'yellow') for u in rows])
    def profile(self):
        if self.table.selected(): ProfileDialog(self.app,self.table.selected())
        else: self.app.toast('Select a student first.','yellow')
