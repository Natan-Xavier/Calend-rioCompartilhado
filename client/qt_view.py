import sys
import calendar
import uuid
import warnings
from datetime import datetime, date, timedelta

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDialog, QFormLayout, QDateEdit,
    QDateTimeEdit, QFrame, QStackedWidget, QScrollArea, QGridLayout,
    QSizePolicy, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QDate, QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from client.calendar_proxy import CalendarProxy

# ──────────────────────────────────────────────
# Google Calendar Palette
# ──────────────────────────────────────────────
BG          = "#ffffff"
BG_SIDE     = "#f6f8fc"
BG_CELL     = "#ffffff"
BG_EMPTY    = "#f8f9fa"
BG_HOVER    = "#f1f3f4"
BORDER      = "#dadce0"
TEXT        = "#3c4043"
TEXT_MUTED  = "#70757a"
TEXT_DIM    = "#bdc1c6"
ACCENT      = "#1a73e8"
ACCENT_DARK = "#1557b0"
RED         = "#d93025"
TODAY_BG    = "#1a73e8"
TODAY_TEXT  = "#ffffff"

EVENTO_BG    = "#d2e3fc"
EVENTO_TEXT  = "#1558b0"
TAREFA_BG    = "#ceead6"
TAREFA_TEXT  = "#137333"
LEMBRETE_BG  = "#feefc3"
LEMBRETE_TEXT = "#b05e02"

