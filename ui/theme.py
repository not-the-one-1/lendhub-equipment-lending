"""
theme.py — Global styling for the Equipment Management System.

Usage:
    import customtkinter as ctk
    from theme import apply_theme, COLORS, FONTS

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    apply_theme()

    # Example:
    root = ctk.CTk()
    root.configure(fg_color=COLORS["app_bg"])
    ...

Palette:
    Periwinkle: #7899D4
    Midnight:   #0C1821
    Navy:       #1B2A41
    Slate blue: #324A5F
    Lavender:   #CCC9DC
"""

import customtkinter as ctk


# ---------------------------------------------------------------------------
# Global palette
# ---------------------------------------------------------------------------

COLORS = {
    # Core backgrounds
    "app_bg": "#0C1821",          # Midnight: main window background
    "sidebar_bg": "#1B2A41",      # Navy: navigation sidebar
    "surface": "#142330",         # Raised panels/cards
    "surface_alt": "#203449",     # Alternate panel / hover surface
    "input_bg": "#142330",

    # Brand / actions
    "primary": "#7899D4",         # Periwinkle blue
    "primary_hover": "#6687C5",
    "primary_pressed": "#5878B5",
    "secondary": "#324A5F",       # Slate blue
    "secondary_hover": "#3D5A73",

    # Text
    "text": "#F5F7FB",
    "text_muted": "#B5C0D0",
    "text_on_primary": "#FFFFFF",
    "text_dark": "#0C1821",

    # Borders / dividers
    "border": "#324A5F",
    "divider": "#293D50",

    # Status colors
    "success": "#56C596",
    "success_bg": "#173D36",
    "warning": "#F2C66D",
    "warning_bg": "#493B24",
    "danger": "#F07878",
    "danger_bg": "#49282D",
    "info": "#8CB7F0",
    "info_bg": "#203A55",

    # Special
    "lavender": "#CCC9DC",
    "white": "#FFFFFF",
    "black": "#000000",
}


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

# Segoe UI is a clean Windows UI font. Tk will fall back if unavailable.
# Keep font sizes centralized so the whole application stays consistent.
FONTS = {
    "family": "Segoe UI",
    "family_fallback": "Arial",
    "xs": ("Segoe UI", 10),
    "small": ("Segoe UI", 11),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "button": ("Segoe UI", 11, "bold"),
    "label": ("Segoe UI", 11, "bold"),
    "subheading": ("Segoe UI", 15, "bold"),
    "heading": ("Segoe UI", 22, "bold"),
    "display": ("Segoe UI", 30, "bold"),
    "mono": ("Cascadia Code", 11),
}


# ---------------------------------------------------------------------------
# Component defaults
# ---------------------------------------------------------------------------

SIZES = {
    "sidebar_width": 190,
    "button_height": 38,
    "input_height": 38,
    "card_radius": 12,
    "button_radius": 8,
    "panel_radius": 12,
    "page_padding": 24,
    "component_gap": 12,
}


def apply_theme():
    """Set application-wide CustomTkinter defaults."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # CTk widget defaults. Per-widget values can override these.
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = COLORS["primary"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = COLORS["primary_hover"]
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = COLORS["text_on_primary"]
    ctk.ThemeManager.theme["CTkButton"]["corner_radius"] = SIZES["button_radius"]
    ctk.ThemeManager.theme["CTkButton"]["border_width"] = 0

    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = COLORS["surface"]
    ctk.ThemeManager.theme["CTkFrame"]["corner_radius"] = SIZES["panel_radius"]

    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkLabel"]["font"] = FONTS["body"]

    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = COLORS["input_bg"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkEntry"]["border_color"] = COLORS["border"]
    ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"] = COLORS["text_muted"]

    ctk.ThemeManager.theme["CTkTextbox"]["fg_color"] = COLORS["input_bg"]
    ctk.ThemeManager.theme["CTkTextbox"]["text_color"] = COLORS["text"]

    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color"] = COLORS["primary"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] = COLORS["primary_hover"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color"] = COLORS["primary_pressed"]

    ctk.ThemeManager.theme["CTkComboBox"]["fg_color"] = COLORS["input_bg"]
    ctk.ThemeManager.theme["CTkComboBox"]["border_color"] = COLORS["border"]
    ctk.ThemeManager.theme["CTkComboBox"]["text_color"] = COLORS["text"]

    ctk.ThemeManager.theme["CTkCheckBox"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkRadioButton"]["text_color"] = COLORS["text"]

    ctk.ThemeManager.theme["CTkSlider"]["progress_color"] = COLORS["primary"]
    ctk.ThemeManager.theme["CTkSlider"]["button_color"] = COLORS["primary"]
    ctk.ThemeManager.theme["CTkSlider"]["button_hover_color"] = COLORS["primary_hover"]


def style_button(button, variant="primary"):
    """Apply a named button style to an existing CTkButton."""
    variants = {
        "primary": {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_hover"],
            "text_color": COLORS["text_on_primary"],
        },
        "secondary": {
            "fg_color": COLORS["secondary"],
            "hover_color": COLORS["secondary_hover"],
            "text_color": COLORS["text"],
        },
        "ghost": {
            "fg_color": "transparent",
            "hover_color": COLORS["surface_alt"],
            "text_color": COLORS["text_muted"],
        },
        "danger": {
            "fg_color": COLORS["danger_bg"],
            "hover_color": "#63333A",
            "text_color": COLORS["danger"],
        },
        "success": {
            "fg_color": COLORS["success_bg"],
            "hover_color": "#205548",
            "text_color": COLORS["success"],
        },
    }
    button.configure(**variants[variant])
    return button


def style_entry(entry):
    """Apply consistent styling to a CTkEntry."""
    entry.configure(
        fg_color=COLORS["input_bg"],
        text_color=COLORS["text"],
        border_color=COLORS["border"],
        placeholder_text_color=COLORS["text_muted"],
        corner_radius=8,
        height=SIZES["input_height"],
        font=FONTS["body"],
    )
    return entry


def style_card(card, color=None):
    """Apply a standard dashboard-card style to an existing CTkFrame."""
    card.configure(
        fg_color=color or COLORS["surface"],
        corner_radius=SIZES["card_radius"],
        border_width=1,
        border_color=COLORS["border"],
    )
    return card


def style_page_title(title_label, subtitle_label=None):
    """Style a page heading and optional subtitle."""
    title_label.configure(
        font=FONTS["heading"],
        text_color=COLORS["text"],
    )
    if subtitle_label is not None:
        subtitle_label.configure(
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
        )


def configure_treeview_style():
    """
    Return ttk style setup for ttk.Treeview tables.
    Call this after creating a Tk root, since ttk styles need a Tk interpreter.
    """
    from tkinter import ttk

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Equipment.Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=36,
        borderwidth=0,
        font=FONTS["body"],
    )
    style.configure(
        "Equipment.Treeview.Heading",
        background=COLORS["sidebar_bg"],
        foreground=COLORS["text_muted"],
        relief="flat",
        font=FONTS["label"],
        padding=(10, 9),
    )
    style.map(
        "Equipment.Treeview",
        background=[("selected", COLORS["secondary"])],
        foreground=[("selected", COLORS["white"])],
    )
    return style
