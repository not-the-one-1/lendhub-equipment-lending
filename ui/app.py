import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from theme import apply_theme, COLORS, FONTS


class EquipmentRepository:

    def __init__(self):
        self._items = [
            {"id": "E001", "name": "Laptop Dell XPS 13", "category": "Laptop", "available": 5, "total": 5},
            {"id": "E002", "name": "Scientific Calculator", "category": "Calculator", "available": 10, "total": 10},
            {"id": "E003", "name": "Projector Epson", "category": "Projector", "available": 0, "total": 2},
            {"id": "E004", "name": "Camera Canon", "category": "Camera", "available": 3, "total": 3},
            {"id": "E005", "name": "Tablet iPad", "category": "Tablet", "available": 4, "total": 4},
            {"id": "E006", "name": "HDMI Cable", "category": "Accessory", "available": 8, "total": 8},
        ]

    def get_all(self):
        return [item.copy() for item in self._items]

    def get_categories(self):
        return sorted({item["category"] for item in self._items})

    def borrow_one(self, equipment_id):
        for item in self._items:
            if item["id"] == equipment_id and item["available"] > 0:
                item["available"] -= 1
                return True
        return False

    def get_stats(self):
        total = sum(item["total"] for item in self._items)
        available = sum(item["available"] for item in self._items)
        return {
            "total": total,
            "available": available,
            "lent": total - available,
            # These need real loan/student records to calculate accurately.
            "overdue": 0,
            "at_risk": 0,
        }


def label(parent, text, font=None, color=None, **kwargs):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font or FONTS["body"],
        text_color=color or COLORS["text"],
        **kwargs,
    )


