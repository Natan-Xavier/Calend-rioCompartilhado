# 🚀 Como Rodar o SharedCalendar
### Windows + VS Code

---

## 1. Pré-requisitos

Instale as seguintes ferramentas antes de começar:

### Python
1. Acesse https://www.python.org/downloads/
2. Baixe a versão mais recente
3. **IMPORTANTE:** Durante a instalação, marque a opção **"Add Python to PATH"**
4. Verifique abrindo o PowerShell e rodando:
   ```
   python --version
   ```

### Git
1. Acesse https://git-scm.com/downloads
2. Baixe e instale com as opções padrão
3. Verifique abrindo o PowerShell e rodando:
   ```
   git --version
   ```

### VS Code
1. Acesse https://code.visualstudio.com/
2. Baixe e instale
3. Abra o VS Code e instale a extensão **Python**:
   - `Ctrl+Shift+X` → pesquise "Python" → instale a da Microsoft

---

## 2. Clonar o repositório

1. Abra o VS Code
2. Pressione `Ctrl+Shift+P` → digite `Git: Clone`
3. Cole a URL do repositório:
   ```
   https://github.com/SEU_USUARIO/Calend-rioCompartilhado.git
   ```
4. Escolha uma pasta para salvar
5. Clique em **Open** quando perguntar se quer abrir o projeto

---

## 3. Abrir o terminal no VS Code

Pressione `` Ctrl+` `` (acento grave) para abrir o terminal integrado.

Certifique-se que está na pasta do projeto — o terminal deve mostrar algo como:
```
PS C:\Users\seu_usuario\Calend-rioCompartilhado>
```

---

## 4. Criar o ambiente virtual (venv)

No terminal do VS Code, rode:

```
python -m venv .venv
```

Ative o venv:

```
.venv\Scripts\activate
```

Você saberá que está ativo quando aparecer `(.venv)` no início do terminal:
```
(.venv) PS C:\Users\seu_usuario\Calend-rioCompartilhado>
```

⚠️ Se aparecer um erro de permissão, rode antes:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
E tente ativar o venv novamente.

---

## 5. Selecionar o interpretador Python no VS Code

1. Pressione `Ctrl+Shift+P`
2. Digite `Python: Select Interpreter`
3. Escolha a opção que contém `.venv` no caminho

---

## 6. Instalar dependências

Com o venv ativo no terminal, rode:

```
pip install -r requirements.txt
```

---

## 7. Rodar o servidor

No terminal com o venv ativo, rode:

```
python -m server.app
```

Você verá algo como:
```
* Running on http://0.0.0.0:5000
* Running on http://192.168.1.10:5000
```

⚠️ **Deixe esse terminal aberto** — o servidor precisa estar rodando.

---

## 8. Abrir um segundo terminal

No VS Code, clique no **+** ao lado do terminal atual para abrir um segundo.

Ative o venv no novo terminal:
```
.venv\Scripts\activate
```

---

## 9. Descobrir o IP do servidor (para outros na rede)

Na máquina que roda o servidor, no terminal rode:
```
ipconfig
```

Procure por **IPv4 Address** — ex: `192.168.1.10`

---

## 10. Rodar o cliente CLI

No segundo terminal (com venv ativo), rode:

```
python -m client.cli_view
```

Você verá:
```
IP do servidor (Enter para localhost):
```

- Se estiver na **mesma máquina** que o servidor → aperte **Enter**
- Se estiver em **outra máquina na mesma rede** → digite o IP (ex: `192.168.1.10`)

O menu aparece:
```
=============================================
          📅 SharedCalendar
=============================================
  1. Ver agenda (por intervalo de datas)
  2. Criar evento
  3. Criar tarefa
  4. Criar lembrete
  5. Editar item
  6. Deletar item
  7. Criar usuário
  0. Sair
=============================================
```

---

## 11. Rodar os testes

### Testes automatizados (pytest):
```
pytest tests/test_endpoints.py -v
```

### Teste manual com output visual:
Abra dois terminais:

**Terminal 1 — servidor:**
```
python -m server.app
```

**Terminal 2 — teste manual:**
```
python tests/manual_test.py
```

---

## 12. Ver os testes no GitHub Actions

Os testes rodam automaticamente a cada push no GitHub.

1. Acesse o repositório no GitHub
2. Clique na aba **Actions**
3. Clique no último workflow **Server Tests**
4. Expanda os steps **Run pytest** e **Run endpoint output tests** para ver o output completo

---

## Resumo rápido

| O que fazer | Comando |
|---|---|
| Ativar venv | `.venv\Scripts\activate` |
| Instalar dependências | `pip install -r requirements.txt` |
| Rodar servidor | `python -m server.app` |
| Rodar cliente CLI | `python -m client.cli_view` |
| Rodar testes | `pytest tests/test_endpoints.py -v` |
| Pegar atualizações | `git pull` |
| Enviar alterações | `git add . && git commit -m "msg" && git push` |