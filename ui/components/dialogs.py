import tkinter as tk
from datetime import date,timedelta
from ui.theme import C,FONT
from ui.components.widgets import *
from services.errors import ValidationError

class ConfirmDialog(Dialog):
    def __init__(self,app,title,message,action):
        super().__init__(app,title,460,270)
        label(self.body,message,11,color=C['muted'],wraplength=405,justify='left').pack(anchor='w',pady=16)
        row=frame(self.footer); row.pack(fill='x',pady=10)
        button(row,'Cancel',self.destroy,'secondary').pack(side='left')
        button(row,'Confirm',lambda:self.run(lambda:(action(),self.destroy()))).pack(side='right')

class BorrowDialog(Dialog):
    def __init__(self,app,equipment_id=None,user_id=None):
        super().__init__(app,'Borrow equipment',520,625)
        label(self.body,'Choose what you need. A technician approves collection.',10,color=C['muted']).pack(anchor='w')
        self.students=app.trust.list_students(); self.items=app.equipment.list_equipment()
        self.student_map={f"{u['code']} - {u['name']}":u for u in self.students}
        self.item_map={f"{e['code']} - {e['name']}":e for e in self.items}
        self.student=tk.StringVar(); self.item=tk.StringVar(); self.days=tk.StringVar(value='7')
        label(self.body,'Student',10,color=C['muted']).pack(anchor='w',pady=(20,5))
        combo(self.body,self.student,list(self.student_map),48).pack(fill='x')
        label(self.body,'Equipment',10,color=C['muted']).pack(anchor='w',pady=(16,5))
        combo(self.body,self.item,list(self.item_map),48).pack(fill='x')
        field(self.body,'Duration in days',self.days)
        self.due=label(self.body,'',10,color=C['muted']); self.due.pack(anchor='w',pady=10)
        self.info=label(self.body,'',11,wraplength=450,justify='left',anchor='w',padx=14,pady=16)
        self.info.pack(fill='x',pady=8)
        row=frame(self.footer); row.pack(fill='x',side='bottom',pady=6)
        button(row,'Cancel',self.destroy,'secondary').pack(side='left')
        self.submit=button(row,'Send request',lambda:self.run(self.confirm)); self.submit.pack(side='right')
        for variable in (self.student,self.item,self.days): variable.trace_add('write',self.refresh)
        self.student.set(next((k for k,u in self.student_map.items() if u['id']==user_id),next(iter(self.student_map),'')))
        self.item.set(next((k for k,e in self.item_map.items() if e['id']==equipment_id),next(iter(self.item_map),'')))
        self.bind('<Return>',lambda e:self.run(self.confirm)); self.refresh()
    def refresh(self,*args):
        try:
            user=self.student_map.get(self.student.get()); item=self.item_map.get(self.item.get())
            if not user or not item: raise ValidationError('Choose a student and equipment.')
            try: days=int(self.days.get())
            except ValueError: raise ValidationError('Enter a whole number of days.')
            self.due.configure(text=f'If approved today, due {(date.today()+timedelta(days=max(0,min(days,365)))):%d %b %Y}')
            limits=self.app.loans.eligibility(user['id'],item['id'],days)
            self.info.configure(text=f"✓  Eligible to borrow\n\nScore {user['score']} · {limits['label']}\nLimit: {limits['loans']} loans / {limits['days']} days\nStock: {item['available']} units available",fg=C['green'],bg=C['green_bg'])
            self.submit.configure(state='normal')
        except ValidationError as exc:
            self.info.configure(text=f'!  Request unavailable\n\n{exc}',fg=C['yellow'],bg=C['yellow_bg']); self.submit.configure(state='disabled')
    def confirm(self):
        user=self.student_map.get(self.student.get()); item=self.item_map.get(self.item.get())
        if not user or not item: raise ValidationError('Choose a student and equipment.')
        ident=self.app.loans.request(user['id'],item['id'],int(self.days.get()))
        self.close_success(f'Request L{ident:04} sent for approval.')

