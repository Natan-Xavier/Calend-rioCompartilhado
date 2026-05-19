import requests
import sys
from datetime import date, timedelta

BASE_URL = f"http://{sys.argv[1]}:5000" if len(sys.argv) > 1 else "http://127.0.0.1:5000"


def post(endpoint, data):
    r = requests.post(f"{BASE_URL}{endpoint}", json=data)
    status = "✅" if r.status_code in [200, 201] else "⚠️ "
    print(f"  {status} {r.status_code} - {data.get('title', data.get('name', ''))}")
    return r.json() if r.status_code in [200, 201] else {}


print(f"\n🌱 Populando banco em {BASE_URL}...\n")

# ── Usuários ───────────────────────────────────────────
print("👤 Usuários:")
post("/usuarios", {"name": "Paulo Alberto",    "email": "ana@calendar.app"})
post("/usuarios", {"name": "Nathan Xavier",  "email": "bruno@calendar.app"})
post("/usuarios", {"name": "Haissa Mota", "email": "carol@calendar.app"})

# ── Eventos ────────────────────────────────────────────
print("\n📆 Eventos:")
post("/eventos", {"title": "Apresentação do Projeto",  "date": "2026-05-26",
                  "description": "Entrega final da disciplina", "created_by": "Ana Silva"})

post("/eventos", {"title": "Reunião de Planejamento",  "date": "2026-05-22",
                  "description": "Planejamento do próximo sprint", "created_by": "Bruno Costa"})

post("/eventos", {"title": "Hackathon FIAP",           "date": "2026-06-05",
                  "description": "Maratona de programação", "created_by": "Carol Mendes"})

post("/eventos", {"title": "Defesa de TCC",            "date": "2026-06-20",
                  "description": "Apresentação do trabalho de conclusão", "created_by": "Ana Silva"})

post("/eventos", {"title": "Workshop de Python",       "date": "2026-05-28",
                  "description": "Workshop sobre Python avançado", "created_by": "Bruno Costa"})

# Evento recorrente (semanal — simula 4 semanas)
import uuid
rec_id = str(uuid.uuid4())
for i in range(4):
    d = date(2026, 5, 19) + timedelta(weeks=i)
    post("/eventos", {
        "title": "Daily Scrum", "date": d.strftime("%Y-%m-%d"),
        "description": "Reunião diária do time",
        "created_by": "Bruno Costa",
        "recurrence_id": rec_id,
        "recurrence_rule": "SEMANAL"
    })

# ── Lembretes ──────────────────────────────────────────
print("\n🔔 Lembretes:")
post("/lembretes", {"title": "Entregar relatório",       "datetime": "2026-05-20T09:00:00",
                    "created_by": "Ana Silva"})

post("/lembretes", {"title": "Reunião às 14h",           "datetime": "2026-05-21T14:00:00",
                    "created_by": "Bruno Costa"})

post("/lembretes", {"title": "Comprar material",         "datetime": "2026-05-23T10:00:00",
                    "created_by": "Carol Mendes"})

post("/lembretes", {"title": "Ligar para orientador",    "datetime": "2026-05-27T11:00:00",
                    "created_by": "Ana Silva"})

post("/lembretes", {"title": "Renovar matrícula",        "datetime": "2026-06-01T08:00:00",
                    "created_by": "Bruno Costa"})

# Lembrete recorrente (mensal — 3 meses)
rec_id2 = str(uuid.uuid4())
for i, month in enumerate(["05", "06", "07"]):
    post("/lembretes", {
        "title": "Backup dos arquivos", "datetime": f"2026-{month}-01T08:00:00",
        "created_by": "Carol Mendes",
        "recurrence_id": rec_id2,
        "recurrence_rule": "MENSAL"
    })

# ── Tarefas ────────────────────────────────────────────
print("\n📋 Tarefas:")
post("/tarefas", {"title": "Implementar tela Qt",    "description": "Interface gráfica v2.0",
                  "date": "2026-05-19", "created_by": "Ana Silva"})

post("/tarefas", {"title": "Revisar documentação",   "description": "Atualizar README e design patterns",
                  "date": "2026-05-21", "created_by": "Bruno Costa"})

post("/tarefas", {"title": "Corrigir bugs do CLI",   "description": "Validações e mensagens de erro",
                  "date": "2026-05-22", "created_by": "Carol Mendes"})

post("/tarefas", {"title": "Preparar slides",        "description": "Apresentação final do projeto",
                  "date": "2026-05-25", "created_by": "Ana Silva"})

post("/tarefas", {"title": "Testes de usabilidade",  "description": "Testar com usuários reais",
                  "date": "2026-05-26", "created_by": "Bruno Costa"})

post("/tarefas", {"title": "Deploy do servidor",     "description": "Subir o servidor na rede da faculdade",
                  "date": "2026-06-03", "created_by": "Carol Mendes"})

print("\n✅ Banco populado!")
print("   3 usuários | 9 eventos | 8 lembretes | 6 tarefas")