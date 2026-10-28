from datetime import date, timedelta
from database.repositories import users_repo as users, equipment_repo as equipment, loans_repo as loans
from services.trust_service import restrictions, return_impact, apply_return
from services.errors import ValidationError, PermissionDenied

class LoanService:
    def __init__(self, db, auth, today=date.today):
        self.db, self.auth, self.today = db, auth, today

    def list_loans(self, status=None, user_id=None):
        actor = self.auth.require()
        if actor['role'] == 'student': user_id = actor['id']
        with self.db.read() as conn:
            return loans.list_all(conn, user_id, status)

    def _eligible(self, conn, user_id, equipment_id, days, exclude=None):
        user, item = users.get(conn,user_id), equipment.get(conn,equipment_id)
        if not user or user['role'] != 'student': raise ValidationError('Select a student.')
        if not item or item['archived']: raise ValidationError('Select available equipment.')
        limits = restrictions(user, self.today())
        if limits['blocked']: raise ValidationError('This account is blocked. An administrator can review its status.')
        if isinstance(days, bool) or not isinstance(days,int) or not 1 <= days <= limits['days']:
            raise ValidationError(f"Choose a duration from 1 to {limits['days']} days.")
        if loans.open_count(conn,user_id,exclude) >= limits['loans']:
            raise ValidationError('The loan limit is reached (pending requests also count).')
        if loans.overdue_count(conn,user_id,self.today()):
            raise ValidationError('Return overdue equipment before borrowing again.')
        if item['premium'] and not limits['premium']:
            raise ValidationError('Premium equipment requires a trust score of 80 and trusted privileges.')
        if item['available'] < 1: raise ValidationError('No units are available.')
        return user, item, limits

    def eligibility(self, user_id, equipment_id, days):
        actor = self.auth.require()
        if actor['role'] == 'student' and user_id != actor['id']:
            raise PermissionDenied('You can only request equipment for yourself.')
        with self.db.read() as conn:
            return self._eligible(conn,user_id,equipment_id,days)[2]

    def request(self, user_id, equipment_id, days):
        actor = self.auth.require()
        if actor['role'] == 'student' and actor['id'] != user_id:
            raise PermissionDenied('You can only request equipment for yourself.')
        with self.db.transaction() as conn:
            self._eligible(conn,user_id,equipment_id,days)
            return loans.create(conn,user_id,equipment_id,days,self.today())

    def approve(self, loan_id):
        actor = self.auth.require('technician','admin')
        with self.db.transaction() as conn:
            loan = loans.get(conn,loan_id)
            if not loan or loan['status'] != 'pending': raise ValidationError('Only pending requests can be approved.')
            self._eligible(conn,loan['user_id'],loan['equipment_id'],loan['duration_days'],exclude=loan_id)
            if not equipment.reserve(conn,loan['equipment_id']): raise ValidationError('The last available unit has already been borrowed.')
            today = self.today()
            loans.update(conn,loan_id,status='active',borrowed_at=today.isoformat(),due_date=(today+timedelta(days=loan['duration_days'])).isoformat(),approved_by=actor['id'])

    def reject(self, loan_id, reason):
        actor = self.auth.require('technician','admin')
        if not reason.strip(): raise ValidationError('Enter a refusal reason.')
        with self.db.transaction() as conn:
            loan = loans.get(conn,loan_id)
            if not loan or loan['status'] != 'pending': raise ValidationError('Only pending requests can be refused.')
            loans.update(conn,loan_id,status='rejected',decision_reason=reason.strip(),approved_by=actor['id'])

    def cancel(self, loan_id):
        actor = self.auth.require()
        with self.db.transaction() as conn:
            loan = loans.get(conn,loan_id)
            if not loan or (actor['role']=='student' and loan['user_id']!=actor['id']): raise PermissionDenied('You cannot cancel this request.')
            if loan['status'] != 'pending': raise ValidationError('Only pending requests can be cancelled.')
            loans.update(conn,loan_id,status='cancelled')

    def preview_return(self, loan_id, condition):
        self.auth.require('technician','admin')
        with self.db.read() as conn:
            loan = loans.get(conn,loan_id)
            if not loan or loan['status'] != 'active': raise ValidationError('Select an active loan.')
            user = users.get(conn,loan['user_id'])
            late, delta = return_impact(loan['due_date'],condition,self.today())
            new = max(0,min(100,user['score']+delta))
            return {'late_days':late,'delta':new-user['score'],'before':user['score'],'after':new}

    def return_loan(self, loan_id, condition, notes=''):
        actor = self.auth.require('technician','admin')
        with self.db.transaction() as conn:
            loan = loans.get(conn,loan_id)
            if not loan or loan['status'] != 'active': raise ValidationError('This loan is not active or has already been returned.')
            if self.today().isoformat() < loan['borrowed_at']: raise ValidationError('Return date cannot precede the loan date.')
            user = users.get(conn,loan['user_id'])
            late, delta = return_impact(loan['due_date'],condition,self.today())
            new_score = apply_return(conn,user,delta,self.today())
            equipment.receive(conn,loan['equipment_id'],condition)
            loans.update(conn,loan_id,status='returned',returned_at=self.today().isoformat(),condition=condition,returned_by=actor['id'],notes=notes.strip(),score_before=user['score'],score_after=new_score,score_delta=new_score-user['score'],late_days=late)
            return {'before':user['score'],'after':new_score,'delta':new_score-user['score'],'late_days':late}