BASE_STYLE = f"""
    QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-family: "Segoe UI", sans-serif;
        font-size: 13px;
    }}
    QDialog {{ background-color: {BG}; }}
    QLineEdit, QDateEdit, QDateTimeEdit, QComboBox {{
        background-color: {BG};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        min-height: 24px;
        color: {TEXT};
    }}
    QLineEdit:focus, QDateEdit:focus, QDateTimeEdit:focus, QComboBox:focus {{
        border: 2px solid {ACCENT};
    }}
    QScrollBar:vertical {{
        background: {BG}; width: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QCheckBox {{ color: {TEXT}; spacing: 8px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 2px solid {TEXT_MUTED}; border-radius: 3px;
    }}
    QCheckBox::indicator:checked {{
        background-color: {ACCENT}; border-color: {ACCENT};
    }}
"""


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def format_date_display(dt_str):
    if not dt_str or dt_str == "Sem data":
        return "Sem data"
    try:
        if "T" in dt_str:
            return datetime.strptime(dt_str[:16], "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M")
        return datetime.strptime(dt_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return dt_str


def add_months(dt, months):
    month = dt.month - 1 + months
    year  = dt.year + month // 12
    month = month % 12 + 1
    day   = min(dt.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def generate_recurrence_dates(start_date, rule):
    dates = [start_date]
    if rule == "DIARIO":
        for i in range(1, 30):
            dates.append(start_date + timedelta(days=i))
    elif rule == "SEMANAL":
        for i in range(1, 52):
            dates.append(start_date + timedelta(weeks=i))
    elif rule == "MENSAL":
        for i in range(1, 12):
            dates.append(add_months(start_date, i))
    elif rule == "ANUAL":
        for i in range(1, 5):
            dates.append(add_months(start_date, i * 12))
    return dates


def type_colors(tipo):
    return {
        "EVENTO":   (EVENTO_BG,   EVENTO_TEXT),
        "TAREFA":   (TAREFA_BG,   TAREFA_TEXT),
        "LEMBRETE": (LEMBRETE_BG, LEMBRETE_TEXT),
    }.get(tipo, (BG_HOVER, TEXT))


def gcal_btn(text, primary=False, danger=False, small=False):
    b = QPushButton(text)
    pad = "6px 14px" if small else "9px 24px"
    if primary:
        s = f"""QPushButton {{ background-color: {ACCENT}; color: white; border: none;
                    border-radius: 4px; padding: {pad}; font-weight: 500; }}
                QPushButton:hover {{ background-color: {ACCENT_DARK}; }}"""
    elif danger:
        s = f"""QPushButton {{ background-color: transparent; color: {RED};
                    border: 1px solid {RED}; border-radius: 4px; padding: {pad}; font-weight: 500; }}
                QPushButton:hover {{ background-color: #fce8e6; }}"""
    else:
        s = f"""QPushButton {{ background-color: {BG}; color: {ACCENT};
                    border: 1px solid {BORDER}; border-radius: 4px; padding: {pad}; font-weight: 500; }}
                QPushButton:hover {{ background-color: {BG_HOVER}; border-color: {ACCENT}; }}"""
    b.setStyleSheet(s)
    return b


def gcal_nav_btn(text):
    b = QPushButton(text)
    b.setCheckable(True)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent; color: {TEXT};
            border: none; border-radius: 20px;
            padding: 10px 16px; text-align: left; font-size: 14px;
        }}
        QPushButton:hover {{ background-color: {BG_HOVER}; }}
        QPushButton:checked {{ background-color: #e8f0fe; color: {ACCENT}; font-weight: 600; }}
    """)
    return b


def h_sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
    return f


# ──────────────────────────────────────────────
# Toast
# ──────────────────────────────────────────────

class Toast(QLabel):
    def __init__(self, message, parent=None):
        super().__init__(message, parent)
        self.setStyleSheet(f"""
            QLabel {{ background-color: {TEXT}; color: white;
                      border-radius: 4px; padding: 10px 20px; font-weight: 500; }}
        """)
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()
        if parent:
            self.move((parent.width() - self.width()) // 2,
                      parent.height() - self.height() - 30)
        self.show(); self.raise_()
        QTimer.singleShot(2500, self.deleteLater)


# ──────────────────────────────────────────────
# ClickableFrame
# ──────────────────────────────────────────────

class ClickableFrame(QFrame):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ──────────────────────────────────────────────
# CalendarCell — fixed: no self.layout conflict
# ──────────────────────────────────────────────

class CalendarCell(ClickableFrame):
    cell_clicked = pyqtSignal(int, list)

    def __init__(self, day_num, is_today=False):
        super().__init__()
        self.day_num    = day_num
        self.items_list = []
        self.is_today   = is_today

        self.setCursor(Qt.PointingHandCursor if day_num > 0 else Qt.ArrowCursor)
        border = f"2px solid {ACCENT}" if is_today else f"1px solid {BORDER}"
        bg     = BG_CELL if day_num > 0 else BG_EMPTY
        self.setStyleSheet(f"""
            CalendarCell {{ background-color: {bg}; border: {border}; border-radius: 4px; }}
            CalendarCell:hover {{ background-color: {BG_HOVER if day_num > 0 else BG_EMPTY}; }}
        """)

        # _cell_layout avoids shadowing QWidget.layout()
        self._cell_layout = QVBoxLayout(self)
        self._cell_layout.setContentsMargins(4, 4, 4, 4)
        self._cell_layout.setSpacing(2)
        self._cell_layout.setAlignment(Qt.AlignTop)

        if day_num > 0:
            lbl = QLabel(str(day_num))
            if is_today:
                lbl.setStyleSheet(f"""
                    color: {TODAY_TEXT}; font-weight: 700; font-size: 12px;
                    background-color: {TODAY_BG}; border-radius: 12px;
                    padding: 2px 6px;
                """)
            else:
                lbl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
            self._cell_layout.addWidget(lbl, alignment=Qt.AlignLeft)

        self.clicked.connect(self._emit)

    def _emit(self):
        if self.day_num > 0:
            self.cell_clicked.emit(self.day_num, self.items_list)

    def add_badge(self, title, tipo):
        bg, fg = type_colors(tipo)
        short  = title[:13] + "…" if len(title) > 13 else title
        badge  = QLabel(f" {short}")
        badge.setStyleSheet(f"""
            background-color: {bg}; color: {fg};
            font-size: 10px; font-weight: 600; border-radius: 3px; padding: 1px 4px;
        """)
        badge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self._cell_layout.addWidget(badge)


# ──────────────────────────────────────────────
# RecurrenceWidget
# ──────────────────────────────────────────────

class RecurrenceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)

        self.check = QCheckBox("É recorrente?")
        self.combo = QComboBox()
        self.combo.addItems(["Diário (30 dias)", "Semanal (52 semanas)",
                             "Mensal (12 meses)", "Anual (5 anos)"])
        self.combo.hide()
        self.combo.setFixedWidth(200)

        self._layout.addWidget(self.check)
        self._layout.addWidget(self.combo)
        self._layout.addStretch()
        self.check.toggled.connect(self.combo.setVisible)

    def get_rule(self):
        if not self.check.isChecked():
            return None
        return ["DIARIO", "SEMANAL", "MENSAL", "ANUAL"][self.combo.currentIndex()]


# ──────────────────────────────────────────────
# QuickAddDialog — fast create from cell
# ──────────────────────────────────────────────

class QuickAddDialog(QDialog):
    def __init__(self, proxy, prefill_date=None, parent=None):
        super().__init__(parent)
        self.proxy = proxy
        self._pdate = prefill_date or date.today()
        self.setWindowTitle("Adicionar item")
        self.setFixedSize(380, 270)
        self.setStyleSheet(BASE_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(12)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["📆 Evento", "📋 Tarefa", "🔔 Lembrete"])
        row1.addWidget(self.type_combo)
        self._layout.addLayout(row1)

        self._layout.addWidget(QLabel("Título:"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nome do item")
        self.inp_title.returnPressed.connect(self._save)
        self._layout.addWidget(self.inp_title)

        self._layout.addWidget(QLabel("Data:"))
        self.inp_date = QDateEdit(QDate(self._pdate.year, self._pdate.month, self._pdate.day))
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setDisplayFormat("dd/MM/yyyy")
        self._layout.addWidget(self.inp_date)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

        self._layout.addStretch()
        btn_row = QHBoxLayout()
        cancel = gcal_btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        save = gcal_btn("Adicionar", primary=True, small=True)
        save.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        self._layout.addLayout(btn_row)

    def _save(self):
        title = self.inp_title.text().strip()
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        d_str  = self.inp_date.date().toString("yyyy-MM-dd")
        idx    = self.type_combo.currentIndex()
        user   = getattr(self.proxy, "current_user", "")

        if idx == 0:
            _, s = self.proxy._request("POST", "/eventos",
                {"title": title, "date": d_str, "description": "-", "created_by": user})
        elif idx == 1:
            _, s = self.proxy._request("POST", "/tarefas",
                {"title": title, "description": "-", "date": d_str, "created_by": user})
        else:
            _, s = self.proxy._request("POST", "/lembretes",
                {"title": title, "datetime": f"{d_str}T09:00:00", "created_by": user})

        if s in [200, 201]:
            self.accept()
        elif s == 409:
            self.err_lbl.setText("Já existe um item com este nome nesta data.")
        else:
            self.err_lbl.setText("Erro ao comunicar com o servidor.")


# ──────────────────────────────────────────────
# FilterDialog — with error on invalid range
# ──────────────────────────────────────────────

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar por período")
        self.setFixedSize(360, 220)
        self.setStyleSheet(BASE_STYLE)
        self.start_date = None
        self.end_date   = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(12)

        lbl = QLabel("Selecionar período:")
        lbl.setStyleSheet(f"font-weight: 600; font-size: 14px;")
        self._layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)
        self.start_input = QDateEdit(QDate.currentDate())
        self.start_input.setCalendarPopup(True)
        self.start_input.setDisplayFormat("dd/MM/yyyy")
        form.addRow("De:", self.start_input)

        self.end_input = QDateEdit(QDate.currentDate())
        self.end_input.setCalendarPopup(True)
        self.end_input.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Até:", self.end_input)
        self._layout.addLayout(form)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

        self._layout.addStretch()
        btns = QHBoxLayout()
        cancel = gcal_btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        ok = gcal_btn("Aplicar", primary=True, small=True)
        ok.clicked.connect(self._apply)
        btns.addStretch(); btns.addWidget(cancel); btns.addWidget(ok)
        self._layout.addLayout(btns)

    def _apply(self):
        s = self.start_input.date()
        e = self.end_input.date()
        if s > e:
            self.err_lbl.setText("A data final não pode ser anterior à inicial.")
            return
        self.start_date = s.toString("yyyy-MM-dd")
        self.end_date   = e.toString("yyyy-MM-dd")
        self.accept()


# ──────────────────────────────────────────────
# DayDetailsDialog — with + quick add button
# Any day is clickable (empty or with items)
# ──────────────────────────────────────────────

class DayDetailsDialog(QDialog):
    def __init__(self, day_num, month, year, items, proxy, parent=None):
        super().__init__(parent)
        self.proxy        = proxy
        self.day_num      = day_num
        self.month        = month
        self.year         = year
        self.selected_item = None
        self.quick_added  = False

        self.setWindowTitle(f"{day_num:02d}/{month:02d}/{year}")
        self.setFixedSize(420, 420)
        self.setStyleSheet(BASE_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background: {BG_SIDE}; border-bottom: 1px solid {BORDER};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 12, 16, 12)
        date_lbl = QLabel(f"{day_num:02d}/{month:02d}/{year}")
        date_lbl.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {TEXT};")
        hl.addWidget(date_lbl)
        hl.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedSize(36, 36)
        add_btn.setToolTip("Adicionar item neste dia")
        add_btn.setStyleSheet(f"""
            QPushButton {{ background: {ACCENT}; color: white; border: none;
                          border-radius: 18px; font-size: 20px; font-weight: 300; }}
            QPushButton:hover {{ background: {ACCENT_DARK}; }}
        """)
        add_btn.clicked.connect(self._quick_add)
        hl.addWidget(add_btn)
        self._layout.addWidget(header)

        # Scroll area for items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.container = QWidget()
        self.cl = QVBoxLayout(self.container)
        self.cl.setContentsMargins(16, 12, 16, 12)
        self.cl.setSpacing(8)
        self.scroll.setWidget(self.container)
        self._layout.addWidget(self.scroll)

        self._populate(items)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(f"border-top: 1px solid {BORDER};")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 8, 16, 8)
        close = gcal_btn("Fechar", small=True)
        close.clicked.connect(self.reject)
        fl.addStretch(); fl.addWidget(close)
        self._layout.addWidget(footer)

    def _populate(self, items):
        # Clear
        for i in reversed(range(self.cl.count())):
            w = self.cl.itemAt(i).widget()
            if w:
                w.setParent(None)

        if not items:
            lbl = QLabel("Sem agenda para este dia.\nClique em  +  para adicionar.")
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; padding: 30px 0;")
            lbl.setAlignment(Qt.AlignCenter)
            self.cl.addWidget(lbl)
        else:
            for item in items:
                tipo = item.get("type", "EVENTO")
                bg, fg = type_colors(tipo)
                frame  = ClickableFrame()
                frame.setCursor(Qt.PointingHandCursor)
                frame.setStyleSheet(f"""
                    QFrame {{ background: {bg}; border-radius: 6px; border: 1px solid transparent; }}
                    QFrame:hover {{ border: 1px solid {fg}; }}
                """)
                fl = QVBoxLayout(frame)
                fl.setContentsMargins(12, 10, 12, 10)
                fl.setSpacing(3)

                top = QHBoxLayout()
                type_lbl = QLabel(tipo)
                type_lbl.setStyleSheet(f"color: {fg}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
                top.addWidget(type_lbl)
                top.addStretch()
                rec = item.get("recurrence_rule")
                if rec:
                    rec_map = {"DIARIO": "Diário", "SEMANAL": "Semanal",
                               "MENSAL": "Mensal", "ANUAL": "Anual"}
                    rl = QLabel(f"↻ {rec_map.get(rec, rec)}")
                    rl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
                    top.addWidget(rl)
                fl.addLayout(top)

                tl = QLabel(item.get("title", ""))
                tl.setStyleSheet(f"font-weight: 600; color: {TEXT}; font-size: 13px;")
                fl.addWidget(tl)

                dt_val = item.get("datetime", "")
                if dt_val and len(dt_val) > 10:
                    hl2 = QLabel(f"🕐 {dt_val[11:16]}")
                    hl2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
                    fl.addWidget(hl2)

                creator = item.get("created_by", "")
                if creator:
                    cr = QLabel(f"👤 {creator}")
                    cr.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
                    fl.addWidget(cr)

                frame.clicked.connect(lambda it=item: self._select(it))
                self.cl.addWidget(frame)

        self.cl.addStretch()

    def _quick_add(self):
        prefill = date(self.year, self.month, self.day_num)
        dlg = QuickAddDialog(self.proxy, prefill_date=prefill, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self.quick_added = True
            self.accept()

    def _select(self, item):
        self.selected_item = item
        self.accept()


# ──────────────────────────────────────────────
# DetailsDialog — created_by + recurrence rule
# ──────────────────────────────────────────────

class DetailsDialog(QDialog):
    def __init__(self, item, resource, parent=None):
        super().__init__(parent)
        self.item     = item
        self.resource = resource
        self.action   = None
        self.setWindowTitle("Detalhes")
        self.setFixedSize(400, 360)
        self.setStyleSheet(BASE_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        tipo    = item.get("type", "")
        bg, fg  = type_colors(tipo)

        # Colored header
        header = QWidget()
        header.setStyleSheet(f"background: {bg};")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 16)
        type_lbl = QLabel(tipo)
        type_lbl.setStyleSheet(f"color: {fg}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        hl.addWidget(type_lbl)
        title_lbl = QLabel(item.get("title", ""))
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT};")
        title_lbl.setWordWrap(True)
        hl.addWidget(title_lbl)
        self._layout.addWidget(header)

        # Info
        info = QWidget()
        il = QVBoxLayout(info)
        il.setContentsMargins(20, 16, 20, 16)
        il.setSpacing(10)

        raw_dt = item.get("datetime") or item.get("date", "")
        if raw_dt:
            dr = QHBoxLayout()
            dr.addWidget(QLabel("📅"))
            dv = QLabel(format_date_display(raw_dt))
            dv.setStyleSheet(f"color: {TEXT_MUTED};")
            dr.addWidget(dv); dr.addStretch()
            il.addLayout(dr)

        rec = item.get("recurrence_rule")
        if rec:
            rec_map = {"DIARIO": "Diariamente", "SEMANAL": "Semanalmente",
                       "MENSAL": "Mensalmente",  "ANUAL":   "Anualmente"}
            rr = QHBoxLayout()
            rr.addWidget(QLabel("↻"))
            rv = QLabel(rec_map.get(rec, rec))
            rv.setStyleSheet(f"color: {TEXT_MUTED};")
            rr.addWidget(rv); rr.addStretch()
            il.addLayout(rr)

        creator = item.get("created_by", "")
        if creator:
            cr = QHBoxLayout()
            cr.addWidget(QLabel("👤"))
            cv = QLabel(f"Criado por {creator}")
            cv.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            cr.addWidget(cv); cr.addStretch()
            il.addLayout(cr)

        desc = item.get("description", "")
        if desc and desc != "-":
            il.addWidget(h_sep())
            dl = QLabel(desc)
            dl.setWordWrap(True)
            dl.setStyleSheet(f"color: {TEXT};")
            il.addWidget(dl)

        il.addStretch()
        self._layout.addWidget(info, 1)

        # Footer
        footer = QWidget()
        footer.setStyleSheet(f"border-top: 1px solid {BORDER};")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 10, 16, 10)
        b_del   = gcal_btn("Excluir", danger=True, small=True)
        b_del.clicked.connect(self._on_delete)
        b_edit  = gcal_btn("Editar",  primary=True, small=True)
        b_edit.clicked.connect(self._on_edit)
        b_close = gcal_btn("Fechar",  small=True)
        b_close.clicked.connect(self.reject)
        fl.addWidget(b_del); fl.addStretch()
        fl.addWidget(b_edit); fl.addWidget(b_close)
        self._layout.addWidget(footer)

    def _on_edit(self):   self.action = "EDIT";   self.accept()
    def _on_delete(self): self.action = "DELETE";  self.accept()


# ──────────────────────────────────────────────
# EditDialog — "edit next events" for recurrence
# ──────────────────────────────────────────────

class EditDialog(QDialog):
    def __init__(self, item, resource, parent=None):
        super().__init__(parent)
        self.item        = item
        self.resource    = resource
        self.result_data = {}
        self.edit_next   = False
        self.setWindowTitle("Editar item")
        self.setFixedSize(440, 340)
        self.setStyleSheet(BASE_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(12)

        lbl = QLabel("Editar item")
        lbl.setStyleSheet(f"font-size: 16px; font-weight: 600;")
        self._layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)
        self.title_input = QLineEdit(item.get("title", ""))
        form.addRow("Título:", self.title_input)

        self.date_input     = None
        self.datetime_input = None
        self.desc_input     = None

        if resource in ["events", "tasks"]:
            self.date_input = QDateEdit(QDate.fromString(item.get("date", ""), "yyyy-MM-dd"))
            self.date_input.setCalendarPopup(True)
            self.date_input.setDisplayFormat("dd/MM/yyyy")
            form.addRow("Data:", self.date_input)
            self.desc_input = QLineEdit(item.get("description", ""))
            form.addRow("Descrição:", self.desc_input)
        elif resource == "reminders":
            self.datetime_input = QDateTimeEdit(
                QDateTime.fromString(item.get("datetime", "")[:16], "yyyy-MM-ddTHH:mm"))
            self.datetime_input.setCalendarPopup(True)
            self.datetime_input.setDisplayFormat("dd/MM/yyyy HH:mm")
            form.addRow("Data/Hora:", self.datetime_input)

        self._layout.addLayout(form)

        # Recurrence option
        self.edit_next_check = None
        if item.get("recurrence_id"):
            rec_frame = QFrame()
            rec_frame.setStyleSheet(f"background: #e8f0fe; border-radius: 6px;")
            rl = QHBoxLayout(rec_frame)
            rl.setContentsMargins(10, 8, 10, 8)
            self.edit_next_check = QCheckBox("Editar próximos eventos da série também?")
            self.edit_next_check.setStyleSheet(f"color: {ACCENT}; font-weight: 500;")
            rl.addWidget(self.edit_next_check)
            self._layout.addWidget(rec_frame)

        self._layout.addStretch()

        btns = QHBoxLayout()
        cancel = gcal_btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        save = gcal_btn("Salvar", primary=True, small=True)
        save.clicked.connect(self._save)
        btns.addStretch(); btns.addWidget(cancel); btns.addWidget(save)
        self._layout.addLayout(btns)

    def _save(self):
        self.result_data["title"] = self.title_input.text().strip()
        if self.date_input:
            self.result_data["date"] = self.date_input.date().toString("yyyy-MM-dd")
        if self.datetime_input:
            # Fixed: T separator
            self.result_data["datetime"] = self.datetime_input.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        if self.desc_input:
            self.result_data["description"] = self.desc_input.text().strip()
        if self.edit_next_check:
            self.edit_next = self.edit_next_check.isChecked()
        self.accept()


# ──────────────────────────────────────────────
# DeleteConfirmDialog
# ──────────────────────────────────────────────

class DeleteConfirmDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar exclusão")
        self.setFixedSize(360, 160)
        self.setStyleSheet(BASE_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(12)

        msg = QLabel(f"Deseja excluir permanentemente\n\"{title}\"?")
        msg.setStyleSheet(f"font-size: 14px; color: {TEXT};")
        msg.setWordWrap(True)
        self._layout.addWidget(msg)
        self._layout.addStretch()

        btns = QHBoxLayout()
        cancel  = gcal_btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        confirm = gcal_btn("Excluir", danger=True, small=True)
        confirm.clicked.connect(self.accept)
        btns.addStretch(); btns.addWidget(cancel); btns.addWidget(confirm)
        self._layout.addLayout(btns)


# ──────────────────────────────────────────────
# ConnectDialog
# ──────────────────────────────────────────────

class ConnectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendário Compartilhado")
        self.setFixedSize(380, 200)
        self.setStyleSheet(BASE_STYLE)
        self.url = "http://127.0.0.1:5000"

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(28, 28, 28, 28)
        self._layout.setSpacing(14)

        title = QLabel("Calendário Compartilhado")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT};")
        self._layout.addWidget(title)

        sub = QLabel("IP do servidor (vazio = localhost):")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self._layout.addWidget(sub)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("127.0.0.1")
        self.ip_input.returnPressed.connect(self._connect)
        self._layout.addWidget(self.ip_input)

        btn = gcal_btn("Conectar", primary=True)
        btn.clicked.connect(self._connect)
        self._layout.addWidget(btn)

    def _connect(self):
        val = self.ip_input.text().strip()
        if val:
            self.url = val if val.startswith("http") else f"http://{val}:5000"
        self.accept()


# ──────────────────────────────────────────────
# UserDialog — create + delete user
# ──────────────────────────────────────────────

class UserDialog(QDialog):
    def __init__(self, proxy):
        super().__init__()
        self.proxy         = proxy
        self.selected_user = None
        self.users_data    = []
        self.setWindowTitle("Selecionar usuário")
        self.setFixedSize(400, 320)
        self.setStyleSheet(BASE_STYLE)
        self._init_ui()
        self._load_users()

    def _init_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(10)

        title = QLabel("Quem é você?")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT};")
        self._layout.addWidget(title)

        sub = QLabel("Selecione ou crie um usuário para continuar.")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self._layout.addWidget(sub)
        self._layout.addWidget(h_sep())

        # Combo + Select + Delete
        self.cb = QComboBox()
        self.cb.setMinimumHeight(36)
        self._layout.addWidget(self.cb)

        btn_row = QHBoxLayout()
        self.btn_select = gcal_btn("Entrar", primary=True, small=True)
        self.btn_select.clicked.connect(self._select)
        self.btn_delete = gcal_btn("Deletar", danger=True, small=True)
        self.btn_delete.clicked.connect(self._delete)
        btn_row.addWidget(self.btn_select)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_delete)
        self._layout.addLayout(btn_row)

        self._layout.addWidget(h_sep())

        new_lbl = QLabel("Novo usuário:")
        new_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self._layout.addWidget(new_lbl)

        create_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome")
        self.name_input.returnPressed.connect(self._create)
        create_row.addWidget(self.name_input)
        btn_new = gcal_btn("Criar", small=True)
        btn_new.clicked.connect(self._create)
        create_row.addWidget(btn_new)
        self._layout.addLayout(create_row)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

    def _load_users(self):
        self.cb.clear()
        self.users_data = []
        try:
            users, status = self.proxy.get_users()
            if status == 200 and users:
                for u in users:
                    self.cb.addItem(u.get("name", ""))
                    self.users_data.append(u)
        except Exception:
            self.err_lbl.setText("Erro ao carregar usuários.")

    def _select(self):
        if self.cb.count() == 0:
            self.err_lbl.setText("Nenhum usuário. Crie um novo.")
            return
        self.selected_user = self.cb.currentText()
        self.accept()

    def _delete(self):
        idx = self.cb.currentIndex()
        if idx < 0 or idx >= len(self.users_data):
            return
        user = self.users_data[idx]
        _, s = self.proxy.delete_user(user.get("id", ""))
        if s == 200:
            self._load_users()
            self.err_lbl.setText("")
        else:
            self.err_lbl.setText("Erro ao deletar usuário.")

    def _create(self):
        name = self.name_input.text().strip()
        if not name:
            self.err_lbl.setText("O nome não pode estar vazio.")
            return
        email = f"{name.lower().replace(' ', '.')}@calendar.app"
        _, s = self.proxy.create_user(name, email)
        if s in [200, 201]:
            self.selected_user = name
            self.accept()
        else:
            self.err_lbl.setText("Erro ao criar usuário.")


# ──────────────────────────────────────────────
# AgendaPanel — all fixes applied
# ──────────────────────────────────────────────

class AgendaPanel(QWidget):
    def __init__(self, proxy):
        super().__init__()
        self.proxy          = proxy
        self.curr_date      = date.today()
        self._filter_start  = None
        self._filter_end    = None
        # Debounce timer for real-time search
        self._search_timer  = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load_month)
        self._init_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Top bar
        topbar = QWidget()
        topbar.setStyleSheet(f"background: {BG}; border-bottom: 1px solid {BORDER};")
        tbl = QHBoxLayout(topbar)
        tbl.setContentsMargins(16, 10, 16, 10)
        tbl.setSpacing(8)

        # Real-time search — title only
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔍 Buscar por título...")
        self.inp_search.setFixedHeight(36)
        self.inp_search.setMaximumWidth(280)
        self.inp_search.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_SIDE}; border: 1px solid {BORDER};
                border-radius: 20px; padding: 6px 14px;
            }}
            QLineEdit:focus {{ border: 2px solid {ACCENT}; background: {BG}; }}
        """)
        # 300 ms debounce — real-time
        self.inp_search.textChanged.connect(lambda: self._search_timer.start(300))
        tbl.addWidget(self.inp_search)

        self.btn_filter = gcal_btn("Filtrar período", small=True)
        self.btn_filter.clicked.connect(self._open_filter)
        tbl.addWidget(self.btn_filter)

        self.btn_clear = gcal_btn("✕ Limpar", small=True)
        self.btn_clear.clicked.connect(self._clear_filters)
        self.btn_clear.hide()
        tbl.addWidget(self.btn_clear)

        tbl.addStretch()

        btn_today = gcal_btn("Hoje", small=True)
        btn_today.clicked.connect(self._go_today)
        tbl.addWidget(btn_today)

        self.btn_prev = QPushButton("‹")
        self.btn_next = QPushButton("›")
        for b in [self.btn_prev, self.btn_next]:
            b.setFixedSize(32, 32)
            b.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {BORDER}; border-radius: 16px;
                    background: {BG}; color: {TEXT}; font-size: 20px;
                }}
                QPushButton:hover {{ background: {BG_HOVER}; }}
            """)
        self.btn_prev.clicked.connect(self._prev_month)
        self.btn_next.clicked.connect(self._next_month)

        self.lbl_month = QLabel("")
        self.lbl_month.setStyleSheet(f"font-size: 17px; font-weight: 600; color: {TEXT}; padding: 0 8px;")

        tbl.addWidget(self.btn_prev)
        tbl.addWidget(self.lbl_month)
        tbl.addWidget(self.btn_next)
        self._layout.addWidget(topbar)

        # Filter info bar
        self.filter_info = QLabel("")
        self.filter_info.setStyleSheet(f"background: #e8f0fe; color: {ACCENT}; font-size: 12px; padding: 4px 16px;")
        self.filter_info.hide()
        self._layout.addWidget(self.filter_info)

        # Calendar area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background: {BG};")
        self.content_vl = QVBoxLayout(self.content_widget)
        self.content_vl.setContentsMargins(8, 8, 8, 8)
        self.content_vl.setSpacing(6)
        self.scroll.setWidget(self.content_widget)
        self._layout.addWidget(self.scroll, 1)

        self._load_month()

    def _go_today(self):
        self.curr_date = date.today()
        self._clear_filters()

    def _open_filter(self):
        dlg = FilterDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._filter_start = dlg.start_date
            self._filter_end   = dlg.end_date
            s = format_date_display(self._filter_start)
            e = format_date_display(self._filter_end)
            self.filter_info.setText(f"  Período filtrado: {s} → {e}")
            self.filter_info.show()
            self.btn_clear.show()
            self._load_month()

    def _clear_filters(self):
        self.inp_search.blockSignals(True)
        self.inp_search.clear()
        self.inp_search.blockSignals(False)
        self._filter_start = None
        self._filter_end   = None
        self.filter_info.hide()
        self.btn_clear.hide()
        self._load_month()

    def _prev_month(self):
        m, y = self.curr_date.month - 1, self.curr_date.year
        if m == 0: m, y = 12, y - 1
        self.curr_date = date(y, m, 1)
        self._load_month()

    def _next_month(self):
        m, y = self.curr_date.month + 1, self.curr_date.year
        if m == 13: m, y = 1, y + 1
        self.curr_date = date(y, m, 1)
        self._load_month()

    def _clear_content(self):
        while self.content_vl.count():
            item = self.content_vl.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _load_month(self):
        self._clear_content()

        search_text = self.inp_search.text().strip().lower()
        has_filter  = bool(search_text or (self._filter_start and self._filter_end))

        MONTHS = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
                  "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        if has_filter:
            self.lbl_month.setText("Resultados")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            s_date = self._filter_start or "2000-01-01"
            e_date = self._filter_end   or "2099-12-31"
        else:
            self.lbl_month.setText(f"{MONTHS[self.curr_date.month]} {self.curr_date.year}")
            self.btn_prev.setEnabled(True)
            self.btn_next.setEnabled(True)
            last   = calendar.monthrange(self.curr_date.year, self.curr_date.month)[1]
            s_date = f"{self.curr_date.year}-{self.curr_date.month:02d}-01"
            e_date = f"{self.curr_date.year}-{self.curr_date.month:02d}-{last:02d}"

        items_by_day = {}
        try:
            data, status = self.proxy.get_agenda(s_date, e_date)
            if status == 200 and data:
                for item in data:
                    # Search by title only
                    if search_text and search_text not in item.get("title", "").lower():
                        continue
                    dt_raw = item.get("date") or item.get("datetime", "")
                    if dt_raw:
                        items_by_day.setdefault(dt_raw[:10], []).append(item)
        except Exception:
            pass

        if has_filter:
            self._render_list(items_by_day)
        else:
            self._render_grid(items_by_day)

    def _render_list(self, items_by_day):
        """Filtered view: list of days with item badges"""
        sorted_days = sorted(items_by_day.keys())

        if not sorted_days:
            lbl = QLabel("Nenhum item encontrado.")
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; padding: 40px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.content_vl.addWidget(lbl)
            self.content_vl.addStretch()
            return

        for day_key in sorted_days:
            day_items = items_by_day[day_key]
            try:
                dt_obj = datetime.strptime(day_key, "%Y-%m-%d")
                day_n, mon, yr = dt_obj.day, dt_obj.month, dt_obj.year
            except:
                continue

            row = ClickableFrame()
            row.setCursor(Qt.PointingHandCursor)
            row.setStyleSheet(f"""
                QFrame {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; }}
                QFrame:hover {{ background: {BG_HOVER}; border-color: {ACCENT}; }}
            """)

            rl = QHBoxLayout(row)
            rl.setContentsMargins(16, 12, 16, 12)
            rl.setSpacing(16)

            # Date block
            dw = QWidget()
            dw.setFixedWidth(52)
            dvl = QVBoxLayout(dw)
            dvl.setContentsMargins(0, 0, 0, 0)
            dvl.setSpacing(0)
            dvl.setAlignment(Qt.AlignCenter)
            dl = QLabel(f"{day_n:02d}")
            dl.setStyleSheet(f"font-size: 22px; font-weight: 300; color: {TEXT};")
            dl.setAlignment(Qt.AlignCenter)
            ml = QLabel(dt_obj.strftime("%b").upper())
            ml.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px;")
            ml.setAlignment(Qt.AlignCenter)
            dvl.addWidget(dl); dvl.addWidget(ml)
            rl.addWidget(dw)

            vline = QFrame()
            vline.setFrameShape(QFrame.VLine)
            vline.setStyleSheet(f"background: {BORDER}; max-width: 1px; border: none;")
            rl.addWidget(vline)

            # Badges
            bw = QWidget()
            bl = QHBoxLayout(bw)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(6)
            for item in day_items:
                t = item.get("type", "")
                bg, fg = type_colors(t)
                badge = QLabel(f" {item.get('title', '')[:18]} ")
                badge.setStyleSheet(f"""
                    background: {bg}; color: {fg};
                    font-weight: 600; font-size: 12px;
                    border-radius: 4px; padding: 3px 8px;
                """)
                bl.addWidget(badge)
            bl.addStretch()
            rl.addWidget(bw, 1)

            # Fixed: use different variable names to avoid closure bug with 'date' module
            row.clicked.connect(
                lambda _dn=day_n, _mn=mon, _yr=yr, _its=day_items:
                self._open_day(_dn, _mn, _yr, _its)
            )
            self.content_vl.addWidget(row)

        self.content_vl.addStretch()

    def _render_grid(self, items_by_day):
        """Calendar grid view"""
        grid = QGridLayout()
        grid.setSpacing(4)

        DAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for col, d in enumerate(DAYS):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; padding: 4px 0;")
            grid.addWidget(lbl, 0, col)

        cal   = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.curr_date.year, self.curr_date.month)
        today = date.today()

        for r_idx, week in enumerate(weeks):
            for c_idx, day_num in enumerate(week):
                if day_num == 0:
                    empty = QFrame()
                    empty.setStyleSheet(f"background: {BG_EMPTY}; border-radius: 4px; min-height: 90px;")
                    grid.addWidget(empty, r_idx + 1, c_idx)
                    grid.setRowStretch(r_idx + 1, 1)
                    grid.setColumnStretch(c_idx, 1)
                    continue

                is_today = (today.year == self.curr_date.year and
                            today.month == self.curr_date.month and
                            today.day == day_num)

                cell = CalendarCell(day_num, is_today=is_today)
                key  = f"{self.curr_date.year}-{self.curr_date.month:02d}-{day_num:02d}"
                day_items       = items_by_day.get(key, [])
                cell.items_list = day_items

                # Max 2 badges + "+ X mais"
                for it in day_items[:2]:
                    cell.add_badge(it.get("title", ""), it.get("type", ""))
                if len(day_items) > 2:
                    more = QLabel(f"+ {len(day_items) - 2} mais")
                    more.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; padding: 0 2px;")
                    cell._cell_layout.addWidget(more)

                cell.cell_clicked.connect(
                    lambda dn, its, m=self.curr_date.month, y=self.curr_date.year:
                    self._open_day(dn, m, y, its)
                )

                grid.addWidget(cell, r_idx + 1, c_idx)
                grid.setRowStretch(r_idx + 1, 1)
                grid.setColumnStretch(c_idx, 1)

        gw = QWidget()
        gw.setLayout(grid)
        self.content_vl.addWidget(gw, 1)

    def _open_day(self, day_num, month, year, items):
        """Any day is clickable — empty or with items"""
        dlg    = DayDetailsDialog(day_num, month, year, items, self.proxy, self)
        result = dlg.exec_()
        if dlg.quick_added or (result == QDialog.Accepted and dlg.selected_item is None):
            self._load_month()
        elif result == QDialog.Accepted and dlg.selected_item:
            self._show_item_actions(dlg.selected_item)

    def _show_item_actions(self, item):
        res = {"EVENTO": "events", "TAREFA": "tasks", "LEMBRETE": "reminders"}.get(item.get("type", ""))
        det = DetailsDialog(item, res, self)
        if det.exec_() == QDialog.Accepted:
            if det.action == "EDIT":
                self._handle_edit(item, res)
            elif det.action == "DELETE":
                self._handle_delete(item, res)

    def _handle_edit(self, item, resource):
        dlg = EditDialog(item, resource, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        title = item["title"]
        if resource == "events":
            _, s = self.proxy.edit_event(title, dlg.result_data)
        elif resource == "tasks":
            _, s = self.proxy.edit_task(title, dlg.result_data)
        else:
            _, s = self.proxy.edit_reminder(title, dlg.result_data)

        if s == 200 and dlg.edit_next and item.get("recurrence_id"):
            self._edit_series(item, resource, dlg.result_data)

        if s == 200:
            Toast("Item atualizado.", self.parent())
            self._load_month()
        else:
            Toast("Erro ao atualizar.", self.parent())

    def _edit_series(self, original, resource, update_data):
        """Edit all next items in the recurrence series"""
        rec_id   = original.get("recurrence_id")
        cur_date = (original.get("date") or original.get("datetime", ""))[:10]
        try:
            all_data, s = self.proxy.get_agenda("2000-01-01", "2099-12-31")
            if s != 200:
                return
            for item in all_data:
                if item.get("recurrence_id") != rec_id:
                    continue
                item_date = (item.get("date") or item.get("datetime", ""))[:10]
                if item_date <= cur_date:
                    continue
                # Only update non-date fields to preserve each item's date
                patch = {k: v for k, v in update_data.items()
                         if k not in ("date", "datetime")}
                if not patch:
                    continue
                if resource == "events":
                    self.proxy.edit_event(item["title"], patch)
                elif resource == "tasks":
                    self.proxy.edit_task(item["title"], patch)
                else:
                    self.proxy.edit_reminder(item["title"], patch)
        except Exception:
            pass

    def _handle_delete(self, item, resource):
        dlg = DeleteConfirmDialog(item["title"], self)
        if dlg.exec_() != QDialog.Accepted:
            return
        title = item["title"]
        if resource == "events":
            _, s = self.proxy.delete_event(title)
        elif resource == "tasks":
            _, s = self.proxy.delete_task(title)
        else:
            _, s = self.proxy.delete_reminder(title)
        if s == 200:
            Toast("Item removido.", self.parent())
            self._load_month()
        else:
            Toast("Erro ao remover.", self.parent())


# ──────────────────────────────────────────────
# Create panels — recurrence + explicit created_by
# ──────────────────────────────────────────────

class CreateEventPanel(QWidget):
    def __init__(self, proxy, on_success):
        super().__init__()
        self.proxy      = proxy
        self.on_success = on_success
        self._init_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(32, 24, 32, 24)
        self._layout.setSpacing(14)

        lbl = QLabel("Novo Evento")
        lbl.setStyleSheet(f"font-size: 22px; font-weight: 300; color: {TEXT};")
        self._layout.addWidget(lbl)
        self._layout.addWidget(h_sep())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nome do evento")
        form.addRow("Título:", self.inp_title)

        self.inp_date = QDateEdit(QDate.currentDate())
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Data:", self.inp_date)

        self.inp_desc = QLineEdit()
        self.inp_desc.setPlaceholderText("Descrição (opcional)")
        form.addRow("Descrição:", self.inp_desc)

        self._layout.addLayout(form)
        self.recurrence = RecurrenceWidget()
        self._layout.addWidget(self.recurrence)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

        self._layout.addStretch()
        save = gcal_btn("Criar Evento", primary=True)
        save.clicked.connect(self._save)
        self._layout.addWidget(save)

    def _save(self):
        title = self.inp_title.text().strip()
        desc  = self.inp_desc.text().strip() or "-"
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        self.err_lbl.setText("")

        rule       = self.recurrence.get_rule()
        start      = self.inp_date.date().toPyDate()
        dates      = generate_recurrence_dates(start, rule) if rule else [start]
        rec_id     = str(uuid.uuid4()) if rule else None
        user       = getattr(self.proxy, "current_user", "")
        errors     = 0

        for d in dates:
            payload = {"title": title, "date": d.strftime("%Y-%m-%d"),
                       "description": desc, "created_by": user}
            if rec_id:
                payload["recurrence_id"]   = rec_id
                payload["recurrence_rule"] = rule
            _, s = self.proxy._request("POST", "/eventos", payload)
            if s not in [200, 201]:
                errors += 1

        if errors == 0:
            self.inp_title.clear(); self.inp_desc.clear()
            self.on_success()
        elif errors == len(dates):
            self.err_lbl.setText("Erro: já existe um item com este nome nesta data.")
        else:
            self.err_lbl.setText(f"{errors} datas com conflito foram ignoradas.")
            self.on_success()


class CreateTaskPanel(QWidget):
    def __init__(self, proxy, on_success):
        super().__init__()
        self.proxy      = proxy
        self.on_success = on_success
        self._init_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(32, 24, 32, 24)
        self._layout.setSpacing(14)

        lbl = QLabel("Nova Tarefa")
        lbl.setStyleSheet(f"font-size: 22px; font-weight: 300; color: {TEXT};")
        self._layout.addWidget(lbl)
        self._layout.addWidget(h_sep())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nome da tarefa")
        form.addRow("Título:", self.inp_title)

        self.inp_date = QDateEdit(QDate.currentDate())
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Data:", self.inp_date)

        self.inp_desc = QLineEdit()
        self.inp_desc.setPlaceholderText("Descrição (opcional)")
        form.addRow("Descrição:", self.inp_desc)

        self._layout.addLayout(form)
        self.recurrence = RecurrenceWidget()
        self._layout.addWidget(self.recurrence)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

        self._layout.addStretch()
        save = gcal_btn("Criar Tarefa", primary=True)
        save.clicked.connect(self._save)
        self._layout.addWidget(save)

    def _save(self):
        title = self.inp_title.text().strip()
        desc  = self.inp_desc.text().strip() or "-"
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        self.err_lbl.setText("")

        rule   = self.recurrence.get_rule()
        start  = self.inp_date.date().toPyDate()
        dates  = generate_recurrence_dates(start, rule) if rule else [start]
        rec_id = str(uuid.uuid4()) if rule else None
        user   = getattr(self.proxy, "current_user", "")
        errors = 0

        for d in dates:
            payload = {"title": title, "description": desc,
                       "date": d.strftime("%Y-%m-%d"), "created_by": user}
            if rec_id:
                payload["recurrence_id"]   = rec_id
                payload["recurrence_rule"] = rule
            _, s = self.proxy._request("POST", "/tarefas", payload)
            if s not in [200, 201]:
                errors += 1

        if errors == 0:
            self.inp_title.clear(); self.inp_desc.clear()
            self.on_success()
        elif errors == len(dates):
            self.err_lbl.setText("Erro: já existe um item com este nome nesta data.")
        else:
            self.err_lbl.setText(f"{errors} datas com conflito foram ignoradas.")
            self.on_success()


class CreateReminderPanel(QWidget):
    def __init__(self, proxy, on_success):
        super().__init__()
        self.proxy      = proxy
        self.on_success = on_success
        self._init_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(32, 24, 32, 24)
        self._layout.setSpacing(14)

        lbl = QLabel("Novo Lembrete")
        lbl.setStyleSheet(f"font-size: 22px; font-weight: 300; color: {TEXT};")
        self._layout.addWidget(lbl)
        self._layout.addWidget(h_sep())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Nome do lembrete")
        form.addRow("Título:", self.inp_title)

        self.inp_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.inp_dt.setCalendarPopup(True)
        # Fixed: display format without seconds, and toString uses T separator
        self.inp_dt.setDisplayFormat("dd/MM/yyyy HH:mm")
        form.addRow("Data/Hora:", self.inp_dt)

        self._layout.addLayout(form)
        self.recurrence = RecurrenceWidget()
        self._layout.addWidget(self.recurrence)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {RED}; font-size: 12px;")
        self._layout.addWidget(self.err_lbl)

        self._layout.addStretch()
        save = gcal_btn("Criar Lembrete", primary=True)
        save.clicked.connect(self._save)
        self._layout.addWidget(save)

    def _save(self):
        title = self.inp_title.text().strip()
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        self.err_lbl.setText("")

        # Fixed: use T separator
        time_part = self.inp_dt.dateTime().toString("THH:mm:ss")
        rule      = self.recurrence.get_rule()
        start     = self.inp_dt.date().toPyDate()
        dates     = generate_recurrence_dates(start, rule) if rule else [start]
        rec_id    = str(uuid.uuid4()) if rule else None
        user      = getattr(self.proxy, "current_user", "")
        errors    = 0

        for d in dates:
            dt_str  = d.strftime("%Y-%m-%d") + time_part
            payload = {"title": title, "datetime": dt_str, "created_by": user}
            if rec_id:
                payload["recurrence_id"]   = rec_id
                payload["recurrence_rule"] = rule
            _, s = self.proxy._request("POST", "/lembretes", payload)
            if s not in [200, 201]:
                errors += 1

        if errors == 0:
            self.inp_title.clear()
            self.on_success()
        elif errors == len(dates):
            self.err_lbl.setText("Erro: já existe um item com este nome nesta data.")
        else:
            self.err_lbl.setText(f"{errors} datas com conflito foram ignoradas.")
            self.on_success()


# ──────────────────────────────────────────────
# MainWindow
# ──────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy
        self.setWindowTitle("SharedCalendar")
        self.resize(1200, 750)
        self.setStyleSheet(f"background-color: {BG};")
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background: {BG_SIDE}; border-right: 1px solid {BORDER};")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(8, 16, 8, 16)
        sl.setSpacing(2)

        logo = QLabel("SharedCalendar")
        logo.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT}; padding: 8px 12px 16px 12px;")
        sl.addWidget(logo)

        self.nav_agenda = gcal_nav_btn("📅  Agenda")
        self.nav_ev     = gcal_nav_btn("📆  Novo Evento")
        self.nav_ta     = gcal_nav_btn("📋  Nova Tarefa")
        self.nav_le     = gcal_nav_btn("🔔  Novo Lembrete")
        self.nav_agenda.setChecked(True)

        for b in [self.nav_agenda, self.nav_ev, self.nav_ta, self.nav_le]:
            sl.addWidget(b)

        sl.addStretch()
        sl.addWidget(h_sep())

        # Current user
        self.user_lbl = QLabel(f"👤  {getattr(self.proxy, 'current_user', '')}")
        self.user_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; padding: 6px 14px;")
        sl.addWidget(self.user_lbl)

        btn_switch = QPushButton("Trocar usuário")
        btn_switch.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {ACCENT};
                          border: none; padding: 4px 14px; text-align: left; font-size: 12px; }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        btn_switch.clicked.connect(self._change_user)
        sl.addWidget(btn_switch)

        root.addWidget(sidebar)

        # Stack
        self.stack    = QStackedWidget()
        self.agenda_p = AgendaPanel(self.proxy)
        self.stack.addWidget(self.agenda_p)
        self.stack.addWidget(CreateEventPanel(self.proxy, self._go_agenda))
        self.stack.addWidget(CreateTaskPanel(self.proxy, self._go_agenda))
        self.stack.addWidget(CreateReminderPanel(self.proxy, self._go_agenda))
        root.addWidget(self.stack)

        self._btns = [self.nav_agenda, self.nav_ev, self.nav_ta, self.nav_le]
        self.nav_agenda.clicked.connect(lambda: self._nav(0))
        self.nav_ev.clicked.connect(lambda: self._nav(1))
        self.nav_ta.clicked.connect(lambda: self._nav(2))
        self.nav_le.clicked.connect(lambda: self._nav(3))

    def _nav(self, i):
        self.stack.setCurrentIndex(i)
        for idx, b in enumerate(self._btns):
            b.setChecked(idx == i)
        if i == 0:
            self.agenda_p._load_month()

    def _go_agenda(self):
        self._nav(0)

    def _change_user(self):
        dlg = UserDialog(self.proxy)
        if dlg.exec_() == QDialog.Accepted:
            self.proxy.current_user = dlg.selected_user
            self.user_lbl.setText(f"👤  {dlg.selected_user}")
            self.agenda_p._load_month()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def run():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 13))

    d = ConnectDialog()
    if d.exec_() != QDialog.Accepted:
        return

    proxy = CalendarProxy(d.url)

    user_dlg = UserDialog(proxy)
    if user_dlg.exec_() != QDialog.Accepted:
        return

    proxy.current_user = user_dlg.selected_user

    window = MainWindow(proxy)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()