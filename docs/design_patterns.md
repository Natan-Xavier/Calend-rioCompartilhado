# Padrões de Projeto — CalendárioCompartilhado

Este documento descreve os quatro padrões de projeto implementados no sistema CalendárioCompartilhado, onde cada um é aplicado e por que foi escolhido.

---

## 1. Singleton

**Categoria:** Criacional

**Onde:** `AppServer`, `StorageManager`, `NotificationManager` — lado do servidor

**Como funciona:**
Cada uma dessas classes possui um atributo privado `_instance` e um método de classe `get_instance()`. Na primeira chamada, o objeto é criado. Em todas as chamadas seguintes, o mesmo objeto é retornado. A instanciação direta via construtor é bloqueada.

**Por que foi usado:**
Múltiplas requisições Flask podem chegar ao mesmo tempo. Sem o Singleton, cada requisição poderia criar seu próprio `StorageManager`, causando condições de corrida e dados inconsistentes. Garantir uma única instância compartilhada para o gerenciamento de armazenamento e notificações mantém o estado do servidor consistente entre todas as requisições.

---

## 2. Observer

**Categoria:** Comportamental

**Onde:** `NotificationManager` (sujeito), `IObserver` (interface), `ClientSession` (observador concreto) — lado do servidor

**Como funciona:**
O `NotificationManager` mantém uma lista de objetos `ClientSession`. Sempre que uma operação de escrita ocorre (criar evento, adicionar tarefa, etc.), o endpoint Flask chama `NotificationManager.notify(event)`, que percorre todas as sessões registradas e chama `update(event)` em cada uma. Qualquer classe que queira receber notificações deve implementar a interface `IObserver`, que exige o método `update()`.

**Por que foi usado:**
O calendário é compartilhado entre múltiplos usuários. Quando um usuário modifica dados, todos os outros clientes conectados precisam ser informados. O padrão Observer desacopla a lógica de notificação da lógica de negócio — os serviços e endpoints nunca sabem quem está escutando, apenas disparam `notify()` e o gerenciador cuida do resto.

---

## 3. Command

**Categoria:** Comportamental

**Onde:** `ICommand` (interface), `CreateUserCmd`, `CreateEventCmd`, `CreateReminderCmd`, `AddTaskCmd`, `GetTasksCmd`, `DeleteTaskCmd` — lado do cliente

**Como funciona:**
Cada ação do usuário é encapsulada em um objeto Command. Cada comando concreto implementa a interface `ICommand`, que exige o método `execute()`. A camada de interface (`CLIView` ou `QtView`) constrói o Command adequado, injeta um `CalendarProxy` nele e chama `execute()`. O Command então delega a chamada HTTP ao proxy. Cada Command corresponde diretamente a um endpoint Flask.

**Por que foi usado:**
Encapsular cada ação em sua própria classe isola a intenção da ação da mecânica de executá-la. Isso facilita a adição de novas operações (basta criar um novo Command), e mantém tanto a camada de interface quanto a camada do proxy completamente independentes entre si. Também facilita os testes — cada Command pode ser testado de forma isolada.

---

## 4. Proxy

**Categoria:** Estrutural

**Onde:** `CalendarProxy` — lado do cliente

**Como funciona:**
O `CalendarProxy` é a única classe no cliente que conhece a `base_url` do servidor e constrói as requisições HTTP. Ele expõe um método por endpoint (`create_user()`, `create_event()`, `add_task()`, `get_tasks()`, `delete_task()`, `create_reminder()`), e internamente gerencia a construção das requisições, o tratamento de erros e o parsing das respostas por meio de métodos privados (`_request()`, `_handle_err()`, `_parse_resp()`). Todos os Commands e as duas interfaces possuem uma referência ao `CalendarProxy` e nunca fazem chamadas HTTP diretamente.

**Por que foi usado:**
Centralizar toda a lógica de rede em um único lugar significa que, se a URL do servidor mudar, cabeçalhos de autenticação forem adicionados ou o protocolo for atualizado, apenas o `CalendarProxy` precisa ser alterado. O restante do cliente — Commands, CLI, Qt — permanece intocado. Também facilita simular o proxy durante os testes de integração sem precisar subir um servidor real.

---

## Resumo da Interação entre os Padrões

```
[CLIView / QtView]
       │
       │  constrói
       ▼
  [ICommand] ◄─────────────────── ação do usuário
       │
       │  chama
       ▼
 [CalendarProxy]  ──── HTTP ────► [endpoints Flask]
                                         │
                                         │  delega para
                                         ▼
                               [CalendarService / TaskService]
                                         │
                                         │  lê/grava via
                                         ▼
                                  [StorageManager]  ◄── Singleton
                                         │
                                         │  após escrita, dispara
                                         ▼
                               [NotificationManager]  ◄── Singleton + Sujeito
                                         │
                                         │  notify()
                                         ▼
                                  [ClientSession]  ◄── Observer
```