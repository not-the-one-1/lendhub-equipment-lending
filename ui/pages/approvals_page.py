from ui.pages.base import Page
from ui.components.widgets import *
from ui.components.dialogs import ReasonDialog,ConfirmDialog,ProfileDialog

class ApprovalsPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.rows=app.loans.list_loans('pending')
        self.section('Approval queue',f'{len(self.rows)} requests waiting for review. Stock and trust limits are checked again on approval.')
        card=Card(self.content); card.pack(fill='both',expand=True)
        self.table=Table(card,[('id','REQUEST',80),('student','STUDENT',170),('equipment','EQUIPMENT',250),('requested','REQUESTED',120),('duration','DURATION',100)],height=12); self.table.pack(fill='both',expand=True,padx=12,pady=12)
        self.table.set_rows([(l['id'],(f"L{l['id']:04}",l['student_name'],l['equipment_name'],l['requested_at'],f"{l['duration_days']} days"),'muted') for l in self.rows])
        actions=frame(self.content); actions.pack(fill='x',pady=18)
        button(actions,'Approve request',self.approve).pack(side='left',padx=(0,10))
        button(actions,'Refuse with reason',self.reject,'danger').pack(side='left',padx=(0,10))
        button(actions,'Student profile',self.profile,'secondary').pack(side='left')
    def chosen(self):
        ident=self.table.selected()
        if not ident: self.app.toast('Select a request first.','yellow')
        return ident
    def approve(self):
        ident=self.chosen()
        if ident: ConfirmDialog(self.app,'Approve request','Approve collection? The loan starts today and one unit is removed from available stock.',lambda:self.app.perform(lambda:self.app.loans.approve(ident),'Request approved. Equipment is ready for collection.'))
    def reject(self):
        ident=self.chosen()
        if ident: ReasonDialog(self.app,'Refuse request',lambda reason,value:self.app.loans.reject(ident,reason))
    def profile(self):
        ident=self.chosen()
        if ident: ProfileDialog(self.app,next(l['user_id'] for l in self.rows if l['id']==ident))
