from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from tests.support import *
from services.errors import ValidationError,PermissionDenied

class LoanTests(ServiceCase):
    def test_request_approve_return_end_to_end(self):
        ident=self.loans.request(3,1,7); self.assertEqual(self.item()['available'],2)
        self.login('tec'); self.loans.approve(ident); self.assertEqual(self.item()['available'],1)
        preview=self.loans.preview_return(ident,'good'); result=self.loans.return_loan(ident,'good','All accessories returned')
        self.assertEqual(preview,result); self.assertEqual(self.item()['available'],2); self.assertEqual(self.user()['score'],87); self.inventory_consistent()
    def test_student_cannot_request_for_someone_else_or_approve(self):
        with self.assertRaises(PermissionDenied): self.loans.request(4,1,7)
        ident=self.loans.request(3,1,7)
        with self.assertRaises(PermissionDenied): self.loans.approve(ident)
    def test_blocked_account_cannot_borrow(self):
        for fields in [dict(blacklisted=1),dict(blacklisted=0,blocked_until='2026-11-01')]:
            self.update_user(**fields)
            with self.assertRaises(ValidationError): self.loans.request(3,2,7)
    def test_duration_and_premium_restrictions(self):
        self.update_user(score=65,privilege='standard')
        with self.assertRaises(ValidationError): self.loans.request(3,1,7)
        for days in (0,-1,15,True,1.5,'7'):
            with self.assertRaises(ValidationError): self.loans.request(3,2,days)
    def test_pending_requests_count_toward_limits(self):
        self.update_user(score=45,privilege='restricted'); self.loans.request(3,2,7)
        with self.assertRaises(ValidationError): self.loans.request(3,2,7)
    def test_approval_rechecks_score_and_stock(self):
        ident=self.loans.request(3,1,21); self.update_user(score=65); self.login('tec')
        with self.assertRaises(ValidationError): self.loans.approve(ident)
        self.assertEqual(self.item()['available'],2)
    def test_reject_and_cancel_dont_change_inventory(self):
        ident=self.loans.request(3,1,7); self.login('tec')
        with self.assertRaises(ValidationError): self.loans.reject(ident,'')
        self.loans.reject(ident,'Reserved for class'); self.assertEqual(self.item()['available'],2)
        self.login('stu1'); ident=self.loans.request(3,1,7); self.loans.cancel(ident)
        with self.assertRaises(ValidationError): self.loans.cancel(ident)
    def test_return_twice_is_rejected_without_stock_change(self):
        ident=self.active(); self.loans.return_loan(ident,'good')
        with self.assertRaises(ValidationError): self.loans.return_loan(ident,'good')
        self.assertEqual(self.item()['available'],2); self.assertEqual(self.user()['score'],87)
    def test_damaged_and_lost_items_stay_unavailable(self):
        first=self.active(); self.loans.return_loan(first,'damaged'); self.assertEqual(self.item()['maintenance'],1)
        second=self.active(uid=4); self.loans.return_loan(second,'lost'); self.assertEqual(self.item()['lost'],1)
        self.assertEqual(self.item()['available'],0); self.inventory_consistent()
        self.equipment.repair_one(1); self.assertEqual(self.item()['available'],1); self.inventory_consistent()
    def test_late_return_triggers_temporary_block(self):
        ident=self.active(eid=2); self.update_user(score=45)
        self.loans.today=lambda:TODAY+timedelta(days=10)
        result=self.loans.return_loan(ident,'good'); self.assertEqual(result['after'],30)
        self.assertEqual(self.user()['blocked_until'],(TODAY+timedelta(days=24)).isoformat())
    def test_overdue_loan_prevents_new_borrowing(self):
        self.active(); self.loans.today=lambda:TODAY+timedelta(days=8)
        with self.assertRaises(ValidationError): self.loans.request(3,2,7)
    def test_invalid_return_condition_rolls_back(self):
        ident=self.active()
        with self.assertRaises(ValidationError): self.loans.return_loan(ident,'broken')
        self.assertEqual(self.item()['available'],1); self.assertEqual(self.user()['score'],85); self.inventory_consistent()
    def test_simultaneous_approvals_do_not_oversell(self):
        self.login('adm'); ids=[self.loans.request(uid,2,7) for uid in (3,4)]
        def approve(ident):
            try: self.loans.approve(ident); return True
            except ValidationError: return False
        with ThreadPoolExecutor(2) as pool: outcomes=list(pool.map(approve,ids))
        self.assertEqual(sum(outcomes),1); self.inventory_consistent()
    def test_students_only_see_own_loans(self):
        self.active(4); self.login('stu1'); self.assertEqual(self.loans.list_loans(user_id=4),[])
