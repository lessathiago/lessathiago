""" 
retriever.py

Fase 2 do RAG: Dada uma pergunta, busca os chunks mais relevantes no banco de dados por similaridade semântica

Essa é a parte "R" do RAG.

"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

CAMINHO_DB = "db"

TOP_K = 2     
# Quantos chunks recuperar por pergunta. Quanto mais chunks, mais contexto, o que pode confundir o LLM

def carregar_db():
    """ 
    Carrega o banco vetorial já existente.
    Deve ser chamado após rodar o criar_db.py pelo menos uma vez.
    """

    if not os.path.exists(CAMINHO_DB):
        raise FileNotFoundError(
            f"Banco vetorial não encontrado em {CAMINHO_DB}. "
            "Execute primeiro o arquivo criar_db.py"
        )
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    db = Chroma(
        persist_directory=CAMINHO_DB,
        embedding_function=embeddings
    )
    return db

def buscar_chunks(pergunta:str, db:Chroma, top_k: int = TOP_K):
    """
    Recebe uma pergunta e retorna os chunks mais relevantes no DB.

    Como funciona:
    1. A pergunta é convertida em embedding (mesmo modelo usado na indexação)
    2. O ChromaDB calcula a distância entre o embedding da pergunta e todos os embeddings indexados
    3. Retorna os top_k chunks mais próximos (mais similares semanticamente)
 
    Retorna lista de dicts com:
    - 'conteudo': texto do chunk
    - 'fonte': nome do arquivo PDF
    - 'pagina': número da página
    - 'score': score de similaridade (0 a 1, maior = mais relevante)
    """

    # Busca com score de relevância
    resultados = db.similarity_search_with_relevance_scores(pergunta, top_k)

    chunks_formatados = []
    for doc, score in resultados:
        chunks_formatados.append({
            "conteudo":doc.page_content,
            "fonte":doc.metadata.get("source_file", "desconhecido"),
            "pagina":doc.metadata.get("page", "?"),
            "score": round(score, 4)
        })

    return chunks_formatados


def formatar_contexto(chunks: list):
    """
    Formata os chunks recuperados em um bloco de contexto para ser inserido no prompt do LLM.
    """
    contexto = ""
    for i, chunk in enumerate(chunks, 1):
        contexto += (
            f"[Fonte {i}: {chunk['fonte']}, página {chunk['pagina']}"
            f"(relevância : {chunk['score']})]\n"
            f"{chunk['conteudo']}\n\n"
        )

    return contexto.strip()


#
# Teste rápido - execute retriever.py
#

if __name__ == "__main__":
    print("Carregando banco vetorial...")
    vs = carregar_db()
 
    pergunta = "O que é o PLD?"
    print(f"\nPergunta: {pergunta}")
    print("-" * 50)
 
    chunks = buscar_chunks(pergunta, vs)
    for i, c in enumerate(chunks, 1):
        print(f"\n[Chunk {i}] {c['fonte']} | pág. {c['pagina']} | score: {c['score']}")
        print(c['conteudo'][:300] + "...")

              


