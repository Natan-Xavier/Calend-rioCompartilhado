import requests

BASE_URL = "http://127.0.0.1:5000"

def post(endpoint, data):
    r = requests.post(f"{BASE_URL}{endpoint}", json=data)
    status = "✅" if r.status_code in [200, 201] else "⚠️ "
    print(f"{status} {r.status_code} - {data.get('title', data.get('name'))}")

print("\n🌱 Populando banco de dados...\n")

# Eventos
print("📅 Eventos:")
post("/eventos", {"title": "Feira de Carreiras", "date": "2026-05-20", "description": "Evento anual de recrutamento"})
post("/eventos", {"title": "Reunião de Planejamento", "date": "2026-05-22", "description": "Planejamento do próximo sprint"})
post("/eventos", {"title": "Apresentação do Projeto", "date": "2026-05-26", "description": "Entrega final da disciplina"})
post("/eventos", {"title": "Hackathon FIAP", "date": "2026-06-05", "description": "Maratona de programação"})
post("/eventos", {"title": "Defesa de TCC", "date": "2026-06-15", "description": "Apresentação do trabalho de conclusão"})

# Lembretes
print("\n🔔 Lembretes:")
post("/lembretes", {"title": "Entregar relatório", "datetime": "2026-05-18T09:00:00"})
post("/lembretes", {"title": "Reunião às 14h", "datetime": "2026-05-21T14:00:00"})
post("/lembretes", {"title": "Comprar material de escritório", "datetime": "2026-05-23T10:00:00"})
post("/lembretes", {"title": "Ligar para o orientador", "datetime": "2026-05-28T11:00:00"})
post("/lembretes", {"title": "Renovar matrícula", "datetime": "2026-06-01T08:00:00"})

# Tarefas
print("\n✅ Tarefas:")
post("/tarefas", {"title": "Implementar tela Qt", "description": "Interface gráfica versão 2.0", "date": "2026-05-19"})
post("/tarefas", {"title": "Revisar documentação", "description": "Atualizar README e design patterns", "date": "2026-05-21"})
post("/tarefas", {"title": "Corrigir bugs do CLI", "description": "Validações e mensagens de erro", "date": "2026-05-22"})
post("/tarefas", {"title": "Preparar slides", "description": "Apresentação final do projeto", "date": "2026-05-25"})
post("/tarefas", {"title": "Fazer testes de usabilidade", "description": "Testar com usuários reais", "date": "2026-05-26"})

print("\n✅ Banco populado com sucesso!")
print("   5 eventos | 5 lembretes | 5 tarefas")