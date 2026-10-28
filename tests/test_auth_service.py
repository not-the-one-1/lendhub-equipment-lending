from tests.support import *
from services.auth_service import verify_password,hash_password
from services.errors import ValidationError,PermissionDenied

class AuthTests(ServiceCase):
    def test_salted_hashes_and_verification(self):
        first=hash_password(PASSWORD); second=hash_password(PASSWORD)
        self.assertNotEqual(first,second); self.assertTrue(verify_password(PASSWORD,first)); self.assertFalse(verify_password('wrong',first)); self.assertNotIn(PASSWORD,first)
    def test_malformed_hash_is_rejected(self):
        for value in ('x','pbkdf2_sha256$1$aa$bb',None,'pbkdf2_sha256$260000$invalid$0'):
            self.assertFalse(verify_password(PASSWORD,value))
    def test_case_insensitive_login_and_no_hash_in_session(self):
        self.auth.login('  STU1@TEST.LOCAL ',PASSWORD); self.assertEqual(self.auth.current_user['id'],3); self.assertNotIn('password_hash',self.auth.current_user)
    def test_invalid_login(self):
        with self.assertRaises(ValidationError): self.auth.login('stu1@test.local','wrong')
    def test_logout_revokes_permissions(self):
        self.auth.logout()
        with self.assertRaises(PermissionDenied): self.auth.require()
    def test_change_password_requires_old_and_valid_new(self):
        with self.assertRaises(ValidationError): self.auth.change_password('wrong','NewPass123')
        with self.assertRaises(ValidationError): self.auth.change_password(PASSWORD,'short')
        self.auth.change_password(PASSWORD,'NewPass123')
        with self.assertRaises(ValidationError): self.auth.login('stu1@test.local',PASSWORD)
        self.auth.login('stu1@test.local','NewPass123')
    def test_create_student_permissions_and_duplicate_email(self):
        with self.assertRaises(PermissionDenied): self.auth.create_student('STU5','Alex','alex@test.local',PASSWORD)
        self.login('adm'); self.auth.create_student('STU5','Alex','alex@test.local',PASSWORD)
        with self.assertRaises(ValidationError): self.auth.create_student('STU6','Alex','ALEX@test.local',PASSWORD)
        with self.assertRaises(ValidationError): self.auth.create_student('STU5','Alex','another@test.local',PASSWORD)
    def test_empty_name_invalid_email_and_password(self):
        self.login('adm')
        for code,name,email,password in [('S','','s@test.local',PASSWORD),('S','Name','invalid',PASSWORD),('','Name','s@test.local',PASSWORD),('S','Name','s@test.local','short')]:
            with self.assertRaises(ValidationError): self.auth.create_student(code,name,email,password)
    def test_student_cannot_view_other_profile(self):
        with self.assertRaises(ValidationError): self.trust.profile(4)
        self.assertEqual(len(self.trust.list_students()),1)
