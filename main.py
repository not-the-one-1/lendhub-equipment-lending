"""Launch LendHub: python main.py (no external packages required)."""
import argparse
import logging
from pathlib import Path
from config.settings import DB_PATH
from database.connection import Database
from database.seed import seed_database

def main():
    parser=argparse.ArgumentParser(description='LendHub campus equipment lending')
    parser.add_argument('--db',type=Path,default=DB_PATH,help='Use a separate local SQLite database')
    args=parser.parse_args()
    db=Database(args.db)
    logging.basicConfig(filename=args.db.parent/'lendhub.log',level=logging.ERROR,format='%(asctime)s %(levelname)s %(message)s',encoding='utf-8')
    seed_database(db)
    from ui.app import App
    App(db).mainloop()

if __name__=='__main__': main()
