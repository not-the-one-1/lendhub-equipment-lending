import tkinter as tk
from ui.pages.base import Page
from ui.components.widgets import *
from ui.components.dialogs import BorrowDialog,EquipmentDialog,ConfirmDialog
from services.trust_service import restrictions

class CataloguePage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app); self.manage=app.current_page=='Equipment'
        self.section('Equipment inventory' if self.manage else 'Find your next tool','Browse campus equipment for your next class, project, or big idea.')
        toolbar=frame(self.content); toolbar.pack(fill='x',pady=(0,16))
        self.query=tk.StringVar(); self.category=tk.StringVar(value='All categories'); self.available=tk.BooleanVar()
        e=entry(toolbar,self.query); e.pack(side='left',fill='x',expand=True,ipady=9,padx=(0,10))
        categories=['All categories']+sorted({e['category'] for e in app.equipment.list_equipment()})
        combo(toolbar,self.category,categories,18).pack(side='left',padx=(0,10))
        tk.Checkbutton(toolbar,text='Available only',variable=self.available,command=self.refresh,bg=C['bg'],fg=C['muted'],selectcolor=C['input'],activebackground=C['bg'],font=(FONT,10)).pack(side='left')
        if self.manage:
            actions=frame(self.content); actions.pack(fill='x',pady=(0,16))
            button(actions,'+ Add equipment',lambda:EquipmentDialog(app)).pack(side='left',padx=(0,8))
            button(actions,'Import CSV',app.import_equipment,'secondary').pack(side='left',padx=(0,8))
            button(actions,'Export CSV',lambda:app.export_file('equipment'),'secondary').pack(side='left')
        self.count=label(self.content,'',10,color=C['muted']); self.count.pack(anchor='w',pady=(0,12))
        self.grid_area=frame(self.content); self.grid_area.pack(fill='both',expand=True)
        self.cols=3
        if self.manage:
            self.table=Table(self.grid_area,[('code','ID',60),('name','EQUIPMENT',235),('category','CATEGORY',110),('stock','AVAILABLE',80),('total','TOTAL',60),('repair','REPAIR',70),('lost','LOST',60),('tier','ACCESS',100)],height=13)
            self.table.pack(fill='both',expand=True)
            actions=frame(self.content); actions.pack(fill='x',pady=15)
            button(actions,'Edit selected',lambda:self.selected_action('edit'),'secondary').pack(side='left',padx=(0,8))
            button(actions,'Repair one unit',lambda:self.selected_action('repair'),'secondary').pack(side='left',padx=(0,8))
            button(actions,'Export QR label',lambda:self.selected_action('qr'),'secondary').pack(side='left')
        else: self.grid_area.bind('<Configure>',self.resize)
        self.query.trace_add('write',self.refresh); self.category.trace_add('write',self.refresh); self.refresh()
    def resize(self,event):
        columns=max(1,min(4,event.width//295))
        if columns!=self.cols: self.cols=columns; self.refresh()
    def refresh(self,*args):
        items=self.app.equipment.list_equipment(self.query.get(),self.category.get(),self.available.get())
        self.count.configure(text=f'{len(items)} equipment types  ·  Search by name, category or code')
        if self.manage:
            self.table.set_rows([(e['id'],(e['code'],e['name'],e['category'],e['available'],e['total'],e['maintenance'],e['lost'],'Premium' if e['premium'] else 'Standard'),'green' if e['available'] else 'red') for e in items]); return
        for child in self.grid_area.winfo_children(): child.destroy()
        for col in range(4): self.grid_area.columnconfigure(col,weight=1 if col<self.cols else 0,uniform='catalogue' if col<self.cols else '')
        user=self.app.auth.current_user; limits=restrictions(user) if user['role']=='student' else None
        if not items: label(self.grid_area,'No equipment matches your search. Try another category.',12,color=C['muted']).pack(pady=50); return
        for i,item in enumerate(items):
            card=Card(self.grid_area,height=258); card.grid(row=i//self.cols,column=i%self.cols,sticky='nsew',padx=(0,12),pady=(0,14)); card.pack_propagate(False)
            top=frame(card); top.pack(fill='x',padx=16,pady=(12,4))
            equipment_icon(top,item['category']).pack(side='left')
            pill(top,'Premium' if item['premium'] else 'Standard','yellow' if item['premium'] else 'blue').pack(side='right')
            label(card,item['code']+'  /  '+item['category'].upper(),9,color=C['muted'],bold=True).pack(anchor='w',padx=18)
            label(card,item['name'],13,bold=True,wraplength=260,justify='left').pack(anchor='w',padx=18,pady=(6,5))
            label(card,f"{item['available']} of {item['total']} units available",10,color=C['green'] if item['available'] else C['red']).pack(anchor='w',padx=18)
            locked=bool(limits and (limits['blocked'] or (item['premium'] and not limits['premium'])))
            b=button(card,'Trust restriction' if locked else 'Request equipment' if item['available'] else 'Unavailable',lambda ident=item['id']:BorrowDialog(self.app,ident),'secondary' if locked else 'primary')
            b.pack(side='bottom',fill='x',padx=18,pady=16)
            if locked or not item['available']: b.configure(state='disabled')
    def selected_action(self,action):
        ident=self.table.selected()
        if not ident: return self.app.toast('Select an equipment row first.','yellow')
        item=next(e for e in self.app.equipment.list_equipment() if e['id']==ident)
        if action=='edit': EquipmentDialog(self.app,item)
        elif action=='qr': self.app.export_file('qr',ident)
        else: ConfirmDialog(self.app,'Complete repair','Confirm that one unit has been repaired and is ready to lend.',lambda:self.app.perform(lambda:self.app.equipment.repair_one(ident),'One unit returned to available stock.'))