class ReturnDialog(Dialog):
    def __init__(self,app,loan_id):
        super().__init__(app,'Return equipment',510,650)
        self.loan_id=loan_id
        loan=next(l for l in app.loans.list_loans('active') if l['id']==loan_id)
        label(self.body,f"L{loan_id:04} · {loan['student_name']}",11,color=C['muted']).pack(anchor='w',pady=6)
        label(self.body,loan['equipment_name'],13,bold=True).pack(anchor='w')
        label(self.body,f"Due {loan['due_date']}",10,color=C['muted']).pack(anchor='w',pady=(5,15))
        self.condition=tk.StringVar(value='good')
        for value,title in [('good','Good condition'),('damaged','Damaged - move to maintenance'),('lost','Lost - remove from available stock')]:
            tk.Radiobutton(self.body,text=title,variable=self.condition,value=value,bg=C['panel'],fg=C['text'],selectcolor=C['input'],activebackground=C['panel'],activeforeground=C['text'],font=(FONT,11),command=self.preview).pack(anchor='w',pady=5)
        self.impact=label(self.body,'',11,bold=True,padx=12,pady=14); self.impact.pack(fill='x',pady=16)
        label(self.body,'Notes (optional)',10,color=C['muted']).pack(anchor='w',pady=(0,5))
        self.notes=tk.Text(self.body,height=3,bg=C['input'],fg=C['text'],insertbackground=C['text'],relief='flat',font=(FONT,11),padx=10,pady=8); self.notes.pack(fill='x')
        row=frame(self.footer); row.pack(fill='x',side='bottom',pady=5)
        button(row,'Cancel',self.destroy,'secondary').pack(side='left')
        button(row,'Confirm return',lambda:self.run(self.confirm)).pack(side='right')
        self.preview()
    def preview(self):
        impact=self.app.loans.preview_return(self.loan_id,self.condition.get())
        tone='green' if impact['delta']>=0 else 'red'
        self.impact.configure(text=f"Trust score: {impact['before']} → {impact['after']}  ({impact['delta']:+d})\n{impact['late_days']} days late",fg=C[tone],bg=C[tone+'_bg'])
    def confirm(self):
        result=self.app.loans.return_loan(self.loan_id,self.condition.get(),self.notes.get('1.0','end'))
        self.close_success(f"Return recorded. New trust score: {result['after']}.")

class ReasonDialog(Dialog):
    def __init__(self,app,title,on_submit,privilege=False):
        super().__init__(app,title,480,370)
        label(self.body,'Every decision is recorded with your reason.',10,color=C['muted']).pack(anchor='w',pady=5)
        self.value=tk.StringVar(value='automatic'); self.reason=tk.StringVar()
        if privilege:
            label(self.body,'Maximum privilege (trust rules still apply)',10,color=C['muted']).pack(anchor='w',pady=(15,5))
            combo(self.body,self.value,['automatic','restricted','standard','trusted']).pack(fill='x')
        field(self.body,'Reason',self.reason)
        def submit():
            if not self.reason.get().strip(): raise ValidationError('Enter a reason.')
            on_submit(self.reason.get(),self.value.get())
            self.close_success('Decision saved.')
        button(self.footer,'Save decision',lambda:self.run(submit)).pack(side='bottom',fill='x',pady=14)

class EquipmentDialog(Dialog):
    def __init__(self,app,item=None):
        super().__init__(app,'Edit equipment' if item else 'Add equipment',500,575)
        item=item or {}; self.item=item
        self.name=tk.StringVar(value=item.get('name','')); self.category=tk.StringVar(value=item.get('category','Accessory'))
        self.total=tk.StringVar(value=str(item.get('total',1))); self.premium=tk.BooleanVar(value=item.get('premium',False)); self.description=tk.StringVar(value=item.get('description',''))
        field(self.body,'Equipment name',self.name)
        field(self.body,'Category',self.category)
        field(self.body,'Total units (including lent / maintenance / lost)',self.total)
        field(self.body,'Description',self.description)
        tk.Checkbutton(self.body,text='Premium equipment (trusted students only)',variable=self.premium,bg=C['panel'],fg=C['text'],selectcolor=C['input'],activebackground=C['panel'],activeforeground=C['text'],font=(FONT,10)).pack(anchor='w',pady=15)
        button(self.footer,'Save equipment',lambda:self.run(self.save)).pack(side='bottom',fill='x',pady=10)
    def save(self):
        try: total=int(self.total.get())
        except ValueError: raise ValidationError('Enter a whole number of units.')
        self.app.equipment.save(self.name.get(),self.category.get(),total,self.premium.get(),self.description.get(),self.item.get('id'))
        self.close_success('Equipment saved.')

