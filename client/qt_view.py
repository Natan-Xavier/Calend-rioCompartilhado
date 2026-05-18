import sys
import calendar
from datetime import datetime, date

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDialog, QFormLayout, QDateEdit,
    QDateTimeEdit, QFrame, QStackedWidget, QScrollArea, QGridLayout,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QDate, QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from client.calendar_proxy import CalendarProxy

# ──────────────────────────────────────────────
# Paleta monocromática profissional
# ──────────────────────────────────────────────
BG          = "#0f0f0f"
BG2         = "#1a1a1a"
BG3         = "#242424"
BORDER      = "#2e2e2e"
TEXT        = "#e8e8e8"
TEXT_MUTED  = "#666666"
TEXT_DIM    = "#444444"
ACCENT      = "#4a4a4a"
ACCENT_LT   = "#5a5a5a"
WHITE       = "#ffffff"
TODAY_BDR   = "#888888"

EVENTO_CLR   = "#a0a0a0"
TAREFA_CLR   = "#7a7a7a"
LEMBRETE_CLR = "#c0c0c0"

BASE_STYLE = f"""
    QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-family: 'Segoe UI', 'Consolas', monospace;
        font-size: 13px;
    }}
    QLineEdit, QDateEdit, QDateTimeEdit {{
        background-color: {BG2};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 7px 10px;
        selection-background-color: {ACCENT};
    }}
    QLineEdit:focus, QDateEdit:focus, QDateTimeEdit:focus {{
        border: 1px solid {ACCENT_LT};
    }}
    QScrollBar:vertical {{
        background: {BG};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {ACCENT};
        border-radius: 3px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QDialog {{ background-color: {BG}; }}
    QCalendarWidget {{ background-color: {BG2}; color: {TEXT}; }}
"""


# ──────────────────────────────────────────────
# Componentes base
# ──────────────────────────────────────────────

class ClickableFrame(QFrame):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()


def btn(text, primary=False, danger=False, small=False):
    b = QPushButton(text)
    pad = "5px 14px" if small else "8px 22px"
    if danger:
        bg, bg_h, color = "#2a1a1a", "#3a2020", "#cc5555"
    elif primary:
        bg, bg_h, color = "#2a2a2a", "#333333", WHITE
    else:
        bg, bg_h, color = BG2, BG3, TEXT_MUTED
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg}; color: {color};
            border: 1px solid {BORDER}; border-radius: 4px;
            padding: {pad}; font-weight: 500; letter-spacing: 0.3px;
        }}
        QPushButton:hover {{ background-color: {bg_h}; color: {WHITE}; }}
        QPushButton:pressed {{ background-color: {bg}; }}
    """)
    return b


def nav_btn(text, icon=""):
    b = QPushButton(f"  {icon}   {text}")
    b.setCheckable(True)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent; color: {TEXT_MUTED};
            border: none; border-left: 2px solid transparent;
            padding: 11px 16px; text-align: left;
            font-weight: 400; font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {BG2}; color: {TEXT};
            border-left: 2px solid {ACCENT_LT};
        }}
        QPushButton:checked {{
            background-color: {BG2}; color: {WHITE};
            border-left: 2px solid {WHITE}; font-weight: 600;
        }}
    """)
    return b


def section_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 0;")
    return lbl


def divider():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
    return f


def format_date_display(dt_str):
    """Converte YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS para DD/MM/YYYY ou DD/MM/YYYY HH:MM"""
    if not dt_str or dt_str == "Sem data":
        return "Sem data"
    try:
        if "T" in dt_str:
            d = datetime.strptime(dt_str[:16], "%Y-%m-%dT%H:%M")
            return d.strftime("%d/%m/%Y %H:%M")
        else:
            d = datetime.strptime(dt_str[:10], "%Y-%m-%d")
            return d.strftime("%d/%m/%Y")
    except:
        return dt_str


# ──────────────────────────────────────────────
# Toast não-bloqueante
# ──────────────────────────────────────────────

