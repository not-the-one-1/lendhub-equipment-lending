from datetime import date
from ui.components.widgets import *

class Page(ScrollFrame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app
        self.content=frame(self.body); self.content.pack(fill='both',expand=True,padx=24,pady=20)
    def section(self,title,subtitle=None):
        label(self.content,title,20,bold=True).pack(anchor='w')
        if subtitle: label(self.content,subtitle,10,color=C['muted']).pack(anchor='w',pady=(5,20))

def loan_status(loan):
    if loan['status']=='active':
        days=(date.fromisoformat(loan['due_date'])-date.today()).days
        if days<0: return f'{-days}d overdue','red'
        if days<=2: return f'Due in {days}d','yellow'
        return 'Active','green'
    return loan['status'].title(),('green' if loan['status']=='returned' and not loan['late_days'] else 'red' if loan['late_days'] else 'muted')

def loan_rows(loans):
    rows=[]
    for loan in loans:
        status,tone=loan_status(loan)
        rows.append((loan['id'],(f"L{loan['id']:04}",loan['student_name'],loan['equipment_name'],status,loan['due_date'] or 'Awaiting approval',f"{loan['score_delta']:+}" if loan['score_delta'] is not None else '—'),tone))
    return rows

LOAN_COLUMNS=[('id','LOAN',70),('student','STUDENT',160),('equipment','EQUIPMENT',240),('status','STATUS',120),('due','DUE DATE',130),('score','POINTS',65)]
