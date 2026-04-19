"""
app.py
------
Interface Streamlit do Assistente de Comercialização de Energia.
 
Execute com:
    streamlit run app.py
"""
 
import os
import streamlit as st
from dotenv import load_dotenv
from retriever import carregar_db
from rag import responder
 
load_dotenv()
 
# ──────────────────────────────────────────────
# Configuração da página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Assistente MLE",
    page_icon="⚡",
    layout="wide"
)
 
st.title("⚡ Assistente de Comercialização de Energia")
st.markdown(
    "Faça perguntas em linguagem natural sobre as **Regras do PLD**. "
    "Cada resposta inclui a fonte exata do documento."
)
 
# ──────────────────────────────────────────────
# Carregar banco vetorial (cache para não recarregar a cada interação)
# ──────────────────────────────────────────────
@st.cache_resource
def get_db():
    """
    @st.cache_resource: o ChromaDB é carregado uma vez
    e reutilizado em todas as interações do usuário.
    """
    return carregar_db()
 
 
# Verificar se o banco vetorial existe
if not os.path.exists("db"):
    st.error(
        "⚠️ Banco vetorial não encontrado. "
        "Execute primeiro: `python criar_db.py`"
    )
    st.stop()
 
vectorstore = get_db()
 
# ──────────────────────────────────────────────
# Histórico de conversa (mantido na sessão)
# ──────────────────────────────────────────────
if "historico" not in st.session_state:
    st.session_state.historico = []
 
# ──────────────────────────────────────────────
# Sidebar — informações do projeto
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ Sobre o Projeto")
    st.markdown("""
    **Tecnologias:**
    - 🤖 Google Gemini 2.5 Flash
    - 🗄️ ChromaDB (banco vetorial)
    - 🔗 LangChain
    - 🎈 Streamlit
 
    **O que é RAG?**
    *Retrieval-Augmented Generation* combina busca semântica em documentos
    com geração de texto por LLM. O modelo só responde com base nos
    documentos indexados — sem "inventar" informações.
 
    **Documentos indexados:**
    """)
 
    # Listar PDFs indexados
    if os.path.exists("base"):
        pdfs = [f for f in os.listdir("base") if f.endswith(".pdf")]
        for pdf in pdfs:
            st.markdown(f"- 📄 {pdf}")
    else:
        st.markdown("*(pasta base não encontrada)*")
 
    st.divider()
 
    # Exemplos de perguntas
    st.header("💡 Exemplos de perguntas")
    exemplos = [
        "O que é o PLD e para que serve?",
        "O que são os modelos NEWAVE/DECOMP/DESSEM?",
        "Como funciona o processamento dos modelos NEWAVE/DECOMP/DESSEM?",
        "O que é a Função de Custo Futuro?"
    ]
    for ex in exemplos:
        if st.button(ex, use_container_width=True):
            st.session_state.pergunta_exemplo = ex
 
# ──────────────────────────────────────────────
# Interface principal
# ──────────────────────────────────────────────
 
# Campo de entrada
pergunta_default = st.session_state.get("pergunta_exemplo", "")
pergunta = st.text_input(
    "Sua pergunta:",
    value=pergunta_default,
    placeholder="Ex: O que é o PLD?",
    key="input_pergunta"
)
 
col1, col2 = st.columns([1, 5])
with col1:
    enviar = st.button("🔍 Perguntar", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Limpar histórico", use_container_width=False):
        st.session_state.historico = []
        st.rerun()
 
# Processar pergunta
if enviar and pergunta.strip():
    with st.spinner("Buscando nas resoluções..."):
        resultado = responder(pergunta, vectorstore)
 
    # Adicionar ao histórico
    st.session_state.historico.append(resultado)
 
    # Limpar o exemplo após uso
    if "pergunta_exemplo" in st.session_state:
        del st.session_state.pergunta_exemplo
 
# ──────────────────────────────────────────────
# Exibir histórico de respostas
# ──────────────────────────────────────────────
for item in reversed(st.session_state.historico):
    st.divider()
 
    # Pergunta
    st.markdown(f"**🙋 Pergunta:** {item['pergunta']}")
 
    # Resposta
    st.markdown("**🤖 Resposta:**")
    st.markdown(item["resposta"])
 
    # Fontes (expansível)
    with st.expander(f"📚 Ver {len(item['chunks'])} trechos utilizados como contexto"):
        for i, chunk in enumerate(item["chunks"], 1):
            relevancia_pct = f"{chunk['score'] * 100:.0f}%"
            st.markdown(
                f"**Fonte {i}:** `{chunk['fonte']}` | "
                f"Página {chunk['pagina']} | "
                f"Relevância: {relevancia_pct}"
            )
            st.text_area(
                label="Trecho:",
                value=chunk["conteudo"],
                height=120,
                key=f"chunk_{id(item)}_{i}",
                disabled=True
            )
 
# Mensagem inicial se não há histórico
if not st.session_state.historico:
    st.info("👆 Digite uma pergunta acima para começar.")