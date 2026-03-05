"""
✨ Eternal Media Downloader | Developed by Hearlov — Theme & Styling
Dark theme with modern aesthetics
"""

COLORS = {
    #Base
    "bg_primary":       "#0D0F14",
    "bg_secondary":     "#141720",
    "bg_tertiary":      "#1A1E2A",
    "bg_card":          "#1E2235",
    "bg_hover":         "#252A3A",
    "bg_active":        "#2A3045",
    #Accent
    "accent":           "#7C5CFC",
    "accent_hover":     "#9478FF",
    "accent_light":     "#7C5CFC22",
    "accent_glow":      "#7C5CFC44",
    #Text
    "text_primary":     "#E8EAF0",
    "text_secondary":   "#8B90A0",
    "text_muted":       "#555B6E",
    #Status
    "success":          "#34D399",
    "warning":          "#FBBF24",
    "error":            "#F87171",
    "info":             "#60A5FA",
    #Border
    "border":           "#2A2E3E",
    "border_light":     "#353A4E",
    #Scrollbar
    "scrollbar_bg":     "#141720",
    "scrollbar_handle":  "#2A2E3E",
}

FONTS = {
    "primary":    "Segoe UI",
    "monospace":  "Cascadia Code, Consolas",
}

DIMS = {
    "border_radius":        12,
    "border_radius_sm":     8,
    "title_bar_height":     42,
    "sidebar_collapsed":    60,
    "sidebar_expanded":     220,
    "card_height":          90,
    "spacing":              16,
    "spacing_sm":           8,
}

GLOBAL_STYLE = f"""
QWidget {{
    font-family: '{FONTS["primary"]}';
    font-size: 13px;
    color: {COLORS["text_primary"]};
    background: transparent;
}}

QMainWindow {{
    background: {COLORS["bg_primary"]};
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: {COLORS["scrollbar_bg"]};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS["scrollbar_handle"]};
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS["border_light"]};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ── Tooltip ── */
QToolTip {{
    background: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}
"""
