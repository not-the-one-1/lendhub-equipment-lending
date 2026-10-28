"""Exercise every role and page with an isolated demo database.

Run: python tests/ui_smoke.py
Optional --stay admin|tech|student --page Dashboard leaves the demo visible.
"""
import argparse
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from database.connection import Database
from database.seed import seed_database
from ui.app import App
from ui.components.dialogs import BorrowDialog,ReturnDialog,ProfileDialog,EquipmentDialog,UserDialog,ReasonDialog

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--stay',choices=['admin','tech','student']); parser.add_argument('--page'); args=parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        db=Database(Path(directory)/'demo.db'); seed_database(db)
        app=App(db,Path(directory)/'preferences.json'); failures=[]; count=0
        app.report_callback_exception=lambda typ,value,tb:failures.append(str(value))
        app.update()
        for theme in ('dark','light'):
            app.theme=theme
            from ui.theme import apply_theme
            apply_theme(app,theme)
            for role in ('student','tech','admin'):
                app.auth.login(role+'@lendhub.local','LendHub123!'); app.show_shell()
                for page in app.allowed_pages():
                    app.navigate(page); app.update(); count+=1
                app.toggle_sidebar(); app.update(); app.toggle_sidebar(); app.update()
                if role=='admin':
                    for make in (lambda:BorrowDialog(app,2,3),lambda:ReturnDialog(app,41),lambda:ProfileDialog(app,3),lambda:EquipmentDialog(app),lambda:UserDialog(app),lambda:ReasonDialog(app,'Review',lambda reason,value:None,True)):
                        dialog=make(); app.update(); dialog.event_generate('<Escape>'); app.update()
                        assert not dialog.winfo_exists(), 'Escape must close dialogs'
                        count+=1
                app.show_login(); app.update()
        if failures: raise AssertionError(failures)
        print(f'PASS: {count} page/dialog renders across all roles and both themes.',flush=True)
        if args.stay:
            apply_theme(app,'dark'); app.theme='dark'; app.auth.login(args.stay+'@lendhub.local','LendHub123!'); app.show_shell(args.page); app.mainloop()
        else: app.destroy()

if __name__=='__main__': main()
