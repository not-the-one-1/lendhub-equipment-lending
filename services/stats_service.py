from collections import Counter
from datetime import date, timedelta
from database.repositories import users_repo as users, equipment_repo as equipment, loans_repo as loans
from services.trust_service import restrictions

class StatsService:
    def __init__(self, db, auth): self.db, self.auth = db, auth

    def dashboard(self):
        self.auth.require('admin','technician')
        with self.db.read() as conn:
            items=equipment.list_all(conn,True); history=loans.list_all(conn); students=users.list_all(conn,True)
        active=[l for l in history if l['status']=='active']
        returned=[l for l in history if l['status']=='returned']
        counts=Counter(l['equipment_name'] for l in history if l['status'] in ('active','returned'))
        months=[]
        current=date.today().replace(day=1)
        for i in range(6):
            months.insert(0,current.strftime('%Y-%m')); current=(current-timedelta(days=1)).replace(day=1)
        monthly=Counter((l['borrowed_at'] or '')[:7] for l in history if l['status'] in ('active','returned'))
        return {
            'total':sum(e['total'] for e in items), 'available':sum(e['available'] for e in items if not e['archived']),
            'lent':len(active), 'overdue':sum(l['due_date']<date.today().isoformat() for l in active),
            'at_risk':sum(u['score']<60 or restrictions(u)['blocked'] for u in students),
            'pending':sum(l['status']=='pending' for l in history),
            'maintenance':sum(e['maintenance'] for e in items), 'lost':sum(e['lost'] for e in items),
            'late_rate':round(100*sum(l['late_days']>0 for l in returned)/len(returned),1) if returned else 0,
            'top_items':counts.most_common(5), 'monthly':[(m,monthly[m]) for m in months],
            'privileges':list(Counter(restrictions(u)['privilege'] for u in students).items()),
            'recent':sorted(returned,key=lambda l:(l['returned_at'],l['id']),reverse=True)[:5],
            'active':sorted(active,key=lambda l:l['due_date']),
        }
