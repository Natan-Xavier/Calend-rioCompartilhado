from datetime import datetime

ACCEPTED_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d/%m/%y",
]


def parse_date(value):
    """Converte qualquer formato aceito para YYYY-MM-DD (formato do servidor)"""
    value = value.strip()
    for fmt in ACCEPTED_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_datetime(value):
    """Converte data e hora para YYYY-MM-DDTHH:MM:SS"""
    value = value.strip()
    formats = [
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return None


def format_display_date(value):
    """Converte YYYY-MM-DD para DD/MM/YYYY (exibição)"""
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return value


def validate_not_empty(value, field_name):
    """Valida que o campo não está vazio"""
    if not value or not value.strip():
        print(f"❌ {field_name} não pode ser vazio!")
        return False
    return True


def validate_max_length(value, field_name, max_len=100):
    """Valida tamanho máximo"""
    if len(value.strip()) > max_len:
        print(f"❌ {field_name} não pode ter mais de {max_len} caracteres!")
        return False
    return True