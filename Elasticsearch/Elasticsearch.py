import requests
import os
import fitz  # pymupdf para leer PDFs
from config import EMBEDDING_API_URL, es, headers


def create_index(index):
    """Función para crear un índice en Elasticsearch."""
    index_name = index

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

def vectorizar_texto(text):
    """Función que utiliza la API de NextAI para vectorizar un texto."""

    body = {
        "texts": [text],
        "model": "LaBSE"
    }

    response = requests.post(EMBEDDING_API_URL, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()['vectors'][0]
    else: 
        print("Error en la solicitud. Código de respuesta:", response.status_code)
        return None

def extract_text_from_pdf(pdf_path):
    """Función que lee un PDF y extrae el texto."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

def index_pdf(pdf_path, index_name="documents"):
    text = extract_text_from_pdf(pdf_path)
    embedding = vectorizar_texto(text)

    if embedding:
        doc = {
            "filename": os.path.basename(pdf_path),
            "content": text,
            "vector": embedding  # Guardamos el embedding generado por la API
        }
        es.index(index=index_name, body=doc)  # Indexamos en Elasticsearch
        print(f"✅ {pdf_path} indexado correctamente")
    else:
        print(f"⚠️ No se pudo indexar {pdf_path}")

def close_connection():
    """Función para cerrar la conexión con Elasticsearch."""
    es.close()
    print("Conexión cerrada con Elasticsearch")

if __name__ == "__main__":
    indice = "textos_prueba"  
    create_index(indice)

    pdf_folder = r"C:\Users\raulc\OneDrive - UNIR\Documentos\ViewNext\MasterVN\Proyecto\Docs"  
    for pdf_file in os.listdir(pdf_folder):
        print(f"Indexando {pdf_file}")
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            index_pdf(pdf_path)

    print("📄 Todos los PDFs han sido indexados en Elasticsearch 🚀")
    close_connection()