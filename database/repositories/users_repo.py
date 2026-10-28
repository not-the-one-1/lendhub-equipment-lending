import json

def get(conn, user_id):
    row = conn.execute('SELECT * FROM Utilisateurs WHERE id=?', (user_id,)).fetchone()
    return dict(row) if row else None

def by_email(conn, email):
    row = conn.execute('SELECT * FROM Utilisateurs WHERE email=? COLLATE NOCASE', (email,)).fetchone()
    return dict(row) if row else None

def list_all(conn, students_only=False):
    sql = 'SELECT * FROM Utilisateurs'
    if students_only:
        sql += " WHERE role='student'"
    return [dict(r) for r in conn.execute(sql + ' ORDER BY name')]

def create(conn, *, code, name, email, password_hash, role='student', department='', phone='', score=85, privilege='trusted'):
    return conn.execute('INSERT INTO Utilisateurs(code,name,email,password_hash,role,department,phone,score,privilege) VALUES(?,?,?,?,?,?,?,?,?)',
        (code,name,email,password_hash,role,department,phone,score,privilege)).lastrowid

def update(conn, user_id, **fields):
    allowed = {'name','email','phone','department','password_hash','score','privilege','privilege_override','blocked_until','blacklisted','audit_log'}
    if not fields or not set(fields) <= allowed:
        raise ValueError('Unsupported user fields')
    conn.execute('UPDATE Utilisateurs SET ' + ','.join(k+'=?' for k in fields) + ' WHERE id=?', (*fields.values(), user_id))

def audit(conn, user_id, entry):
    entries = json.loads(get(conn, user_id)['audit_log'])
    entries.append(entry)
    update(conn, user_id, audit_log=json.dumps(entries, ensure_ascii=False))
