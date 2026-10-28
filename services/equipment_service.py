import csv
import sqlite3
from database.repositories import equipment_repo as equipment
from services.errors import ValidationError

class EquipmentService:
    def __init__(self, db, auth): self.db, self.auth = db, auth

    def list_equipment(self, query='', category='All categories', available_only=False):
        self.auth.require()
        with self.db.read() as conn: rows = equipment.list_all(conn)
        return [r for r in rows if (not query or query.casefold() in f"{r['code']} {r['name']} {r['category']}".casefold()) and (category=='All categories' or r['category']==category) and (not available_only or r['available']>0)]

    def save(self, name, category, total, premium=False, description='', equipment_id=None, code=None):
        self.auth.require('admin','technician')
        if not name.strip() or not category.strip(): raise ValidationError('Name and category are required.')
        if isinstance(total,bool) or not isinstance(total,int) or not 1 <= total <= 10000: raise ValidationError('Quantity must be a whole number between 1 and 10,000.')
        try:
            with self.db.transaction() as conn:
                if equipment_id:
                    item = equipment.get(conn,equipment_id)
                    if not item: raise ValidationError('Equipment not found.')
                    unavailable = item['total']-item['available']
                    if total < unavailable: raise ValidationError('Quantity cannot be below lent, lost, and maintenance units.')
                    equipment.update(conn,equipment_id,name=name.strip(),category=category.strip(),total=total,available=total-unavailable,premium=int(premium),description=description.strip())
                    return equipment_id
                next_id = max((r['id'] for r in equipment.list_all(conn,True)),default=0)+1
                return equipment.create(conn,code or f'E{next_id:03}',name.strip(),category.strip(),total,premium,description.strip())
        except sqlite3.IntegrityError as exc:
            raise ValidationError('This equipment code is already in use.') from exc

    def repair_one(self, equipment_id):
        self.auth.require('admin','technician')
        with self.db.transaction() as conn:
            item=equipment.get(conn,equipment_id)
            if not item or item['maintenance'] < 1: raise ValidationError('No units are waiting for repair.')
            equipment.update(conn,equipment_id,maintenance=item['maintenance']-1,available=item['available']+1)

    def import_csv(self, path):
        self.auth.require('admin','technician')
        with open(path,newline='',encoding='utf-8-sig') as stream:
            reader=csv.DictReader(stream)
            if not {'code','name','category','total'} <= set(reader.fieldnames or []): raise ValidationError('CSV needs code, name, category, total columns; premium is optional.')
            rows=list(reader)
        if not rows: raise ValidationError('The CSV contains no equipment.')
        try:
            with self.db.transaction() as conn:
                for index,row in enumerate(rows,2):
                    try:
                        total=int(row['total'])
                        premium=row.get('premium','0').strip().lower()
                        if not all(row[k].strip() for k in ('code','name','category')) or not 1<=total<=10000 or premium not in ('0','1','true','false','yes','no',''):
                            raise ValueError()
                    except (ValueError,TypeError,AttributeError): raise ValidationError(f'Invalid equipment data at CSV row {index}.')
                    equipment.create(conn,row['code'].strip(),row['name'].strip(),row['category'].strip(),total,premium in ('1','true','yes'),row.get('description','') or '')
        except sqlite3.IntegrityError as exc: raise ValidationError('A code in the CSV already exists or is duplicated. Nothing was imported.') from exc
        return len(rows)
