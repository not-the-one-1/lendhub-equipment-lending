from datetime import date, timedelta
from config import rules
from database.repositories import users_repo as users, loans_repo as loans
from services.errors import ValidationError

def restrictions(user, today=None):
    today = today or date.today()
    level = rules.privilege_for(user['score'])
    if user.get('privilege_override'):
        level = min((level, user['privilege_override']), key=rules.RANK.get)
    limits = dict(rules.PRIVILEGES[level])
    blocked = bool(user['score'] < 20 or user['blacklisted'] or (user['blocked_until'] and user['blocked_until'] > today.isoformat()))
    limits.update(privilege=level, blocked=blocked, label=rules.band(user['score'])[1], color=rules.band(user['score'])[3])
    if 20 <= user['score'] < 40 and not blocked:
        limits.update(label='Restricted after block', color='orange')
    if blocked:
        limits.update(loans=0, days=0, premium=False)
    return limits

def return_impact(due_date, condition, today=None):
    today = today or date.today()
    if condition not in ('good','damaged','lost'):
        raise ValidationError('Choose a return condition.')
    late = max(0, (today - date.fromisoformat(due_date)).days)
    delta = -min(rules.MAX_LATE_PENALTY, late * rules.LATE_PER_DAY)
    if condition == 'damaged': delta -= rules.DAMAGE_PENALTY
    elif condition == 'lost': delta -= rules.LOSS_PENALTY
    elif late == 0: delta += rules.ON_TIME_REWARD
    return late, delta

def apply_return(conn, user, delta, today):
    new_score = max(0, min(100, user['score'] + delta))
    fields = {'score': new_score, 'privilege': rules.privilege_for(new_score)}
    if delta < 0 and new_score < 20:
        fields.update(blacklisted=1, blocked_until=None)
    elif delta < 0 and new_score < 40:
        fields['blocked_until'] = (today + timedelta(days=rules.BLOCK_DAYS)).isoformat()
    users.update(conn, user['id'], **fields)
    return new_score

class TrustService:
    def __init__(self, db, auth):
        self.db, self.auth = db, auth

    def list_students(self, risky=False):
        actor = self.auth.require()
        with self.db.read() as conn:
            rows = users.list_all(conn, students_only=True) if actor['role'] != 'student' else [users.get(conn, actor['id'])]
            for u in rows:
                u.pop('password_hash', None)
                u['limits'] = restrictions(u)
                u['open_loans'] = loans.open_count(conn, u['id'])
        if risky:
            rows = [u for u in rows if u['score'] < 60 or u['limits']['blocked']]
            rows.sort(key=lambda u: u['score'])
        return rows

    def profile(self, user_id):
        self.auth.require()
        row = next((u for u in self.list_students() if u['id'] == user_id), None)
        if not row:
            raise ValidationError('Student not found or access is restricted.')
        return row

    def administer(self, user_id, action, reason, value=None):
        self.auth.require('admin')
        if not reason.strip():
            raise ValidationError('A reason is required for every trust decision.')
        with self.db.transaction() as conn:
            user = users.get(conn, user_id)
            if not user or user['role'] != 'student':
                raise ValidationError('Select a student.')
            if action == 'unblock':
                # Reviewed accounts restart at the restricted threshold.
                score = max(40, user['score'])
                users.update(conn, user_id, blacklisted=0, blocked_until=None, score=score, privilege=rules.privilege_for(score))
            elif action == 'block':
                users.update(conn, user_id, blacklisted=1)
            elif action == 'privilege':
                if value not in rules.PRIVILEGES and value != 'automatic':
                    raise ValidationError('Choose a valid privilege level.')
                users.update(conn, user_id, privilege_override=None if value == 'automatic' else value)
            else:
                raise ValidationError('Unknown trust action.')
            users.audit(conn, user_id, {'date':date.today().isoformat(), 'by':self.auth.current_user['code'], 'action':action, 'value':value, 'reason':reason.strip(), 'score_before':user['score'], 'score_after':users.get(conn,user_id)['score']})

    def update_profile(self, user_id, name, email, department, phone):
        from services.auth_service import validate_identity
        import sqlite3
        self.auth.require('admin')
        validate_identity(name, email)
        self.profile(user_id)
        try:
            with self.db.transaction() as conn:
                users.update(conn,user_id,name=name.strip(),email=email.strip().lower(),department=department.strip(),phone=phone.strip())
        except sqlite3.IntegrityError as exc:
            raise ValidationError('This email is already in use.') from exc
