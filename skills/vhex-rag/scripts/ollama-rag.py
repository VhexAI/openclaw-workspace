#!/usr/bin/env python3
import os
import json
import sys
import numpy as np
import ollama

EMBED_MODEL = 'nomic-embed-text'
LLM_MODEL = 'llama3.2:3b'
WORKSPACE = '/home/vhex/.openclaw/workspace'
DB_PATH = os.path.join(WORKSPACE, 'memory', 'vhex-rag-db.json')
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')

def chunk_text(text):
    paras = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
    sentences = []
    for p in paras:
        sents = p.split('. ')
        sentences.extend([s.strip() for s in sents if len(s.strip()) > 50])
    return sentences[:20]  # limit per file

def get_embedding(text):
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return resp['embedding']

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def index():
    chunks = []
    sources = []
    # Index memory dir
    for root, dirs, files in os.walk(MEMORY_DIR):
        for file in files:
            if file.endswith('.md') and file != 'vhex-rag-db.json':
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    file_chunks = chunk_text(text)
                    for ch in file_chunks:
                        chunks.append(ch)
                        sources.append(file)
    # Also index MEMORY.md from workspace root
    memory_md = os.path.join(WORKSPACE, 'MEMORY.md')
    if os.path.exists(memory_md):
        with open(memory_md, 'r', encoding='utf-8') as f:
            text = f.read()
            file_chunks = chunk_text(text)
            for ch in file_chunks:
                chunks.append(ch)
                sources.append('MEMORY.md')
    print(f'Indexing {len(chunks)} chunks from {len(set(sources))} files...')
    db = []
    for i, ch in enumerate(chunks):
        try:
            emb = get_embedding(ch)
            db.append({
                'text': ch,
                'embedding': emb,
                'source': sources[i]
            })
            if (i + 1) % 10 == 0:
                print(f'Progress: {i+1}/{len(chunks)}')
        except Exception as e:
            print(f'Error embedding chunk {i}: {e}')
    with open(DB_PATH, 'w') as f:
        json.dump(db, f)
    print(f'Index complete. {len(db)} chunks saved to {DB_PATH}')

def query(q, top_k=5):
    if not os.path.exists(DB_PATH):
        print('No DB found. Run "index" first.')
        return None
    with open(DB_PATH, 'r') as f:
        db = json.load(f)
    q_emb = get_embedding(q)
    sims = []
    for i, doc in enumerate(db):
        sim = cosine_similarity(np.array(q_emb), np.array(doc['embedding']))
        sims.append((sim, doc))
    sims.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for sim, doc in sims[:top_k]]
    context = '\n---\n'.join([f"[{doc['source']}]\n{doc['text']}" for doc in top_docs])
    prompt = f"""Vhex Memory RAG:
Context from memory:
{context}

Query: {q}

Answer concisely using ONLY the context above. If no relevant info, say so."""
    resp = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user', 'content': prompt}])
    return resp['message']['content']

def generate_finetune_data(n=100):
    if not os.path.exists(DB_PATH):
        print('Index first.')
        return
    with open(DB_PATH, 'r') as f:
        db = json.load(f)[:50]
    data = []
    for _ in range(n):
        chunk = np.random.choice(db)['text']
        qa_prompt = f"Context: {chunk}\nQuestion: "
        q = ollama.generate(model=LLM_MODEL, prompt=qa_prompt + 'Generate a question about this context.')['response']
        a = ollama.generate(model=LLM_MODEL, prompt=f"Q: {q}\nA: ")['response']
        data.append({'prompt': chunk, 'question': q, 'answer': a})
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 ollama-rag.py [index|query "text"|finetune-data]')
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'index':
        index()
    elif cmd == 'query':
        q = ' '.join(sys.argv[2:])
        result = query(q)
        if result:
            print(result)
    elif cmd == 'finetune-data':
        generate_finetune_data()
    else:
        print('Unknown cmd')
