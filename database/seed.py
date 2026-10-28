"""Fictional demo records with dates relative to reset day."""
from datetime import date, timedelta
from database.connection import Database
from database.repositories import users_repo as users, equipment_repo as equipment
from services.auth_service import hash_password
from config.rules import privilege_for

DEMO_PASSWORD = 'LendHub123!'

def seed_database(db, reset=False):
    db.initialize()
    with db.transaction() as conn:
        if conn.execute('SELECT count(*) FROM Utilisateurs').fetchone()[0] and not reset:
            return False
        if reset:
            for table in ('Emprunts','Equipements','Utilisateurs'):
                conn.execute(f'DELETE FROM {table}')
        users.create(conn,code='ADM001',name='Nadia Amrani',email='admin@lendhub.local',password_hash=hash_password(DEMO_PASSWORD),role='admin',department='Campus services')
        users.create(conn,code='TEC001',name='Youssef Idrissi',email='tech@lendhub.local',password_hash=hash_password(DEMO_PASSWORD),role='technician',department='Equipment desk')
        names=['Ahmed Benali','Lina El Amrani','Omar Tazi','Salma Bennani','Adam Alaoui','Imane Saidi','Mehdi Berrada','Sara El Haddadi','Aya Mansouri','Rayan Fassi','Hiba Cherkaoui','Yassine Alami','Nour Zaki','Amine Kabbaj','Ines Rahmani','Hamza Naciri','Malak Rami','Ilyas Idrissi']
        scores=[85,94,78,91,88,72,81,32,90,68,84,55,93,87,15,76,89,82]
        departments=['Computer Science','Design & Media','Engineering','Business']
        today=date.today()
        for i,(name,score) in enumerate(zip(names,scores),1):
            uid=users.create(conn,code=f'STU{i:03}',name=name,email=('student@lendhub.local' if i==1 else f'stu{i:03}@lendhub.local'),password_hash=hash_password(DEMO_PASSWORD),department=departments[(i-1)%4],phone=f'06 00 00 {i:02} 00',score=score,privilege=privilege_for(score))
            if 20<=score<40: users.update(conn,uid,blocked_until=(today+timedelta(days=10)).isoformat())
            if score<20: users.update(conn,uid,blacklisted=1)
        base=[('Dell XPS 13','Laptop',5,1),('Scientific Calculator','Calculator',10,0),('Epson EB-X49','Projector',2,1),('Canon EOS 250D','Camera',3,1),('Apple iPad','Tablet',4,0),('HDMI Cable','Accessory',8,0),('Sony WH-1000XM4','Audio',3,0),('Arduino Starter Kit','Electronics',5,0),('Wacom Intuos','Tablet',2,0),('USB-C Hub','Accessory',6,0)]
        for i in range(40):
            name,category,total,premium=base[i%10]
            name += ['',' / Lab B',' / Media Lab',' / Library'][i//10]
            equipment.create(conn,f'E{i+1:03}',name,category,total,premium,f'Campus {category.lower()} for coursework and student projects.')
        for i in range(40):
            uid=3+i%18; eid=1+i
            start=today-timedelta(days=12+i*4); due=start+timedelta(days=7)
            late=3 if i%7==0 else 0
            condition='damaged' if i==2 else 'lost' if i==3 else 'good'
            delta=-25 if condition=='damaged' else -60 if condition=='lost' else -15 if late else 2
            after=scores[i%18]; before=max(0,min(100,after-delta))
            conn.execute("""INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days,borrowed_at,due_date,returned_at,condition,approved_by,returned_by,score_before,score_after,score_delta,late_days,notes)
                VALUES(?,?,'returned',?,7,?,?,?,?,2,2,?,?,?,?,?)""",(uid,eid,start.isoformat(),start.isoformat(),due.isoformat(),(due+timedelta(days=late)).isoformat(),condition,before,after,after-before,late,'Fictional demo history'))
            if condition!='good':
                column='maintenance' if condition=='damaged' else 'lost'
                conn.execute(f'UPDATE Equipements SET available=available-1,{column}={column}+1 WHERE id=?',(eid,))
        for i in range(12):
            uid=3+i; eid=1+i
            start=today-timedelta(days=10 if 1<=i<=4 else 3); due=start+timedelta(days=7)
            conn.execute("INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days,borrowed_at,due_date,approved_by) VALUES(?,?,'active',?,7,?,?,2)",(uid,eid,start.isoformat(),start.isoformat(),due.isoformat()))
            conn.execute('UPDATE Equipements SET available=available-1 WHERE id=?',(eid,))
        for i in range(6):
            conn.execute("INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days) VALUES(?,?,'pending',?,7)",(6+i,6+i,today.isoformat()))
        for i in range(2):
            conn.execute("INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days,decision_reason,approved_by) VALUES(?,?,'rejected',?,7,'Equipment reserved for a class.',2)",(18+i,16+i,(today-timedelta(days=5)).isoformat()))
    return True

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Seed demo data. Existing records are preserved unless reset is confirmed.')
    parser.add_argument('--reset',action='store_true')
    parser.add_argument('--confirm-reset',action='store_true')
    parser.add_argument('--db')
    args=parser.parse_args()
    if args.reset and not args.confirm_reset:
        parser.error('Use --confirm-reset to acknowledge deletion of current records.')
    db=Database(args.db) if args.db else Database()
    print('Demo data ready.' if seed_database(db,args.reset) else 'Existing data preserved.')
