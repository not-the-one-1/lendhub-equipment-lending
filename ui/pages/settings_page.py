import tkinter as tk
from ui.pages.base import Page
from ui.components.widgets import *
from services.errors import ValidationError

class SettingsPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        self.section('Make it yours','Personalize your workspace and keep your account secure.')
        appearance=Card(self.content,'Appearance'); appearance.pack(fill='x',pady=(0,18))
        row=frame(appearance); row.pack(fill='x',padx=20,pady=(0,20))
        label(row,'Choose a theme',11,color=C['muted']).pack(side='left')
        button(row,'Light',lambda:app.set_theme('light'),'secondary').pack(side='right',padx=(8,0))
        button(row,'Dark',lambda:app.set_theme('dark'),'secondary').pack(side='right')
        card=Card(self.content,'Change password'); card.pack(fill='x')
        inner=frame(card); inner.pack(fill='x',padx=20,pady=(0,20))
        self.old=tk.StringVar(); self.new=tk.StringVar(); self.confirm=tk.StringVar()
        field(inner,'Current password',self.old,'•'); field(inner,'New password (at least 8 characters)',self.new,'•'); field(inner,'Confirm new password',self.confirm,'•')
        button(inner,'Update password',lambda:app.perform(self.change,'Password updated.')).pack(anchor='w',pady=(18,0))
        info=Card(self.content,'About LendHub'); info.pack(fill='x',pady=18)
        label(info,'A local campus equipment lending app. Your data stays in the project’s data folder.',11,color=C['muted'],wraplength=900,justify='left').pack(anchor='w',padx=20,pady=(0,12))
        label(info,'Version 1.0  ·  Python / Tkinter / SQLite',10,color=C['muted']).pack(anchor='w',padx=20,pady=(0,18))
    def change(self):
        if self.new.get()!=self.confirm.get(): raise ValidationError('The new passwords do not match.')
        self.app.auth.change_password(self.old.get(),self.new.get())
