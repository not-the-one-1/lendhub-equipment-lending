import tkinter as tk
from tkinter import ttk
from ui.theme import C,FONT

def frame(parent,bg=None,**kw): return tk.Frame(parent,bg=bg or parent.cget('bg'),**kw)
def label(parent,text='',size=11,color=None,bold=False,**kw):
    return tk.Label(parent,text=text,font=(FONT,size,'bold' if bold else 'normal'),fg=color or C['text'],bg=parent.cget('bg'),**kw)
def button(parent,text,command,kind='primary',**kw):
    bg={'primary':C['blue'],'secondary':C['raised'],'danger':C['red_bg'],'success':C['green_bg']}.get(kind,C['raised'])
    fg={'danger':C['red'],'success':C['green']}.get(kind,C['white'] if kind=='primary' else C['text'])
    b=tk.Button(parent,text=text,command=command,bg=bg,fg=fg,activebackground=C['blue_hover'] if kind=='primary' else C['border'],activeforeground=fg,relief='flat',bd=0,padx=kw.pop('padx',15),pady=kw.pop('pady',10),cursor='hand2',font=(FONT,10,'bold'),disabledforeground=C['muted'],**kw)
    return b
def entry(parent,variable=None,show='',width=24):
    return tk.Entry(parent,textvariable=variable,show=show,width=width,bg=C['input'],fg=C['text'],insertbackground=C['text'],relief='flat',highlightthickness=1,highlightbackground=C['border'],highlightcolor=C['blue'],font=(FONT,11))
def combo(parent,variable,values,width=22):
    return ttk.Combobox(parent,textvariable=variable,values=values,state='readonly',width=width,font=(FONT,10))
def field(parent,title,variable=None,show=''):
    label(parent,title,10,color=C['muted']).pack(anchor='w',pady=(12,5))
    e=entry(parent,variable,show); e.pack(fill='x',ipady=10)
    return e
def divider(parent): frame(parent,C['border'],height=1).pack(fill='x',pady=12)
def pill(parent,text,tone='green'):
    return tk.Label(parent,text=text,padx=10,pady=5,bg=C.get(tone+'_bg',C['raised']),fg=C[tone],font=(FONT,9,'bold'))

class Card(tk.Frame):
    def __init__(self,parent,title=None,**kw):
        super().__init__(parent,bg=C['panel'],highlightthickness=1,highlightbackground=C['border'],**kw)
        if title: label(self,title,12,bold=True).pack(anchor='w',padx=16,pady=(14,10))

class ScrollFrame(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent,bg=C['bg'])
        self.canvas=tk.Canvas(self,bg=C['bg'],highlightthickness=0)
        self.bar=ttk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side='right',fill='y'); self.canvas.pack(side='left',fill='both',expand=True)
        self.body=frame(self.canvas,C['bg'])
        self.window=self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(self.window,width=e.width))
        self.bind('<Destroy>',self.cleanup)
        self.binding=self.bind_all('<MouseWheel>',self.wheel,add='+')
    def wheel(self,event):
        if not self.winfo_exists(): return
        w=event.widget
        # Only scroll the page whose widget received the wheel event.
        if str(w).startswith(str(self)) and self.body.winfo_height()>self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-event.delta/120),'units')
    def cleanup(self,event):
        if event.widget is self:
            self._root()._unbind(('bind','all','<MouseWheel>'),self.binding)

class Table(tk.Frame):
    def __init__(self,parent,columns,height=8,on_select=None):
        super().__init__(parent,bg=C['panel'])
        self.tree=ttk.Treeview(self,columns=[c[0] for c in columns],show='headings',height=height,selectmode='browse')
        for key,title,width in columns:
            self.tree.heading(key,text=title); self.tree.column(key,width=width,minwidth=min(width,80),anchor='w',stretch=True)
        bar=ttk.Scrollbar(self,orient='vertical',command=self.tree.yview)
        horizontal=ttk.Scrollbar(self,orient='horizontal',command=self.tree.xview)
        self.tree.configure(yscrollcommand=bar.set,xscrollcommand=horizontal.set)
        self.tree.grid(row=0,column=0,sticky='nsew'); bar.grid(row=0,column=1,sticky='ns'); horizontal.grid(row=1,column=0,sticky='ew')
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(0,weight=1)
        self.empty=label(self,'No records to show.',11,color=C['muted'])
        for tone in ('green','red','yellow','muted'): self.tree.tag_configure(tone,foreground=C[tone])
        if on_select: self.tree.bind('<<TreeviewSelect>>',lambda e:on_select(self.selected()))
    def set_rows(self,rows):
        self.tree.delete(*self.tree.get_children())
        for ident,values,tone in rows: self.tree.insert('','end',iid=str(ident),values=values,tags=(tone,))
        if rows: self.empty.place_forget()
        else: self.empty.place(relx=.5,rely=.5,anchor='center')
    def selected(self):
        selected=self.tree.selection()
        return int(selected[0]) if selected else None

