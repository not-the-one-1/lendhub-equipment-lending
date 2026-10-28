import tkinter as tk
from ui.pages.base import Page,LOAN_COLUMNS,loan_rows
from ui.components.widgets import *
from ui.components.dialogs import ConfirmDialog

class MyLoansPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.section('My loans','Track requests, due dates, return conditions, and trust changes.')
        self.status=tk.StringVar(value='All loans')
        combo(self.content,self.status,['All loans','pending','active','returned','rejected','cancelled']).pack(anchor='w',pady=(0,15))
        card=Card(self.content); card.pack(fill='both',expand=True)
        self.table=Table(card,LOAN_COLUMNS,height=13,on_select=self.detail); self.table.pack(fill='both',expand=True,padx=12,pady=12)
        self.notes=label(self.content,'Select a row to see its details.',11,color=C['muted'],wraplength=1000,justify='left'); self.notes.pack(anchor='w',pady=14)
        actions=frame(self.content); actions.pack(fill='x')
        button(actions,'Download loan slip',self.pdf).pack(side='left',padx=(0,10))
        button(actions,'Cancel pending request',self.cancel,'secondary').pack(side='left')
        self.status.trace_add('write',self.refresh); self.refresh()
    def refresh(self,*args):
        self.loans=self.app.loans.list_loans(None if self.status.get()=='All loans' else self.status.get()); self.table.set_rows(loan_rows(self.loans))
    def detail(self,ident):
        loan=next((l for l in self.loans if l['id']==ident),None)
        if loan:
            self.notes.configure(text=f"Requested {loan['requested_at']} · Duration {loan['duration_days']} days\n"+(loan['decision_reason'] or loan['notes'] or 'Collect approved equipment from the equipment desk.'))
    def pdf(self):
        if self.table.selected(): self.app.export_file('pdf',self.table.selected())
        else: self.app.toast('Select a loan first.','yellow')
    def cancel(self):
        ident=self.table.selected()
        if ident: ConfirmDialog(self.app,'Cancel request','Cancel this pending equipment request?',lambda:self.app.perform(lambda:self.app.loans.cancel(ident),'Request cancelled.'))
        else: self.app.toast('Select a pending request.','yellow')