class UserDialog(Dialog):
    def __init__(self,app,user=None):
        super().__init__(app,'Edit student' if user else 'Add student',490,660)
        self.user=user; user=user or {}; self.vars={}
        fields=[('name','Full name'),('email','Email'),('department','Department'),('phone','Phone')]
        if not user: fields=[('code','Student number')]+fields+[('password','Initial password (8+ characters)')]
        for key,title in fields:
            self.vars[key]=tk.StringVar(value=user.get(key,''))
            field(self.body,title,self.vars[key],show='•' if key=='password' else '')
        button(self.footer,'Save student',lambda:self.run(self.save)).pack(side='bottom',fill='x',pady=12)
    def save(self):
        data={k:v.get() for k,v in self.vars.items()}
        if self.user: self.app.trust.update_profile(self.user['id'],**data)
        else: self.app.auth.create_student(**data)
        self.close_success('Student saved.')

class ProfileDialog(Dialog):
    def __init__(self,app,user_id):
        super().__init__(app,'Student profile',840,700)
        u=app.trust.profile(user_id); limits=u['limits']
        top=frame(self.body); top.pack(fill='x',pady=(12,5))
        gauge(top,u['score'],140).pack(side='left',padx=(0,25))
        details=frame(top); details.pack(side='left',fill='both',expand=True)
        label(details,u['name'],21,bold=True).pack(anchor='w',pady=(8,5))
        label(details,f"{u['code']} · {u['department']}",11,color=C['muted']).pack(anchor='w')
        label(details,u['email'],11,color=C['muted']).pack(anchor='w',pady=6)
        pill(details,limits['label'],limits['color']).pack(anchor='w',pady=6)
        label(details,f"{u['open_loans']} open loans · {limits['loans']} maximum · {limits['days']} days",10,color=C['muted']).pack(anchor='w')
        if limits['blocked']: label(details,'Blocked until '+(u['blocked_until'] or 'administrator review'),10,color=C['red']).pack(anchor='w',pady=5)
        divider(self.body)
        label(self.body,'Loan history',12,bold=True).pack(anchor='w',pady=(0,8))
        history=app.loans.list_loans(user_id=user_id)
        table=Table(self.body,[('id','LOAN',60),('equipment','EQUIPMENT',245),('status','STATUS',100),('due','DUE',100),('score','SCORE',100)],height=5)
        table.pack(fill='both',expand=True)
        table.set_rows([(l['id'],(f"L{l['id']:04}",l['equipment_name'],l['status'].title(),l['due_date'] or 'Pending',f"{l['score_before']} → {l['score_after']}" if l['score_after'] is not None else '—'),'red' if l['late_days'] else 'muted') for l in history])
        import json
        audits=json.loads(u['audit_log'])
        if audits:
            a=audits[-1]; label(self.body,f"Latest review: {a['date']} · {a['action']} · {a['reason']}",10,color=C['muted'],wraplength=750,justify='left').pack(anchor='w',pady=10)
        row=frame(self.footer); row.pack(fill='x',pady=(15,0))
        if app.auth.current_user['role']=='admin':
            def decision(action):
                self.destroy(); ReasonDialog(app,action.title()+' student',lambda reason,value:app.trust.administer(user_id,action,reason,value),action=='privilege')
            button(row,'Unblock' if limits['blocked'] else 'Block',lambda:decision('unblock' if limits['blocked'] else 'block'),'secondary').pack(side='left',padx=(0,8))
            button(row,'Privileges',lambda:decision('privilege'),'secondary').pack(side='left',padx=(0,8))
            button(row,'Edit profile',lambda:(self.destroy(),UserDialog(app,u)),'secondary').pack(side='left')
        button(row,'Close',self.destroy).pack(side='right')
