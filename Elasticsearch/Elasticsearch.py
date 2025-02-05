import requests
import os
import re
import fitz  # pymupdf para leer PDFs
import numpy as np
from config import EMBEDDING_API_URL, es, headers


def create_index(index):
    """Función para crear un índice en Elasticsearch."""
    index_name = index

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

def vectorizar_texto(text, max_chars=150000):
    """Función que utiliza la API de NextAI para vectorizar un texto, dividiéndolo si excede el límite de caracteres."""

    text = limpiar_texto(text)
    if not text:
        print("Error: El texto quedó vacío después de la limpieza")
        return None
    
    # Si el texto es más corto que el máximo, procesarlo directamente
    if len(text) <= max_chars:
        body = {
            "texts": [text],
            "model": "LaBSE"
        }
        try:
            response = requests.post(EMBEDDING_API_URL, headers=headers, json=body)
            if response.status_code == 200:
                return response.json()['vectors'][0]
            else:
                print(f"Error en la solicitud. Código de respuesta: {response.status_code}")
                return None
        except Exception as e:
            print(f"Excepción al hacer la solicitud: {str(e)}")
            return None
    
    # Dividir el texto en segmentos usando puntos como separadores
    segments = []
    current_text = text
    while len(current_text) > max_chars:
        # Buscar el último punto antes del límite
        split_index = current_text.rfind('.', 0, max_chars)
        
        if split_index == -1:
            # Si no hay punto, buscar el último espacio
            split_index = current_text.rfind(' ', 0, max_chars)
            if split_index == -1:
                # Si no hay espacio, cortar en el límite
                split_index = max_chars
        
        segment = current_text[:split_index].strip()
        if segment:
            segments.append(segment)
        current_text = current_text[split_index + 1:].strip()
    
    if current_text:
        segments.append(current_text)
    
    print(f"Texto dividido en {len(segments)} segmentos")
    
    # Vectorizar cada segmento
    vectors = []
    for i, segment in enumerate(segments, 1):
        print(f"\nProcesando segmento {i}/{len(segments)}")
        print(f"Longitud del segmento: {len(segment)} caracteres")
        
        # Asegurarse de que el segmento esté limpio
        segment = limpiar_texto(segment)
        if not segment:
            print(f"Segmento {i} quedó vacío después de la limpieza")
            continue
            
        body = {
            "texts": [segment],
            "model": "LaBSE"
        }
        
        try:
            response = requests.post(EMBEDDING_API_URL, headers=headers, json=body)
            if response.status_code == 200:
                vectors.append(response.json()['vectors'][0])
                print(f"✅ Segmento {i} procesado correctamente")
            else:
                print(f"❌ Error en segmento {i}. Código: {response.status_code}")
                
                # Intentar dividir el segmento si sigue siendo muy largo
                if len(segment) > max_chars // 2:
                    print("Intentando dividir el segmento...")
                    subsegments = [segment[j:j + max_chars // 2] for j in range(0, len(segment), max_chars // 2)]
                    for subseg in subsegments:
                        subseg = limpiar_texto(subseg)
                        if subseg:
                            body["texts"] = [subseg]
                            response = requests.post(EMBEDDING_API_URL, headers=headers, json=body)
                            if response.status_code == 200:
                                vectors.append(response.json()['vectors'][0])
                                print(f"✅ Subsegmento procesado correctamente")
                
        except Exception as e:
            print(f"Error en segmento {i}: {str(e)}")
            continue
    
    if not vectors:
        print("❌ No se pudo vectorizar ningún segmento")
        return None
    
    # Calcular el vector promedio de los segmentos
    return np.mean(vectors, axis=0).tolist()


def limpiar_texto(texto):
    """
    Función auxiliar para limpiar y formatear el texto.
    """
    # Reemplazar múltiples espacios y saltos de línea con un solo espacio
    texto = re.sub(r'\s+', ' ', texto)
    
    # Eliminar caracteres no imprimibles excepto espacios normales
    texto = ''.join(char for char in texto if char.isprintable() or char == ' ')
    
    # Eliminar espacios al inicio y final
    texto = texto.strip()
    
    # Asegurarse de que el texto no esté vacío
    if not texto:
        return None
        
    return texto

def extract_text_from_pdf(pdf_path):
    """Función que lee un PDF y extrae el texto."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

def index_pdf(pdf_path, index_name="documents"):
    text = extract_text_from_pdf(pdf_path)
    print(f"Longitud del texto extraído: {len(text)} caracteres")
    
    # Verificar caracteres especiales en el texto completo
    special_chars = set(char for char in text[:1000] if not char.isprintable())
    if special_chars:
        print(f"Caracteres especiales encontrados en el texto: {special_chars}")

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