# Instalando biblicotecas necessárias
#!pip install python-dotenv langchain langchain-google-genai langchain-community langchain-chroma chromadb google-generativeai pypdf pydantic

# Importando bibliotecas
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from retriever import carregar_db, buscar_chunks, formatar_contexto
from dotenv import load_dotenv
import os

load_dotenv()

# Configurar a API do Google
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Modelo a usar
MODELO = "gemini-2.5-flash"

# Caminho do banco de dados vetorial
caminho_db = "db"

PROMPT_TEMPLATE = """Você é um assistente especializado no Mercado Livre de Energia Elétrica Brasileiro.
Sua função é responder perguntas sobre as regras de comercialização da CCEE de forma clara e precisa.
 
REGRAS IMPORTANTES:
1. Responda APENAS com base nos trechos fornecidos abaixo.
2. Se a resposta não estiver nos trechos, diga explicitamente: "Não encontrei essa informação nas resoluções indexadas."
3. Ao final da resposta, sempre cite a fonte (nome do arquivo e página).
4. Use linguagem clara e objetiva. Evite jargão desnecessário.
5. Se a pergunta envolver prazos ou valores, destaque-os claramente.
 
TRECHOS DAS REGRAS DA CCEE:
{contexto}
 
PERGUNTA DO USUÁRIO:
{pergunta}
 
RESPOSTA:"""



def responder(pergunta: str, db : None):
    """
    Pipeline RAG completo: recebe uma pergunta e retorna a resposta com fontes.
 
    Fluxo:
    1. Busca chunks relevantes no ChromaDB
    2. Monta prompt com os chunks como contexto
    3. Envia ao Gemini
    4. Retorna resposta + chunks usados (para rastreabilidade)
 
    Args:
        pergunta: string com a pergunta do usuário
        db: instância do ChromaDB (se None, carrega do disco)
 
    Returns:
        dict com:
        - 'resposta': texto gerado pelo Gemini
        - 'chunks': lista de chunks usados como contexto
        - 'pergunta': pergunta original
    """
    # Carregar banco vetorial caso não fornecido
    if db is None:
        db = carregar_db()
    
    # Passo 1: Recuperar chunks relevantes
    chunks = buscar_chunks(pergunta, db)

    # Passo 2: Formatar contexto
    contexto = formatar_contexto(chunks)

    # Passo 3: Montar prompt
    prompt = PROMPT_TEMPLATE.format(
        contexto = contexto,
        pergunta = pergunta
    )

    # Passo 4: Chamar o Gemini
    model = genai.GenerativeModel(MODELO)
    response = model.generate_content(prompt)

    return {
        "pergunta":pergunta,
        "resposta": response.text,
        "chunks":chunks
    }


# ──────────────────────────────────────────────
# Teste rápido — execute: python src/rag_chain.py
# ──────────────────────────────────────────────
if __name__ == "__main__":
    perguntas_teste = [
        "O que é o PLD?",
        "O que é o modelo NEWAVE?"
    ]
 
    vs = carregar_db()
 
    for pergunta in perguntas_teste:
        print("\n" + "=" * 60)
        print(f"PERGUNTA: {pergunta}")
        print("=" * 60)
 
        resultado = responder(pergunta, vs)
        print(f"\nRESPOSTA:\n{resultado['resposta']}")
 
        print("\nFONTES UTILIZADAS:")
        for i, chunk in enumerate(resultado['chunks'], 1):
            print(f"  [{i}] {chunk['fonte']} | pág. {chunk['pagina']} | score: {chunk['score']}")


 



