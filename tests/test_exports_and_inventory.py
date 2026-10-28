import csv
from tests.support import *
from services.export_service import ExportService,write_csv
from services.qr_encoder import matrix,write_png
from services.errors import ValidationError,PermissionDenied

class ExportInventoryTests(ServiceCase):
    def test_import_is_atomic_on_duplicate(self):
        self.login('adm'); path=self.path/'items.csv'
        path.write_text('code,name,category,total\nNEW,Test,Accessory,2\nE001,Duplicate,Laptop,2\n',encoding='utf-8')
        with self.assertRaises(ValidationError): self.equipment.import_csv(path)
        self.assertEqual(len(self.equipment.list_equipment()),2)
    def test_import_and_inventory_edit_validate_quantities(self):
        self.login('adm'); path=self.path/'items.csv'
        path.write_text('code,name,category,total,premium\nNEW,Test,Accessory,2,yes\n',encoding='utf-8')
        self.assertEqual(self.equipment.import_csv(path),1)
        with self.assertRaises(ValidationError): self.equipment.save('','Accessory',2)
        self.active()
        with self.assertRaises(ValidationError): self.equipment.save('Laptop','Laptop',0,equipment_id=1)
        self.inventory_consistent()
    def test_student_cannot_import_or_export_private_reports(self):
        service=ExportService(self.auth,self.loans,self.equipment)
        with self.assertRaises(PermissionDenied): service.loans_csv(self.path/'report.csv')
        with self.assertRaises(PermissionDenied): self.equipment.import_csv(self.path/'missing.csv')
    def test_csv_formula_injection_is_escaped(self):
        p=self.path/'safe.csv'; write_csv(p,[{'name':' =HYPERLINK("x")','score':-5}],['name','score'])
        with p.open(encoding='utf-8-sig') as stream: row=next(csv.DictReader(stream))
        self.assertTrue(row['name'].startswith("'")); self.assertEqual(row['score'],'-5')
    def test_pdf_permissions_and_valid_structure(self):
        ident=self.active(4); self.login('stu1'); service=ExportService(self.auth,self.loans,self.equipment)
        with self.assertRaises(ValidationError): service.loan_pdf(self.path/'private.pdf',ident)
        self.login('adm'); p=self.path/'slip.pdf'; service.loan_pdf(p,ident)
        data=p.read_bytes(); self.assertTrue(data.startswith(b'%PDF-1.4')); self.assertIn(b'%%EOF',data); self.assertIn(b'L0001',data)
    def test_qr_has_expected_geometry_and_png_header(self):
        qr=matrix('lendhub:equipment:1'); self.assertEqual(len(qr),25); self.assertTrue(all(len(row)==25 and all(bit in (0,1) for bit in row) for row in qr))
        p=self.path/'qr.png'; write_png(p,'lendhub:equipment:1'); self.assertTrue(p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
    def test_database_foreign_keys_and_inventory_constraints(self):
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c: c.execute("INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days) VALUES(999,1,'pending','2026-10-28',7)")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c: c.execute('UPDATE Equipements SET available=-1 WHERE id=1')
