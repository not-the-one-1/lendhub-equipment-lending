from tkinter import ttk
DARK={'bg':'#0B1520','sidebar':'#101F2D','panel':'#132330','raised':'#1B3042','input':'#0F1E2B','border':'#294052','text':'#EAF1FA','muted':'#9EB1C5','blue':'#2788FA','blue_hover':'#1A71D8','blue_bg':'#153C63','green':'#50DE99','green_bg':'#153E33','yellow':'#FFC85B','yellow_bg':'#493B20','orange':'#FFA35D','red':'#FF6979','red_bg':'#482731','white':'#FFFFFF'}
LIGHT={'bg':'#F0F4F8','sidebar':'#E3ECF5','panel':'#FFFFFF','raised':'#EDF3F9','input':'#F6F9FC','border':'#D1DDE8','text':'#172D43','muted':'#586D81','blue':'#126ED4','blue_hover':'#0C56B0','blue_bg':'#DCEBFF','green':'#127B4D','green_bg':'#DDF5E9','yellow':'#966200','yellow_bg':'#FFF0CC','orange':'#AE570C','red':'#C63247','red_bg':'#FDE4E8','white':'#FFFFFF'}
C=dict(DARK)
FONT='Segoe UI'
def apply_theme(root,mode='dark'):
    C.clear(); C.update(LIGHT if mode=='light' else DARK)
    root.configure(bg=C['bg'])
    s=ttk.Style(root); s.theme_use('clam')
    s.configure('Treeview',background=C['panel'],fieldbackground=C['panel'],foreground=C['text'],rowheight=40,borderwidth=0,bordercolor=C['border'],lightcolor=C['border'],darkcolor=C['border'],font=(FONT,10))
    s.configure('Treeview.Heading',background=C['raised'],foreground=C['muted'],relief='flat',padding=(8,10),font=(FONT,9,'bold'))
    s.map('Treeview',background=[('selected',C['blue_bg'])],foreground=[('selected',C['text'])])
    s.configure('TCombobox',fieldbackground=C['input'],background=C['raised'],foreground=C['text'],arrowcolor=C['muted'],bordercolor=C['border'],padding=7)
    s.map('TCombobox',fieldbackground=[('readonly',C['input'])],foreground=[('readonly',C['text'])],selectbackground=[('readonly',C['input'])],selectforeground=[('readonly',C['text'])])
    s.configure('Vertical.TScrollbar',background=C['raised'],troughcolor=C['panel'],bordercolor=C['panel'],arrowcolor=C['muted'])
    s.configure('Horizontal.TScrollbar',background=C['raised'],troughcolor=C['panel'],bordercolor=C['panel'],arrowcolor=C['muted'])
    root.option_add('*TCombobox*Listbox.background',C['input'])
    root.option_add('*TCombobox*Listbox.foreground',C['text'])
    root.option_add('*TCombobox*Listbox.selectBackground',C['blue'])
