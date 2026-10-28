def get(conn, equipment_id):
    row = conn.execute('SELECT * FROM Equipements WHERE id=?', (equipment_id,)).fetchone()
    return dict(row) if row else None

def list_all(conn, include_archived=False):
    sql = 'SELECT * FROM Equipements' + ('' if include_archived else ' WHERE archived=0')
    return [dict(r) for r in conn.execute(sql + ' ORDER BY id')]

def create(conn, code, name, category, total, premium=False, description=''):
    return conn.execute('INSERT INTO Equipements(code,name,category,total,available,premium,description) VALUES(?,?,?,?,?,?,?)',
        (code,name,category,total,total,int(premium),description)).lastrowid

def reserve(conn, equipment_id):
    return conn.execute('UPDATE Equipements SET available=available-1 WHERE id=? AND available>0 AND archived=0', (equipment_id,)).rowcount == 1

def receive(conn, equipment_id, condition):
    column = {'good': 'available', 'damaged': 'maintenance', 'lost': 'lost'}[condition]
    conn.execute(f'UPDATE Equipements SET {column}={column}+1 WHERE id=?', (equipment_id,))

def update(conn, equipment_id, **fields):
    allowed = {'name','category','total','available','premium','description','archived','maintenance'}
    if not fields or not set(fields) <= allowed:
        raise ValueError('Unsupported equipment fields')
    conn.execute('UPDATE Equipements SET ' + ','.join(k+'=?' for k in fields) + ' WHERE id=?', (*fields.values(), equipment_id))
