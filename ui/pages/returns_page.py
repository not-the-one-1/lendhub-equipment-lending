import tkinter as tk
from ui.pages.base import Page,LOAN_COLUMNS,loan_rows
from ui.components.widgets import *
from ui.components.dialogs import ReturnDialog

class ReturnsPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.section('Return desk','Find a loan, inspect the equipment, and preview the trust score before confirming.')
        self.query=tk.StringVar()
        label(self.content,'Search loan, student, equipment, or scan a LendHub QR code',10,color=C['muted']).pack(anchor='w',pady=(0,6))
        e=entry(self.content,self.query); e.pack(fill='x',ipady=10,pady=(0,15))
        card=Card(self.content); card.pack(fill='both',expand=True)
        self.table=Table(card,LOAN_COLUMNS,height=12); self.table.pack(fill='both',expand=True,padx=12,pady=12)
        actions=frame(self.content); actions.pack(fill='x',pady=18)
        button(actions,'Record return',self.return_item).pack(side='left',padx=(0,10))
        button(actions,'Download loan slip',self.pdf,'secondary').pack(side='left')
        self.query.trace_add('write',self.refresh); self.refresh()
        self.table.tree.bind('<Double-1>',lambda e:self.return_item())
    def refresh(self,*args):
        query=self.query.get().strip().casefold(); rows=self.app.loans.list_loans('active')
        if query.startswith('lendhub:equipment:'):
            rows=[l for l in rows if str(l['equipment_id'])==query.rsplit(':',1)[-1]]
        elif query: rows=[l for l in rows if query in f"L{l['id']:04} {l['student_name']} {l['student_code']} {l['equipment_code']} {l['equipment_name']}".casefold()]
        self.table.set_rows(loan_rows(rows))
    def return_item(self):
        ident=self.table.selected()
        if ident: ReturnDialog(self.app,ident)
        else: self.app.toast('Select an active loan.','yellow')
    def pdf(self):
        if self.table.selected(): self.app.export_file('pdf',self.table.selected())
        else: self.app.toast('Select a loan first.','yellow')
