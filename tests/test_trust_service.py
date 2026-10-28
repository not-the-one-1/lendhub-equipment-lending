from datetime import timedelta
from tests.support import *
from services.trust_service import restrictions,return_impact
from services.errors import ValidationError,PermissionDenied

class TrustTests(ServiceCase):
    def test_score_below_twenty_cannot_bypass_blacklist_flag(self):
        u=self.user(); u.update(score=19,blacklisted=0)
        self.assertTrue(restrictions(u,TODAY)['blocked'])
    def test_score_boundaries_and_limits(self):
        for score,level,loans,days in [(100,'trusted',5,21),(80,'trusted',5,21),(79,'standard',3,14),(60,'standard',3,14),(59,'restricted',1,7),(40,'restricted',1,7)]:
            u=self.user(); u['score']=score; result=restrictions(u,TODAY)
            self.assertEqual((result['privilege'],result['loans'],result['days']),(level,loans,days))
    def test_block_expires_exactly_on_expiry_date(self):
        u=self.user(); u.update(score=30,blocked_until=(TODAY+timedelta(days=1)).isoformat())
        self.assertTrue(restrictions(u,TODAY)['blocked']); self.assertFalse(restrictions(u,TODAY+timedelta(days=1))['blocked'])
        self.assertEqual(restrictions(u,TODAY+timedelta(days=1))['loans'],1)
    def test_blacklist_does_not_expire(self):
        u=self.user(); u.update(score=10,blacklisted=1,blocked_until='2020-01-01')
        self.assertTrue(restrictions(u,TODAY)['blocked'])
    def test_rewards_penalties_and_combined_damage(self):
        self.assertEqual(return_impact(TODAY.isoformat(),'good',TODAY),(0,2))
        due=(TODAY-timedelta(days=3)).isoformat()
        self.assertEqual(return_impact(due,'good',TODAY),(3,-15))
        self.assertEqual(return_impact(due,'damaged',TODAY),(3,-40))
        self.assertEqual(return_impact(due,'lost',TODAY),(3,-75))
        self.assertEqual(return_impact('2020-01-01','good',TODAY)[1],-60)
    def test_privilege_override_cannot_raise_score_cap(self):
        u=self.user(); u.update(score=65,privilege_override='trusted')
        self.assertEqual(restrictions(u,TODAY)['privilege'],'standard')
        u.update(score=90,privilege_override='restricted'); self.assertEqual(restrictions(u,TODAY)['loans'],1)
    def test_admin_unblock_requires_reason_and_restores_restricted(self):
        self.update_user(score=10,blacklisted=1)
        with self.assertRaises(PermissionDenied): self.trust.administer(3,'unblock','Reviewed')
        self.login('adm')
        with self.assertRaises(ValidationError): self.trust.administer(3,'unblock','')
        self.trust.administer(3,'unblock','Student completed review')
        u=self.user(); self.assertEqual(u['score'],40); self.assertFalse(u['blacklisted']); self.assertIn('Student completed review',u['audit_log'])
    def test_automatic_promotion_on_return(self):
        self.update_user(score=78,privilege='standard'); ident=self.active(eid=2)
        self.loans.return_loan(ident,'good'); self.assertEqual(self.user()['privilege'],'trusted')
    def test_blacklist_and_score_floor_on_loss(self):
        ident=self.active(); self.update_user(score=50)
        self.loans.return_loan(ident,'lost'); u=self.user(); self.assertEqual(u['score'],0); self.assertTrue(u['blacklisted'])
    def test_score_ceiling(self):
        ident=self.active(); self.update_user(score=99)
        impact=self.loans.return_loan(ident,'good'); self.assertEqual(impact['delta'],1); self.assertEqual(self.user()['score'],100)
