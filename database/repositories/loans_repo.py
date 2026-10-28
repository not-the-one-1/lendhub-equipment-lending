JOIN = """SELECT l.*, u.name AS student_name, u.code AS student_code,
    e.name AS equipment_name, e.code AS equipment_code, e.category
    FROM Emprunts l JOIN Utilisateurs u ON u.id=l.user_id
    JOIN Equipements e ON e.id=l.equipment_id"""

def get(conn, loan_id):
    row = conn.execute(JOIN + ' WHERE l.id=?', (loan_id,)).fetchone()
    return dict(row) if row else None

def list_all(conn, user_id=None, status=None):
    clauses, args = [], []
    if user_id is not None:
        clauses.append('l.user_id=?'); args.append(user_id)
    if status:
        clauses.append('l.status=?'); args.append(status)
    query = JOIN + (' WHERE ' + ' AND '.join(clauses) if clauses else '')
    return [dict(r) for r in conn.execute(query + ' ORDER BY l.id DESC', args)]

def open_count(conn, user_id, exclude=None):
    return conn.execute("SELECT count(*) FROM Emprunts WHERE user_id=? AND status IN ('pending','active') AND id != ?", (user_id, exclude or -1)).fetchone()[0]

def overdue_count(conn, user_id, today):
    return conn.execute("SELECT count(*) FROM Emprunts WHERE user_id=? AND status='active' AND due_date<?", (user_id,today.isoformat())).fetchone()[0]

def create(conn, user_id, equipment_id, days, today):
    return conn.execute("INSERT INTO Emprunts(user_id,equipment_id,status,requested_at,duration_days) VALUES(?,?,'pending',?,?)", (user_id,equipment_id,today.isoformat(),days)).lastrowid

def update(conn, loan_id, **fields):
    allowed = {'status','borrowed_at','due_date','returned_at','condition','approved_by','returned_by','decision_reason','notes','score_before','score_after','score_delta','late_days'}
    if not fields or not set(fields) <= allowed:
        raise ValueError('Unsupported loan fields')
    conn.execute('UPDATE Emprunts SET ' + ','.join(k+'=?' for k in fields) + ' WHERE id=?', (*fields.values(),loan_id))
