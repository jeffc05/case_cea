# Case C&A - Cientista de Dados


## Visão Geral
Esta aplicação de chat inteligente consiste em um sistema RESTful que integra dois agentes especializados: um de SAC, que responde perguntas relacionadas às políticas da empresa usando busca por conhecimento em um arquivo Markdown, e outro de Produtos, que realiza buscas no catálogo fornecido. Mantendo o histórico das conversas em um banco SQLite, ela permite iniciar sessões, enviar mensagens específicas aos agentes, obter respostas contextuais e recuperar o histórico completo da conversa, proporcionando uma interação contínua e personalizada para o usuário.


## Instruções de instalação e execução
Uma vez clonado esse repositório para a sua máquina local:

### 1. Use o arquivo `requirements.txt` para criar um ambiente virtual pip.
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2. Abra o arquivo `app.py` e localize a linha:
```
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```
Substitua `os.getenv("OPENAI_API_KEY")` pela sua chave obtida na plataforma OpenAI:
```
client = OpenAI(api_key='sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX')
```

### 3. Para iniciar a aplicação, execute:
```
python app.py
```
Você verá algo como:
```
 * Running on http://127.0.0.1:5000/
```
Indicando que o servidor está ativo na porta 5000.


## Descrição dos endpoints e exemplos de uso

### 1. `/iniciar` (POST)
**Função**: Cria ou inicia uma nova sessão de conversa, recebendo um `session_id` fornecido pelo cliente. Serve para marcar o início de um diálogo, permitindo que o sistema armazene o histórico correspondente a essa sessão.

**Entrada**: JSON com `session_id`.

**Resposta**: Uma mensagem de boas-vindas.

**Exemplo**:
```
curl -X POST http://127.0.0.1:5000/iniciar \
-H "Content-Type: application/json" \
-d '{"session_id": 1}'
```

### 2. `/mensagem` (POST)
**Função**: Recebe uma mensagem do usuário, juntamente com o `session_id` e o agente especificado (`sac` ou `produto`). Envia a mensagem ao agente correspondente, obtém a resposta gerada, armazena toda a troca no banco de dados e retorna a resposta ao cliente.

**Entrada**: JSON com `session_id`, `message` e `agent`.

**Resposta**: A resposta gerada pelo agente, que responde com base na mensagem enviada.

**Exemplo**:
```
curl -X POST http://127.0.0.1:5000/mensagem \
-H "Content-Type: application/json" \
-d '{"session_id": 1, "message": "Como devolver uma roupa comprada no site C&A?", "agent": "sac"}'
```
Ou:
```
curl -X POST http://127.0.0.1:5000/mensagem \
-H "Content-Type: application/json" \
-d '{"session_id": 1, "message": 2093380, "agent": "produto"}'
```

### 3. `/historico/<session_id>` (GET)
**Função**: Recupera todo o histórico de troca de mensagens e respostas registrada para a sessão identificada pelo `session_id`.

**Entrada**: `session_id` na URL.

**Resposta**: Lista de mensagens e respostas do diálogo, incluindo quem enviou cada mensagem.

**Exemplo**:
```
curl -X GET http://127.0.0.1:5000/historico/1
```