class Toast(QLabel):
    def __init__(self, message, parent=None):
        super().__init__(message, parent)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {BG3}; color: {WHITE};
                border: 1px solid {BORDER}; border-radius: 4px;
                padding: 8px 18px; font-weight: 500;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()
        if parent:
            pw = parent.width()
            ph = parent.height()
            self.move((pw - self.width()) // 2, ph - self.height() - 24)
        self.show()
        self.raise_()
        QTimer.singleShot(2200, self.deleteLater)


# ──────────────────────────────────────────────
# DaySummaryDialog — 1 badge + "+x itens"
# ──────────────────────────────────────────────

class DaySummaryDialog(QDialog):
    def __init__(self, day, month, year, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{day:02d}/{month:02d}/{year}")
        self.setFixedSize(360, 420)
        self.setStyleSheet(BASE_STYLE)
        self.selected_item = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel(f"{day:02d}/{month:02d}/{year}")
        header.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WHITE};")
        layout.addWidget(header)
        layout.addWidget(divider())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setSpacing(6)

        if not items:
            cl.addWidget(QLabel("Nenhum item para este dia."))
        for item in items:
            tipo = item.get("type", "")
            clr = {"EVENTO": EVENTO_CLR, "TAREFA": TAREFA_CLR, "LEMBRETE": LEMBRETE_CLR}.get(tipo, TEXT)
            ico = {"EVENTO": "◆", "TAREFA": "▣", "LEMBRETE": "◉"}.get(tipo, "·")
            b = QPushButton(f" {ico}  {item.get('title')}")
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG2}; color: {clr};
                    border: 1px solid {BORDER}; border-radius: 4px;
                    padding: 10px 12px; text-align: left; font-weight: 500;
                }}
                QPushButton:hover {{ background-color: {BG3}; border-color: {clr}; color: {WHITE}; }}
            """)
            b.clicked.connect(lambda _, it=item: self._select(it))
            cl.addWidget(b)

        cl.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        close = btn("Fechar", small=True)
        close.clicked.connect(self.reject)
        layout.addWidget(close, alignment=Qt.AlignRight)

    def _select(self, item):
        self.selected_item = item
        self.accept()


# ──────────────────────────────────────────────
# DetailsDialog — data em DD/MM/YYYY
# ──────────────────────────────────────────────

class DetailsDialog(QDialog):
    def __init__(self, item, resource, parent=None):
        super().__init__(parent)
        self.item = item
        self.resource = resource
        self.action = None
        self.setWindowTitle("Detalhes")
        self.setFixedSize(400, 300)
        self.setStyleSheet(BASE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        tipo = item.get("type", "")
        clr = {"EVENTO": EVENTO_CLR, "TAREFA": TAREFA_CLR, "LEMBRETE": LEMBRETE_CLR}.get(tipo, TEXT)
        ico = {"EVENTO": "◆", "TAREFA": "▣", "LEMBRETE": "◉"}.get(tipo, "·")

        top = QHBoxLayout()
        badge = QLabel(f" {ico}  {tipo} ")
        badge.setStyleSheet(f"color: {clr}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        top.addWidget(badge)
        top.addStretch()
        layout.addLayout(top)

        title = QLabel(item.get("title"))
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WHITE};")
        title.setWordWrap(True)
        layout.addWidget(title)

        raw_dt = item.get("datetime") or item.get("date") or "Sem data"
        date_lbl = QLabel(f"  {format_date_display(raw_dt)}")
        date_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(date_lbl)

        layout.addWidget(divider())

        desc = QLabel(item.get("description") or "Sem descrição.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(desc)

        layout.addStretch()

        btns = QHBoxLayout()
        b_del = btn("Excluir", danger=True, small=True)
        b_del.clicked.connect(self._on_delete)
        b_edit = btn("Editar", primary=True, small=True)
        b_edit.clicked.connect(self._on_edit)
        b_close = btn("Fechar", small=True)
        b_close.clicked.connect(self.reject)
        btns.addWidget(b_del)
        btns.addStretch()
        btns.addWidget(b_edit)
        btns.addWidget(b_close)
        layout.addLayout(btns)

    def _on_edit(self): self.action = "EDIT"; self.accept()
    def _on_delete(self): self.action = "DELETE"; self.accept()


# ──────────────────────────────────────────────
# EditDialog
# ──────────────────────────────────────────────

class EditDialog(QDialog):
    def __init__(self, item, resource, parent=None):
        super().__init__(parent)
        self.item = item
        self.resource = resource
        self.result_data = {}
        self.setWindowTitle("Editar")
        self.setFixedSize(420, 300)
        self.setStyleSheet(BASE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)
        self.title_input = QLineEdit(item.get("title", ""))
        form.addRow("Título:", self.title_input)
        self.date_input = None
        self.datetime_input = None
        self.desc_input = None

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

        layout.addLayout(form)
        layout.addStretch()

        btns = QHBoxLayout()
        cancel = btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        save = btn("Salvar", primary=True, small=True)
        save.clicked.connect(self._save)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

    def _save(self):
        self.result_data["title"] = self.title_input.text().strip()
        if self.date_input:
            self.result_data["date"] = self.date_input.date().toString("yyyy-MM-dd")
        if self.datetime_input:
            self.result_data["datetime"] = self.datetime_input.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        if self.desc_input:
            self.result_data["description"] = self.desc_input.text().strip()
        self.accept()


# ──────────────────────────────────────────────
# DeleteConfirmDialog — com botão cancelar
# ──────────────────────────────────────────────

class DeleteConfirmDialog(QDialog):
    def __init__(self, title, resource, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar exclusão")
        self.setFixedSize(340, 160)
        self.setStyleSheet(BASE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        msg = QLabel(f"Deseja excluir\n\"{title}\"?")
        msg.setStyleSheet(f"color: {WHITE}; font-size: 14px; font-weight: 500;")
        msg.setWordWrap(True)
        layout.addWidget(msg)
        layout.addStretch()

        btns = QHBoxLayout()
        cancel = btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        confirm = btn("Excluir", danger=True, small=True)
        confirm.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(confirm)
        layout.addLayout(btns)


# ──────────────────────────────────────────────
# ConnectDialog
# ──────────────────────────────────────────────

class ConnectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SharedCalendar")
        self.setFixedSize(360, 180)
        self.setStyleSheet(BASE_STYLE)
        self.url = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("SharedCalendar")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {WHITE};")
        layout.addWidget(title)

        sub = QLabel("IP do servidor (vazio = localhost):")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(sub)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("127.0.0.1")
        layout.addWidget(self.ip_input)

        ok = btn("Conectar", primary=True)
        ok.clicked.connect(self._connect)
        layout.addWidget(ok)

    def _connect(self):
        ip = self.ip_input.text().strip() or "127.0.0.1"
        if ip.startswith("http"):
            self.url = ip
        else:
            self.url = f"http://{ip}:5000"
        self.accept()


# ──────────────────────────────────────────────
# FilterDialog — filtro por intervalo de datas
# ──────────────────────────────────────────────

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar por período")
        self.setFixedSize(340, 200)
        self.setStyleSheet(BASE_STYLE)
        self.start_date = None
        self.end_date = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Filtrar agenda por período:"))
        layout.addWidget(divider())

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
        layout.addLayout(form)

        layout.addStretch()
        btns = QHBoxLayout()
        cancel = btn("Cancelar", small=True)
        cancel.clicked.connect(self.reject)
        ok = btn("Filtrar", primary=True, small=True)
        ok.clicked.connect(self._apply)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _apply(self):
        s = self.start_input.date()
        e = self.end_input.date()
        if s > e:
            err = QLabel("Data final não pode ser anterior à inicial.")
            err.setStyleSheet(f"color: #cc5555;")
            self.layout().insertWidget(3, err)
            QTimer.singleShot(2000, err.deleteLater)
            return
        self.start_date = s.toString("yyyy-MM-dd")
        self.end_date = e.toString("yyyy-MM-dd")
        self.accept()


# ──────────────────────────────────────────────
# AgendaPanel — calendário com badges corrigidas
# ──────────────────────────────────────────────

class AgendaPanel(QWidget):
    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy
        self._filter_start = None
        self._filter_end = None
        today = date.today()
        self.current_year, self.current_month = today.year, today.month
        self._build()
        self._load_month()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("Agenda")
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {WHITE};")
        header.addWidget(title)
        header.addStretch()

        self.filter_btn = btn("Filtrar", small=True)
        self.filter_btn.clicked.connect(self._open_filter)
        self.clear_filter_btn = btn("× Limpar filtro", small=True)
        self.clear_filter_btn.clicked.connect(self._clear_filter)
        self.clear_filter_btn.hide()

        refresh = btn("↻", small=True)
        refresh.clicked.connect(self._load_month)
        header.addWidget(self.filter_btn)
        header.addWidget(self.clear_filter_btn)
        header.addWidget(refresh)
        layout.addLayout(header)

        self.filter_lbl = QLabel("")
        self.filter_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        self.filter_lbl.hide()
        layout.addWidget(self.filter_lbl)

        # Navegação de mês
        nav = QHBoxLayout()
        self.prev_b = btn("◀", small=True)
        self.prev_b.clicked.connect(self._prev_month)
        self.month_lbl = QLabel("")
        self.month_lbl.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {WHITE};")
        self.month_lbl.setAlignment(Qt.AlignCenter)
        self.next_b = btn("▶", small=True)
        self.next_b.clicked.connect(self._next_month)
        nav.addWidget(self.prev_b)
        nav.addStretch()
        nav.addWidget(self.month_lbl)
        nav.addStretch()
        nav.addWidget(self.next_b)
        layout.addLayout(nav)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

    def _open_filter(self):
        d = FilterDialog(self)
        if d.exec_() == QDialog.Accepted:
            self._filter_start = d.start_date
            self._filter_end = d.end_date
            self.clear_filter_btn.show()
            s_fmt = format_date_display(self._filter_start)
            e_fmt = format_date_display(self._filter_end)
            self.filter_lbl.setText(f"Filtrando: {s_fmt} → {e_fmt}")
            self.filter_lbl.show()
            self._load_month()

    def _clear_filter(self):
        self._filter_start = None
        self._filter_end = None
        self.clear_filter_btn.hide()
        self.filter_lbl.hide()
        self._load_month()

    def _prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self._load_month()

    def _next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self._load_month()

    def _load_month(self):
        months = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
                  "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.month_lbl.setText(f"{months[self.current_month]} {self.current_year}")
        _, last = calendar.monthrange(self.current_year, self.current_month)

        if self._filter_start and self._filter_end:
            start = self._filter_start
            end = self._filter_end
        else:
            start = f"{self.current_year}-{self.current_month:02d}-01"
            end = f"{self.current_year}-{self.current_month:02d}-{last:02d}"

        data, status = self.proxy.get_agenda(start, end)
        self._populate_grid(data if status == 200 else [])

    def _populate_grid(self, items):
        while self.grid_layout.count():
            w = self.grid_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        items_by_day = {}
        for it in items:
            d_str = it.get("datetime") or it.get("date") or ""
            if len(d_str) >= 10:
                try:
                    d = int(d_str[8:10])
                    items_by_day.setdefault(d, []).append(it)
                except:
                    pass

        headers = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for col, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
            self.grid_layout.addWidget(lbl, 0, col)

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)
        today = date.today()

        for r, week in enumerate(weeks, 1):
            for c, day in enumerate(week):
                if day == 0:
                    f = QFrame()
                    f.setStyleSheet(f"background: {BG2}; border-radius: 4px; min-height: 80px;")
                    self.grid_layout.addWidget(f, r, c)
                    continue

                is_today = (self.current_year == today.year and
                            self.current_month == today.month and
                            day == today.day)

                cell = ClickableFrame()
                cell.setCursor(Qt.PointingHandCursor)
                border = f"1px solid {TODAY_BDR}" if is_today else f"1px solid {BORDER}"
                cell.setStyleSheet(f"""
                    QFrame {{
                        background: {BG2}; border: {border};
                        border-radius: 4px; min-height: 80px;
                    }}
                    QFrame:hover {{ background: {BG3}; }}
                """)

                l = QVBoxLayout(cell)
                l.setContentsMargins(6, 6, 6, 4)
                l.setSpacing(2)

                day_lbl = QLabel(str(day))
                day_lbl.setStyleSheet(
                    f"color: {WHITE if is_today else TEXT_MUTED}; font-weight: {'700' if is_today else '400'}; "
                    f"font-size: 12px; border: none; background: transparent;"
                )
                l.addWidget(day_lbl)

                day_items = items_by_day.get(day, [])

                # Mostra apenas 1 item + badge "+x itens"
                if day_items:
                    first = day_items[0]
                    tipo = first.get("type", "")
                    clr = {"EVENTO": EVENTO_CLR, "TAREFA": TAREFA_CLR, "LEMBRETE": LEMBRETE_CLR}.get(tipo, TEXT)
                    ico = {"EVENTO": "◆", "TAREFA": "▣", "LEMBRETE": "◉"}.get(tipo, "·")
                    title_txt = first.get("title", "")[:11]
                    mini = QLabel(f"{ico} {title_txt}{'…' if len(first.get('title','')) > 11 else ''}")
                    mini.setStyleSheet(
                        f"font-size: 9px; color: {clr}; border: none; background: transparent; font-weight: 500;")
                    l.addWidget(mini)

                    if len(day_items) > 1:
                        more = QLabel(f"+ {len(day_items) - 1} mais")
                        more.setStyleSheet(
                            f"font-size: 9px; color: {TEXT_DIM}; border: none; background: transparent;")
                        l.addWidget(more)

                l.addStretch()
                cell.clicked.connect(lambda d=day, its=day_items: self._open_day(d, its))
                self.grid_layout.addWidget(cell, r, c)

    def _open_day(self, day, items):
        if not items:
            return
        summary = DaySummaryDialog(day, self.current_month, self.current_year, items, self)
        if summary.exec_() == QDialog.Accepted and summary.selected_item:
            self._show_item_actions(summary.selected_item)

    def _show_item_actions(self, item):
        res = {"EVENTO": "events", "TAREFA": "tasks", "LEMBRETE": "reminders"}.get(item.get("type", ""))
        det = DetailsDialog(item, res, self)
        det.exec_()
        if det.action == "EDIT":
            self._handle_edit(item, res)
        elif det.action == "DELETE":
            self._handle_delete(item, res)

    def _handle_edit(self, item, resource):
        dialog = EditDialog(item, resource, self)
        if dialog.exec_() == QDialog.Accepted:
            if resource == "events":
                _, s = self.proxy.edit_event(item["title"], dialog.result_data)
            elif resource == "tasks":
                _, s = self.proxy.edit_task(item["title"], dialog.result_data)
            else:
                _, s = self.proxy.edit_reminder(item["title"], dialog.result_data)
            if s == 200:
                Toast("Item atualizado.", self)
                self._load_month()
            else:
                Toast("Erro ao atualizar.", self)

    def _handle_delete(self, item, resource):
        dialog = DeleteConfirmDialog(item["title"], resource, self)
        if dialog.exec_() == QDialog.Accepted:
            if resource == "events":
                _, s = self.proxy.delete_event(item["title"])
            elif resource == "tasks":
                _, s = self.proxy.delete_task(item["title"])
            else:
                _, s = self.proxy.delete_reminder(item["title"])
            if s == 200:
                Toast("Item removido.", self)
                self._load_month()
            else:
                Toast("Erro ao remover.", self)


# ──────────────────────────────────────────────
# Painéis de criação — com labels e validação
# ──────────────────────────────────────────────

class CreateEventPanel(QWidget):
    def __init__(self, proxy, on_success=None):
        super().__init__()
        self.proxy = proxy
        self.on_success = on_success
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        layout.addWidget(section_label("NOVO EVENTO"))
        title_lbl = QLabel("Título")
        title_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(title_lbl)
        self.t_in = QLineEdit()
        self.t_in.setPlaceholderText("Nome do evento")
        layout.addWidget(self.t_in)

        date_lbl = QLabel("Data")
        date_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(date_lbl)
        self.d_in = QDateEdit(QDate.currentDate())
        self.d_in.setCalendarPopup(True)
        self.d_in.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.d_in)

        desc_lbl = QLabel("Descrição")
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(desc_lbl)
        self.ds_in = QLineEdit()
        self.ds_in.setPlaceholderText("Descrição do evento")
        layout.addWidget(self.ds_in)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: #cc5555; font-size: 12px;")
        layout.addWidget(self.err_lbl)

        b_save = btn("Criar Evento", primary=True)
        b_save.clicked.connect(self._submit)
        layout.addWidget(b_save)
        layout.addStretch()

    def _submit(self):
        title = self.t_in.text().strip()
        desc = self.ds_in.text().strip()
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        if not desc:
            self.err_lbl.setText("A descrição não pode estar vazia.")
            return
        self.err_lbl.setText("")
        date_str = self.d_in.date().toString("yyyy-MM-dd")
        _, s = self.proxy.create_event(title, date_str, desc)
        if s == 201:
            self.t_in.clear()
            self.ds_in.clear()
            if self.on_success:
                self.on_success()
        elif s == 409:
            self.err_lbl.setText("Já existe um item com este nome.")
        else:
            self.err_lbl.setText("Erro ao conectar ao servidor.")


class CreateTaskPanel(QWidget):
    def __init__(self, proxy, on_success=None):
        super().__init__()
        self.proxy = proxy
        self.on_success = on_success
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        layout.addWidget(section_label("NOVA TAREFA"))

        title_lbl = QLabel("Título")
        title_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(title_lbl)
        self.t_in = QLineEdit()
        self.t_in.setPlaceholderText("Nome da tarefa")
        layout.addWidget(self.t_in)

        desc_lbl = QLabel("Descrição")
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(desc_lbl)
        self.ds_in = QLineEdit()
        self.ds_in.setPlaceholderText("Descrição da tarefa")
        layout.addWidget(self.ds_in)

        date_lbl = QLabel("Data")
        date_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(date_lbl)
        self.d_in = QDateEdit(QDate.currentDate())
        self.d_in.setCalendarPopup(True)
        self.d_in.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.d_in)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: #cc5555; font-size: 12px;")
        layout.addWidget(self.err_lbl)

        b_save = btn("Criar Tarefa", primary=True)
        b_save.clicked.connect(self._submit)
        layout.addWidget(b_save)
        layout.addStretch()

    def _submit(self):
        title = self.t_in.text().strip()
        desc = self.ds_in.text().strip()
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        if not desc:
            self.err_lbl.setText("A descrição não pode estar vazia.")
            return
        self.err_lbl.setText("")
        date_str = self.d_in.date().toString("yyyy-MM-dd")
        _, s = self.proxy.add_task(title, desc, date_str)
        if s == 201:
            self.t_in.clear()
            self.ds_in.clear()
            if self.on_success:
                self.on_success()
        elif s == 409:
            self.err_lbl.setText("Já existe um item com este nome.")
        else:
            self.err_lbl.setText("Erro ao conectar ao servidor.")


class CreateReminderPanel(QWidget):
    def __init__(self, proxy, on_success=None):
        super().__init__()
        self.proxy = proxy
        self.on_success = on_success
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        layout.addWidget(section_label("NOVO LEMBRETE"))

        title_lbl = QLabel("Título")
        title_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(title_lbl)
        self.t_in = QLineEdit()
        self.t_in.setPlaceholderText("Nome do lembrete")
        layout.addWidget(self.t_in)

        dt_lbl = QLabel("Data e hora")
        dt_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(dt_lbl)
        self.dt_in = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_in.setCalendarPopup(True)
        self.dt_in.setDisplayFormat("dd/MM/yyyy HH:mm")
        layout.addWidget(self.dt_in)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: #cc5555; font-size: 12px;")
        layout.addWidget(self.err_lbl)

        b_save = btn("Criar Lembrete", primary=True)
        b_save.clicked.connect(self._submit)
        layout.addWidget(b_save)
        layout.addStretch()

    def _submit(self):
        title = self.t_in.text().strip()
        if not title:
            self.err_lbl.setText("O título não pode estar vazio.")
            return
        self.err_lbl.setText("")
        dt_str = self.dt_in.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        _, s = self.proxy.create_reminder(title, dt_str)
        if s == 201:
            self.t_in.clear()
            if self.on_success:
                self.on_success()
        elif s == 409:
            self.err_lbl.setText("Já existe um item com este nome.")
        else:
            self.err_lbl.setText("Erro ao conectar ao servidor.")


# ──────────────────────────────────────────────
# MainWindow — tamanho fixo, fullscreen opcional
# ──────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy
        self.setWindowTitle("SharedCalendar")
        self.setFixedSize(1100, 720)
        self.setStyleSheet(BASE_STYLE)
        self._build_ui()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self.setFixedSize(1100, 720)
            else:
                self.setMaximumSize(16777215, 16777215)
                self.showFullScreen()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(190)
        sidebar.setStyleSheet(f"background: {BG2}; border-right: 1px solid {BORDER};")
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(0, 20, 0, 20)
        sl.setSpacing(2)

        app_title = QLabel("SharedCalendar")
        app_title.setStyleSheet(f"color: {WHITE}; font-size: 13px; font-weight: 700; padding: 0 16px 16px 16px;")
        sl.addWidget(app_title)
        sl.addWidget(divider())
        sl.addSpacing(8)

        self.nav_agenda = nav_btn("Agenda", "▦")
        self.nav_agenda.setChecked(True)
        self.nav_ev = nav_btn("Novo Evento", "◆")
        self.nav_ta = nav_btn("Nova Tarefa", "▣")
        self.nav_le = nav_btn("Novo Lembrete", "◉")

        for b in [self.nav_agenda, self.nav_ev, self.nav_ta, self.nav_le]:
            sl.addWidget(b)

        sl.addStretch()

        hint = QLabel("F11 — tela cheia")
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; padding: 0 16px;")
        sl.addWidget(hint)

        root.addWidget(sidebar)

        # Stack
        self.stack = QStackedWidget()
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


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def run():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 13))
    d = ConnectDialog()
    if d.exec_() == QDialog.Accepted:
        w = MainWindow(CalendarProxy(d.url))
        w.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    run()