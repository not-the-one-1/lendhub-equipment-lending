from ui.pages.users_page import UsersPage
class RiskyUsersPage(UsersPage):
    def __init__(self,parent,app):
        super().__init__(parent,app,risky=True)
