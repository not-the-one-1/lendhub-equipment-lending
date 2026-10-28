import csv
from pathlib import Path
from services.errors import ValidationError
from services.qr_encoder import write_png

def safe_cell(value):
    if value is None: return ''
    if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')): return "'"+value
    return value

def write_csv(path,rows,fields):
    with open(path,'w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore'); writer.writeheader()
        writer.writerows({key:safe_cell(row.get(key,'')) for key in fields} for row in rows)
    return str(path)

def write_pdf(path,title,lines):
    """One-page PDF receipt, written with the PDF standard's built-in font."""
    def escaped(s): return str(s).replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
    commands=['0.045 0.08 0.13 rg 0 722 595 120 re f','BT /F1 27 Tf 40 785 Td 1 1 1 rg (LendHub) Tj ET',f'BT /F1 14 Tf 40 753 Td 0.65 0.8 1 rg ({escaped(title)}) Tj ET','0.1 0.15 0.2 rg']
    y=675
    import textwrap
    for line in lines:
        for part in textwrap.wrap(str(line),76) or ['']:
            commands.append(f'BT /F1 11 Tf 40 {y} Td ({escaped(part)}) Tj ET'); y-=25
    commands.append('BT /F1 10 Tf 40 42 Td (BORROW / USE / RESPECT - Keep this slip for your records.) Tj ET')
    content='\n'.join(commands).encode('cp1252','replace')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',b'<< /Length '+str(len(content)).encode()+b' >>\nstream\n'+content+b'\nendstream']
    out=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
    for i,obj in enumerate(objects,1):
        offsets.append(len(out)); out+=f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    pos=len(out); out+=b'xref\n0 6\n0000000000 65535 f \n'
    for offset in offsets[1:]: out+=f'{offset:010} 00000 n \n'.encode()
    out+=f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n'.encode()
    Path(path).write_bytes(out)
    return str(path)

class ExportService:
    def __init__(self,auth,loans,equipment): self.auth,self.loans,self.equipment=auth,loans,equipment
    def loans_csv(self,path):
        self.auth.require('admin','technician')
        return write_csv(path,self.loans.list_loans(),['id','student_code','student_name','equipment_code','equipment_name','status','requested_at','borrowed_at','due_date','returned_at','condition','late_days','score_delta','decision_reason'])
    def equipment_csv(self,path):
        self.auth.require('admin','technician')
        return write_csv(path,self.equipment.list_equipment(),['code','name','category','total','available','maintenance','lost','premium','description'])
    def loan_pdf(self,path,loan_id):
        loan=next((l for l in self.loans.list_loans() if l['id']==loan_id),None)
        if not loan: raise ValidationError('Loan not found or access is restricted.')
        if loan['status'] not in ('active','returned'): raise ValidationError('Loan slips are available after approval.')
        return write_pdf(path,f"Loan slip / L{loan['id']:04}",[
            f"Student: {loan['student_code']} - {loan['student_name'][:70]}",
            f"Equipment: {loan['equipment_code'][:20]} - {loan['equipment_name'][:70]}",
            f"Collected: {loan['borrowed_at']}",f"Due date: {loan['due_date']}",
            f"Status: {loan['status'].title()}",f"Return date: {loan['returned_at'] or 'Not yet returned'}",'',
            'Return equipment to the campus equipment desk.',
            'Late returns: -5 points per day (maximum -60).',
            'Damage: -25 points. Loss: -60 points.',
            'Damage/loss penalties are added to any late penalty.','',
            'Student signature: __________________________',
            'Technician signature: ______________________',
        ])
    def equipment_qr(self,path,equipment_id):
        item=next((e for e in self.equipment.list_equipment() if e['id']==equipment_id),None)
        if not item: raise ValidationError('Equipment not found.')
        return write_png(path,f'lendhub:equipment:{item["id"]}')
