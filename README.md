# 📅 Calendário Compartilhado — SharedCalendar

Um sistema de calendário compartilhado construído com **Python**. O projeto possui arquitetura cliente-servidor: um back-end RESTful com **Flask** e dois front-ends — uma interface **CLI** (terminal) e uma interface gráfica desktop com **PyQt5**.

O sistema permite que múltiplos usuários em uma mesma rede compartilhem e gerenciem eventos, tarefas e lembretes em tempo real, com histórico completo de ações.

---

## 🚀 Funcionalidades

### Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/usuarios` | Criação de um novo usuário |
| `GET` | `/usuarios` | Listagem de todos os usuários |
| `DELETE` | `/usuarios/<id>` | Remoção de um usuário |
| `POST` | `/eventos` | Criação de um novo evento |
| `PUT` | `/eventos/<name>` | Edição de um evento |
| `DELETE` | `/eventos/<name>` | Remoção de um evento |
| `POST` | `/lembretes` | Criação de um novo lembrete |
| `PUT` | `/lembretes/<name>` | Edição de um lembrete |
| `DELETE` | `/lembretes/<name>` | Remoção de um lembrete |
| `POST` | `/tarefas` | Adição de uma nova tarefa |
| `GET` | `/tarefas` | Listagem de todas as tarefas |
| `PUT` | `/tarefas/<name>` | Edição de uma tarefa |
| `DELETE` | `/tarefas/<name>` | Remoção de uma tarefa |
| `GET` | `/agenda?start&end` | Visualização da agenda por intervalo de datas |
| `GET` | `/find/<name>` | Busca global de item por nome |
| `GET` | `/historico` | Histórico completo de ações |

### Funcionalidades do cliente

- Visualização da agenda em calendário mensal (Qt) ou listagem por data (CLI)
- Filtro por intervalo de datas e busca em tempo real por nome
- Criação de eventos, tarefas e lembretes com suporte a **recorrência** (diária, semanal, mensal, anual)
- Edição e exclusão de itens por nome, com aviso ao modificar item de outro usuário
- Adição rápida de item ao clicar em um dia no calendário (Qt)
- Histórico de ações com snapshots **antes/depois** de cada modificação
- Seleção e criação de usuários na tela de entrada
- Suporte a múltiplos clientes na mesma rede — dados compartilhados via servidor central

---

## 🏗️ Design Patterns

| Pattern | Categoria | Onde | Papel |
|---------|-----------|------|-------|
| **Singleton** | Criacional | `AppServer`, `StorageManager`, `NotificationManager` | Garante uma única instância dos gerenciadores de estado e armazenamento durante toda a execução do servidor |
| **Observer** | Comportamental | `NotificationManager` (subject), `IObserver`, `ClientSession` | Notifica todos os clientes conectados quando um evento é criado, editado ou removido |
| **Command** | Comportamental | `ICommand`, `CreateEventCmd`, `AddTaskCmd`, `EditItemCmd`, `DeleteItemCmd`, `GetAgendaCmd`, `CreateReminderCmd` | Encapsula cada ação do usuário em um objeto independente que delega a chamada HTTP ao Proxy |
| **Proxy** | Estrutural | `CalendarProxy` | Centraliza toda a lógica de comunicação HTTP — os front-ends nunca chamam o servidor diretamente |

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.10+ |
| Back-end | Flask 3.x |
| Front-end GUI | PyQt5 |
| Front-end CLI | Terminal (built-in) |
| Persistência | JSON (sem dependências externas) |
| Testes | pytest |
| CI/CD | GitHub Actions |

---

## 📁 Estrutura do Projeto

```
SharedCalendar/
├── .github/workflows/    # GitHub Actions (CI)
├── client/
│   ├── commands/         # Command pattern — um arquivo por ação
│   ├── calendar_proxy.py # Proxy pattern — comunicação HTTP
│   ├── cli_view.py       # Interface CLI (v1.0)
│   ├── qt_view.py        # Interface Qt (v2.0)
│   └── validators.py     # Validações de input
├── server/
│   ├── data/             # Persistência JSON
│   ├── app.py            # Flask — registro de endpoints
│   ├── calendar_service.py
│   ├── task_service.py
│   ├── storage_manager.py # Singleton — persistência
│   ├── notification_manager.py # Observer — subject
│   └── observer.py       # IObserver interface
├── docs/
│   ├── diagrams/         # Diagramas de classe (servidor e cliente)
│   └── design_patterns.md
├── tests/
│   ├── test_endpoints.py
│   ├── test_integration.py
│   ├── run_tests.py
│   ├── manual_test.py
│   └── seed.py
├── conftest.py
├── COMO_RODAR.md
└── requirements.txt
```

---

## ⚙️ Como executar

Consulte o arquivo **[COMO_RODAR.md](COMO_RODAR.md)** para o guia completo de instalação e execução (Windows + VS Code).

Resumo rápido:

```bash
# 1. Clonar o repositório
git clone https://github.com/Natan-Xavier/Calend-rioCompartilhado.git
cd Calend-rioCompartilhado

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Subir o servidor (Terminal 1)
python -m server.app

# 5. Rodar o cliente CLI (Terminal 2)
python -m client.cli_view

# 6. Rodar o cliente Qt (Terminal 2)
python -m client.qt_view

# 7. Popular o banco com dados de demonstração
python tests/seed.py

# 8. Rodar os testes
pytest tests/test_endpoints.py -v
pytest tests/test_integration.py -v
```

---

## 👨‍💻 Equipe

| Membro | GitHub |
|--------|--------|
| Natan Xavier | [@Natan-Xavier](https://github.com/Natan-Xavier) |
| Pier Giorgio | [@Pier-Cesar](https://github.com/Pier-Cesar) |
| Guilherme Gomes | [@Gomes-007](https://github.com/Gomes-007) |
| Haissa Mota | [@hfontesdamota](https://github.com/hfontesdamota) |
| Paulo Alberto | [@uepaullo](https://github.com/uepaullo) |