class Dialog(tk.Toplevel):
    def __init__(self,app,title,width=480,height=550):
        super().__init__(app)
        height=min(height,self.winfo_screenheight()-100)
        self.app=app; self.title(title); self.configure(bg=C['panel'])
        self.resizable(False,False); self.transient(app)
        self.geometry(f'{width}x{height}+{max(0,app.winfo_rootx()+(app.winfo_width()-width)//2)}+{max(0,app.winfo_rooty()+(app.winfo_height()-height)//2)}')
        self.body=frame(self,C['panel']); self.body.pack(fill='both',expand=True,padx=24,pady=20)
        label(self.body,title,19,bold=True).pack(anchor='w',pady=(0,7))
        self.error=tk.StringVar()
        self.error_label=label(self.body,'',10,color=C['red'],textvariable=self.error,wraplength=width-55,justify='left')
        self.error_label.pack(side='bottom',anchor='w',pady=(8,0))
        self.footer=frame(self.body)
        self.footer.pack(side='bottom',fill='x')
        self.bind('<Escape>',lambda e:self.destroy())
        self.grab_set()
        self.after_idle(self.focus_set)
    def run(self,fn):
        from services.errors import ValidationError
        try: return fn()
        except (ValidationError,ValueError,OSError) as exc: self.error.set(str(exc))
    def close_success(self,text):
        self.destroy(); self.app.navigate(self.app.current_page); self.app.toast(text)

class Toast(tk.Frame):
    def __init__(self,app,text,tone='green'):
        super().__init__(app,bg=C.get(tone+'_bg',C['raised']),highlightthickness=1,highlightbackground=C[tone])
        tk.Label(self,text=text,font=(FONT,11),fg=C[tone],bg=self.cget('bg'),padx=20,pady=15,wraplength=600).pack()
        self.place(relx=.985,rely=.975,anchor='se'); self.lift()
        self.after(5500,self.destroy)

def equipment_icon(parent,category,size=54):
    c=tk.Canvas(parent,width=size,height=size,bg=parent.cget('bg'),highlightthickness=0)
    color=C['blue']; center=size//2
    if category in ('Laptop','Tablet'):
        c.create_rectangle(10,9,size-10,size-17,outline=color,width=2)
        c.create_line(6,size-12,size-6,size-12,fill=color,width=3)
    elif category=='Camera':
        c.create_rectangle(6,17,size-6,size-12,outline=color,width=2)
        c.create_oval(center-9,20,center+9,38,outline=color,width=2)
        c.create_rectangle(13,11,27,17,fill=color,outline=color)
    elif category=='Audio':
        c.create_arc(9,9,size-9,size-6,start=0,extent=180,style='arc',outline=color,width=3)
        c.create_rectangle(8,26,15,42,fill=color,outline=color); c.create_rectangle(size-15,26,size-8,42,fill=color,outline=color)
    else:
        c.create_polygon(center,7,size-8,18,size-8,38,center,size-5,8,38,8,18,outline=color,fill='',width=2)
        c.create_line(8,18,center,28,size-8,18,fill=color,width=2); c.create_line(center,28,center,size-5,fill=color,width=2)
    return c

def bar_chart(parent,items,color='blue',height=185):
    c=tk.Canvas(parent,bg=C['panel'],highlightthickness=0,height=height)
    def draw(event=None):
        c.delete('all'); width=max(c.winfo_width(),250); top=12; count=max(1,len(items)); step=(height-22)/count
        maximum=max((float(v) for _,v in items),default=1) or 1
        for i,(name,value) in enumerate(items):
            y=top+i*step
            c.create_text(14,y,anchor='nw',text=str(name)[:28],fill=C['muted'],font=(FONT,9))
            c.create_rectangle(14,y+20,width-50,y+26,fill=C['raised'],outline='')
            c.create_rectangle(14,y+20,14+(width-64)*float(value)/maximum,y+26,fill=C[color],outline='')
            c.create_text(width-14,y+12,anchor='e',text=str(value),fill=C['text'],font=(FONT,10,'bold'))
    c.bind('<Configure>',draw)
    return c

def gauge(parent,score,size=175):
    c=tk.Canvas(parent,width=size,height=size,bg=parent.cget('bg'),highlightthickness=0)
    tone='green' if score>=80 else 'yellow' if score>=60 else 'orange' if score>=40 else 'red'
    c.create_arc(15,15,size-15,size-15,start=90,extent=-359.9,outline=C['raised'],style='arc',width=10)
    c.create_arc(15,15,size-15,size-15,start=90,extent=-max(1,score)*3.599,outline=C[tone],style='arc',width=10)
    c.create_text(size/2,size/2-6,text=str(score),fill=C['text'],font=(FONT,34,'bold'))
    c.create_text(size/2,size/2+26,text='TRUST SCORE',fill=C['muted'],font=(FONT,9,'bold'))
    return c
