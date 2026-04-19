# Arquivo para gerar o banco de dados vetorial

import pydantic
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

pasta_base = "base"

def criar_db():
    # Carregar Documentos
    documentos = carregar_documentos()
    # Dividir os documentos em pedaços de texto (chunks)
    chunks = dividir_chunks(documentos)
    # Vetorizar os chunks com os processos de embedding
    vetorizar_chunks(chunks)

def carregar_documentos():
    carregador = PyPDFDirectoryLoader(pasta_base)
    documentos = carregador.load()
    return documentos

def dividir_chunks(documentos):
    separador_docs = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap = 500,
        length_function = len,
        add_start_index = True
    )
    chunks = separador_docs.split_documents(documentos)
    print(f"Quantidade de chunks criados: {len(chunks)}")
    return chunks


def vetorizar_chunks(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model = "gemini-embedding-001", # modelo de embedding do Gemini
        google_api_key = os.getenv("GOOGLE_API_KEY")
    )
    db = Chroma.from_documents(chunks, embeddings, persist_directory="db")
    print("Banco de Dados criado!")

criar_db()