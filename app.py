import os
import json
import numpy as np
import openai
import sqlite3
from flask import Flask, request, jsonify
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            agent TEXT,
            message TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    return response.data[0].embedding

def sac_retrieval(query):
    # Carga de documentos de conhecimento
    with open('dados-sac.md', 'r', encoding='utf-8') as f:
        sac_content = f.read()
    # Divide o conteúdo em tópicos
    sac_paragraphs = sac_content.split('# ')[1:]  # O primeiro tópico é vazio

    # Cria embeddings para cada trecho
    paragraph_embeddings = [get_embedding(p) for p in sac_paragraphs]
    embedding = get_embedding(query)

    # Calcular similaridade com cada trecho
    similarities = []
    for idx, pemb in enumerate(paragraph_embeddings):
        sim = np.dot(embedding, pemb) / (
            np.linalg.norm(embedding) * np.linalg.norm(pemb)
        )
        similarities.append((sim, sac_paragraphs[idx]))

    # Selecionar o trecho mais similar
    similarities.sort(reverse=True, key=lambda x: x[0])
    context = similarities[0][1]
    
    return context

# Função do agente SAC
def sac_agent(query):
    context = sac_retrieval(query)
    prompt = f"""
    Responda às perguntas com base no seguinte conhecimento:\n
    {context}\n
    Pergunta: {query}\n
    Resposta:
    """
    response = client.responses.create(
        model='gpt-4o',
        input=prompt
    )
    return response.output_text

def product_agent(query):
    with open('dados-produtos.json', 'r', encoding='utf-8') as f:
        product_catalog = json.load(f)

    # Filtrar produtos relevantes
    filtered_product = list(
        filter(lambda p: p['productId'] == query, product_catalog)
    )

    # Implementar lógica de resposta do agente de produtos
    if not filtered_product:
        return "Produto não encontrado."

    return json.dumps(filtered_product)

# Endpoints da API
@app.route('/iniciar', methods=['POST'])
def start_session():
    session_id = request.json.get('session_id')
    message = request.json.get('message')
    
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    hello_str = "Olá! Bem-vindo ao atendimento da C&A. Como posso ajudar você hoje?"
    c.execute('''
              INSERT INTO history (session_id, agent, message, response)
              VALUES (?, ?, ?, ?)
              ''', (session_id, 'system', message, hello_str))
    conn.commit()
    conn.close()
    
    return jsonify({"response": hello_str})

@app.route('/mensagem', methods=['POST'])
def handle_message():
    session_id = request.json.get('session_id')
    message = request.json.get('message')
    agent = request.json.get('agent')  # 'sac' ou 'produto'

    # Armazena na história
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    if agent == 'sac':
        response = sac_agent(message)
    elif agent == 'produto':
        response = product_agent(message)
    else:
        response = "Agente desconhecido."

    # Salvar histórico
    c.execute('''
              INSERT INTO history (session_id, agent, message, response)
              VALUES (?, ?, ?, ?)
              ''', (session_id, agent, message, response))
    conn.commit()
    conn.close()

    return jsonify({"response": response})

@app.route('/historico/<session_id>', methods=['GET'])
def get_history(session_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    c.execute('SELECT agent, message, response FROM history WHERE session_id = ?',
              (session_id,))
    rows = c.fetchall()
    conn.close()

    history = [
        {"agent": r[0], "user_message": r[1], "agent_response": r[2]} for r in rows
    ]

    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True)
