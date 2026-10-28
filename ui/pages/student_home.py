from datetime import date
from ui.pages.base import Page,loan_rows,LOAN_COLUMNS
from ui.components.widgets import *

class StudentHome(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        user=app.trust.profile(app.auth.current_user['id']); limits=user['limits']; loans=app.loans.list_loans()
        self.section(f"Hello, {user['name'].split()[0]}.",'Your next great project starts with the right equipment.')
        row=frame(self.content); row.pack(fill='x',pady=(0,20)); row.columnconfigure(0,weight=1); row.columnconfigure(1,weight=2)
        trust=Card(row); trust.grid(row=0,column=0,sticky='nsew',padx=(0,18))
        gauge(trust,user['score']).pack(pady=(16,0))
        pill(trust,limits['label'],limits['color']).pack(pady=(4,16))
        label(trust,f"{limits['privilege'].title()} privileges",12,bold=True).pack(pady=(0,20))
        summary=Card(row,'Your borrowing allowance'); summary.grid(row=0,column=1,sticky='nsew')
        inner=frame(summary); inner.pack(fill='both',expand=True,padx=20,pady=8)
        label(inner,f"{user['open_loans']} / {limits['loans']}",34,bold=True,color=C['blue']).pack(anchor='w')
        label(inner,'open loans and pending requests',11,color=C['muted']).pack(anchor='w',pady=(0,12))
        label(inner,f"Up to {limits['days']} days per loan  ·  {'Premium access' if limits['premium'] else 'Standard equipment'}",12).pack(anchor='w')
        message='Return on time to earn +2 points and keep your privileges.'; tone='green'
        overdue=[l for l in loans if l['status']=='active' and l['due_date']<date.today().isoformat()]
        soon=[l for l in loans if l['status']=='active' and 0<=(date.fromisoformat(l['due_date'])-date.today()).days<=2]
        if limits['blocked']:
            message='Borrowing is blocked until '+(user['blocked_until'] or 'an administrator reviews your account')+'.'; tone='red'
        elif overdue:
            message=f'{len(overdue)} overdue loan(s). Return these before borrowing again.'; tone='red'
        elif soon: message=f'{len(soon)} loan(s) due within two days. Plan your return.'; tone='yellow'
        elif user['score']<80: message='Your trust level limits borrowing. On-time returns improve your score.'; tone='yellow'
        label(inner,message,11,color=C[tone],wraplength=570,justify='left').pack(anchor='w',pady=15)
        button(inner,'Explore the catalogue  →',lambda:app.navigate('Borrow Equipment')).pack(anchor='w',pady=(0,12))
        card=Card(self.content,'Your current loans'); card.pack(fill='both',expand=True)
        table=Table(card,LOAN_COLUMNS,height=6); table.pack(fill='both',expand=True,padx=14,pady=(0,16)); table.set_rows(loan_rows([l for l in loans if l['status'] in ('pending','active')]))
        label(self.content,'To return an item, bring it to the equipment desk. A technician records its condition.',11,color=C['muted']).pack(anchor='w',pady=16)
