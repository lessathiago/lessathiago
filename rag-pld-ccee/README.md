# 🔍 RAG — Assistente de Consulta às Regras de Comercialização da CCEE (PLD)

> Sistema de Retrieval-Augmented Generation (RAG) para consulta em linguagem natural às **Regras de Comercialização da CCEE** relacionadas ao **Preço de Liquidação das Diferenças (PLD)**, com rastreabilidade da fonte de cada resposta.

---

## 📌 Contexto de Negócio

A CCEE (Câmara de Comercialização de Energia Elétrica) publica as **Regras de Comercialização** que disciplinam o funcionamento do Mercado de Curto Prazo (MCP) — o ambiente onde são liquidadas as diferenças entre energia contratada e consumida/gerada. O **PLD** é o preço central desse mercado, e sua metodologia de cálculo, limites e aplicação estão descritos nesses documentos.

Profissionais de comercializadoras, geradoras e grandes consumidores precisam consultar essas regras com frequência para entender como o PLD é formado, quais são seus limites máximos e mínimos, como são tratadas as diferenças entre submercados e quais condições especiais se aplicam. Encontrar essas informações em documentos extensos e técnicos é lento e trabalhoso.

Este projeto resolve esse problema com um **assistente inteligente** que:
- Responde perguntas em linguagem natural sobre as regras do PLD
- Cita o documento e o trecho exato que embasou cada resposta
- Rejeita perguntas fora do escopo indexado, sem inventar respostas

> **Escopo delimitado:** Este assistente cobre exclusivamente os documentos das Regras de Comercialização da CCEE relacionados ao PLD. Perguntas sobre outros aspectos do mercado (medição, liquidação financeira, garantias) podem não ser respondidas adequadamente.

---

## 🎯 Objetivo

Construir um pipeline RAG completo — da ingestão de PDFs ao deploy de uma interface web — usando **Google Gemini** como LLM, **ChromaDB** como banco vetorial local e **Streamlit** para a interface.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FASE 1: INDEXAÇÃO                    │
│                   (roda uma vez)                        │
│                                                         │
│  PDFs da CCEE → Extração de Texto → Chunking           │
│      → Embeddings (Gemini) → ChromaDB (disco)          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  FASE 2: CONSULTA                       │
│                  (a cada pergunta)                      │
│                                                         │
│  Pergunta → Embedding → Busca ChromaDB (top-k chunks)  │
│      → Prompt com contexto → Gemini → Resposta + Fonte │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Estrutura do Projeto

```
ccee-pld-rag/
│
├── base/                   # Regras de Comercialização da CCEE em PDF
│   └── regras_pld_ccee.pdf
│
├── db/                   # Banco vetorial persistido (gerado pelo pipeline)
│

├── src/
│   ├── cria_db.py              # Carrega PDFs, faz chunking e indexa no ChromaDB
│   ├── retriever.py             # Busca chunks relevantes para uma pergunta
│   ├── rag.py             # Monta o prompt e chama o Gemini
│
├── app.py                       # Interface Streamlit
│
│
└── README.md
```

---

## 🗂️ Dados Utilizados

**Regras de Comercialização da CCEE — módulos relacionados ao PLD:**

| Documento | Conteúdo |
|-----------|----------|
| Regras de Comercialização| [ccee.org.br](https://www.ccee.org.br/web/guest/mercado/regras-de-comercializacao) |

**Como baixar:**
1. Acesse [ccee.org.br](https://www.ccee.org.br)
2. Navegue em: **Mercado → Regras de Comercialização**
3. Baixe os módulos relacionados a **Preço de Liquidação das Diferenças**
4. Salve em `base/`

> 💡 **Decisão de escopo:** o projeto foi intencionalmente limitado ao documento sobre PLD para manter os custos de chamadas à API dentro da faixa gratuita do Google Gemini, sem comprometer a qualidade das respostas dentro do escopo definido.

---

## 🔑 Configuração da API

1. Acesse [aistudio.google.com](https://aistudio.google.com) e gere sua API key gratuita
2. Crie um arquivo `.env` na raiz do projeto:

```
GOOGLE_API_KEY=sua_chave_aqui
```

> ⚠️ Nunca versione o arquivo `.env`. Ele já está no `.gitignore`.

---

## 🔧 Instalação e Execução

```bash
pip install -r requirements.txt

# Passo 1: indexar os PDFs (roda uma vez)
python src/criar_db.py

# Passo 2: subir a interface
streamlit run app.py
```

---

## 📦 Requirements

```
google-generativeai>=0.5
chromadb>=0.4
pypdf>=4.0
langchain>=0.2
langchain-google-genai>=1.0
langchain-community>=0.2
python-dotenv>=1.0
streamlit>=1.35
tiktoken>=0.7
```

---

## 💬 Exemplos de Perguntas

- *"Como é calculado o PLD?"*
- *"Quais são os limites máximo e mínimo do PLD?"*
- *"O PLD é o mesmo para todos os submercados?"*
- *"Com que frequência o PLD é atualizado?"*
- *"O que acontece quando o PLD atinge o limite máximo?"*

---

## 🔍 Rastreabilidade

Cada resposta inclui:
- **Documento de origem** (nome do arquivo PDF)
- **Número da página** do trecho utilizado
- **Score de similaridade** do retrieval (0 a 1)
- **Trecho exato** exibido na interface para conferência

Isso garante que o usuário possa verificar a fonte e evita respostas inventadas sobre regras do mercado.

---


## ⚠️ Limitações

- O assistente responde **apenas** com base nos documentos indexados. Perguntas fora do escopo do PLD retornam uma resposta explícita de "não encontrado".
- As Regras de Comercialização da CCEE são atualizadas periodicamente. O assistente reflete a versão dos documentos indexados — **sempre verifique a data da versão do documento**.
- O modelo não substitui consulta jurídica ou regulatória especializada.

---

## 🚀 Deploy

Interface hospedada gratuitamente no **Streamlit Community Cloud**:

https://lessathiago-rag-pld-ccee.streamlit.app/

---


## 👤 Autor

**Thiago Lessa da Costa**
Analista de Backoffice | Comercializadora de Energia | Estatística | Pós-graduando em IA e Negócios

[LinkedIn](https://linkedin.com/in/thiago-lessa) · [GitHub](https://github.com/lessathiago/lessathiago/)