def configure_table_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "CampusLend.Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=38,
        borderwidth=0,
        font=FONTS["body"],
    )
    style.configure(
        "CampusLend.Treeview.Heading",
        background=COLORS["sidebar_bg"],
        foreground=COLORS["text_muted"],
        relief="flat",
        font=FONTS["label"],
        padding=(10, 9),
    )
    style.map(
        "CampusLend.Treeview",
        background=[("selected", COLORS["secondary"])],
        foreground=[("selected", COLORS["white"])],
    )


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(
            master, width=200, corner_radius=0,
            fg_color=COLORS["sidebar_bg"]
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        label(self, "CampusLend", ("Segoe UI", 21, "bold")).pack(
            anchor="w", padx=20, pady=(24, 5)
        )
        label(
            self, "SCHOOL EQUIPMENT LENDING",
            ("Segoe UI", 9, "bold"), COLORS["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 24))

        self.nav_buttons = {}
        items = [
            ("Home", "⌂"), ("Borrow Equipment", "⇄"),
            ("Return Equipment", "↩"), ("Equipment", "▦"),
            ("Students", "♙"), ("Risky Users", "⚠"),
            ("Reports", "▥"), ("Settings", "⚙"),
        ]
        for page, icon in items:
            button = ctk.CTkButton(
                self,
                text=f"{icon}   {page}",
                anchor="w",
                height=39,
                corner_radius=8,
                font=FONTS["small"],
                fg_color="transparent",
                hover_color=COLORS["secondary"],
                text_color=COLORS["text"],
                command=lambda name=page: self.on_navigate(name),
            )
            button.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[page] = button

        self.set_active("Home")
        label(
            self, "BORROW  •  USE  •  RESPECT",
            ("Segoe UI", 9), COLORS["text_muted"]
        ).pack(side="bottom", anchor="w", padx=18, pady=20)

        

    def set_active(self, active_page):
        for page, button in self.nav_buttons.items():
            active = page == active_page
            button.configure(
                fg_color=COLORS["primary"] if active else "transparent",
                text_color=COLORS["text_on_primary"] if active else COLORS["text"],
            )


class StatsCards(ctk.CTkFrame):
    DEFINITIONS = [
        ("total", "Total Equipment"),
        ("available", "Available"),
        ("lent", "Currently Lent"),
        ("overdue", "Overdue"),
        ("at_risk", "At Risk Users"),
    ]

    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.value_labels = {}

        for col in range(len(self.DEFINITIONS)):
            self.grid_columnconfigure(col, weight=1, uniform="stat_cards")

        for col, (key, title) in enumerate(self.DEFINITIONS):
            card = ctk.CTkFrame(
                self, fg_color=COLORS["primary"],
                corner_radius=12, height=96
            )
            card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), sticky="nsew")
            card.grid_propagate(False)

            label(
                card, title, ("Segoe UI", 12, "bold"),
                COLORS["text_on_primary"]
            ).pack(anchor="w", padx=14, pady=(14, 3))

            value = label(
                card, "—", ("Segoe UI", 25, "bold"),
                COLORS["text_on_primary"]
            )
            value.pack(anchor="w", padx=14)
            self.value_labels[key] = value

    def update_stats(self, stats):
        for key, value_label in self.value_labels.items():
            value_label.configure(text=str(stats.get(key, 0)))


class EquipmentTable(ctk.CTkFrame):
    def __init__(self, master, repository, on_borrow):
        super().__init__(
            master, fg_color=COLORS["surface"],
            corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        self.repository = repository
        self.on_borrow = on_borrow
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All categories")
        self.availability_var = tk.StringVar(value="Available only")

        label(self, "Available Equipment", FONTS["subheading"]).pack(
            anchor="w", padx=16, pady=(14, 10)
        )
        self._build_toolbar()
        self._build_tree()

        self.search_var.trace_add("write", self.refresh)
        self.category_var.trace_add("write", self.refresh)
        self.availability_var.trace_add("write", self.refresh)
        self.refresh()

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkEntry(
            toolbar, textvariable=self.search_var,
            placeholder_text="Search by ID, name, or category...",
            height=36
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        categories = ["All categories"] + self.repository.get_categories()
        ctk.CTkOptionMenu(
            toolbar, variable=self.category_var, values=categories,
            width=160, height=36,
            fg_color=COLORS["secondary"],
            button_color=COLORS["secondary"],
            button_hover_color=COLORS["secondary_hover"],
        ).pack(side="left", padx=(0, 10))

        ctk.CTkOptionMenu(
            toolbar, variable=self.availability_var,
            values=["Available only", "All equipment", "Unavailable"],
            width=150, height=36,
            fg_color=COLORS["secondary"],
            button_color=COLORS["secondary"],
            button_hover_color=COLORS["secondary_hover"],
        ).pack(side="left")

    def _build_tree(self):
        configure_table_style()
        area = ctk.CTkFrame(self, fg_color="transparent")
        area.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("id", "name", "category", "status", "available", "action")
        self.tree = ttk.Treeview(
            area, columns=columns, show="headings",
            style="CampusLend.Treeview", selectmode="browse"
        )
        config = {
            "id": ("ID", 80, "center"),
            "name": ("Name", 240, "w"),
            "category": ("Category", 140, "w"),
            "status": ("Status", 110, "center"),
            "available": ("Available", 95, "center"),
            "action": ("Action", 130, "center"),
        }
        for column, (heading, width, anchor) in config.items():
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, minwidth=65, anchor=anchor, stretch=True)

        scrollbar = ttk.Scrollbar(area, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.tag_configure("available", foreground=COLORS["success"])
        self.tree.tag_configure("unavailable", foreground=COLORS["danger"])
        self.tree.bind("<Double-1>", self._on_double_click)

    def refresh(self, *_):
        query = self.search_var.get().strip().casefold()
        category = self.category_var.get()
        availability_filter = self.availability_var.get()
        self.tree.delete(*self.tree.get_children())

        for item in self.repository.get_all():
            is_available = item["available"] > 0
            searchable = f'{item["id"]} {item["name"]} {item["category"]}'.casefold()

            if query and query not in searchable:
                continue
            if category != "All categories" and item["category"] != category:
                continue
            if availability_filter == "Available only" and not is_available:
                continue
            if availability_filter == "Unavailable" and is_available:
                continue

            self.tree.insert(
                "", "end", iid=item["id"],
                values=(
                    item["id"], item["name"], item["category"],
                    "Available" if is_available else "Unavailable",
                    item["available"],
                    "Double-click to borrow" if is_available else "Unavailable",
                ),
                tags=("available" if is_available else "unavailable",),
            )

    def _on_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if row_id and column_id == "#6":
            self.on_borrow(row_id)


class EquipmentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CampusLend - School Equipment Lending")
        self.geometry("1400x800")
        self.minsize(1050, 650)
        self.configure(fg_color=COLORS["app_bg"])

        self.repository = EquipmentRepository()

        # Keep the sidebar separate from the page content.
        self.sidebar = Sidebar(self, self.navigate)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(
            self, fg_color=COLORS["app_bg"], corner_radius=0
        )
        self.content.pack(side="left", fill="both", expand=True)

        # Both widgets are children of the same content frame and stack vertically.
        self.stats_cards = StatsCards(self.content)
        self.stats_cards.pack(fill="x", padx=20, pady=(20, 14))

        self.equipment_table = EquipmentTable(
            self.content, self.repository, self.borrow_equipment
        )
        self.equipment_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_dashboard()

    def refresh_dashboard(self):
        self.stats_cards.update_stats(self.repository.get_stats())

    def borrow_equipment(self, equipment_id):
        item = next(
            (row for row in self.repository.get_all() if row["id"] == equipment_id),
            None,
        )
        if not item:
            return
        if item["available"] <= 0:
            messagebox.showwarning("Unavailable", "No units are available.")
            return

        if messagebox.askyesno(
            "Borrow equipment",
            f"Borrow one unit of {item['name']} ({item['id']})?\n\n"
            "This demo updates sample data only.",
        ):
            if self.repository.borrow_one(equipment_id):
                self.equipment_table.refresh()
                self.refresh_dashboard()

    def navigate(self, page):
        self.sidebar.set_active(page)
        if page != "Home":
            messagebox.showinfo(
                page,
                f"The {page} page can be implemented as a separate module."
            )


if __name__ == "__main__":
    apply_theme()
    app = EquipmentApp()
    app.mainloop()
