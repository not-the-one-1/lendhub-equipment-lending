import tempfile
import unittest
from pathlib import Path
from datetime import date
from database.connection import Database
from database.repositories import users_repo as users,equipment_repo as equipment,loans_repo as loans
from services.auth_service import AuthService,hash_password
from services.loan_service import LoanService
from services.trust_service import TrustService
from services.equipment_service import EquipmentService

PASSWORD='TestPass123!'
HASH=hash_password(PASSWORD)
TODAY=date(2026,10,28)

class ServiceCase(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.path=Path(self.temp.name)
        self.db=Database(self.path/'test.db'); self.db.initialize()
        with self.db.transaction() as c:
            for code,role in [('ADM','admin'),('TEC','technician'),('STU1','student'),('STU2','student')]:
                users.create(c,code=code,name=code,email=code.lower()+'@test.local',password_hash=HASH,role=role)
            equipment.create(c,'E001','Laptop','Laptop',2,True)
            equipment.create(c,'E002','Cable','Accessory',1)
        self.auth=AuthService(self.db); self.auth.login('stu1@test.local',PASSWORD)
        self.loans=LoanService(self.db,self.auth,today=lambda:TODAY)
        self.trust=TrustService(self.db,self.auth); self.equipment=EquipmentService(self.db,self.auth)
    def tearDown(self): self.temp.cleanup()
    def login(self,role): self.auth.login(role+'@test.local',PASSWORD)
    def user(self,uid=3):
        with self.db.read() as c: return users.get(c,uid)
    def item(self,eid=1):
        with self.db.read() as c: return equipment.get(c,eid)
    def active(self,uid=3,eid=1,days=7):
        self.login('adm'); ident=self.loans.request(uid,eid,days); self.loans.approve(ident); return ident
    def update_user(self,**fields):
        with self.db.transaction() as c: users.update(c,3,**fields)
    def inventory_consistent(self):
        with self.db.read() as c:
            for e in equipment.list_all(c):
                active=c.execute("SELECT count(*) FROM Emprunts WHERE equipment_id=? AND status='active'",(e['id'],)).fetchone()[0]
                self.assertEqual(e['total'],e['available']+e['maintenance']+e['lost']+active)
