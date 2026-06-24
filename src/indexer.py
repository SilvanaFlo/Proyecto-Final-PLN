# Importamos las librerías necesarias
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Nombre del modelo de embeddings que se utilizará para representar los textos
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def generar_embeddings(ruta_chunks="data/processed/chunks.json",
                        salida_embeddings="data/processed/embeddings.npy",
                        salida_indice="data/processed/indice.faiss"):
    """
    Función que genera embeddings a partir de los fragmentos (chunks) y construye un índice FAISS.
    - ruta_chunks: archivo JSON con los fragmentos de texto preprocesados.
    - salida_embeddings: archivo .npy donde se guardarán los embeddings generados.
    - salida_indice: archivo .faiss donde se guardará el índice FAISS.
    Retorna:
    - embeddings: matriz numpy con los vectores generados.
    - indice: objeto FAISS con el índice construido.
    """

    # Cargar los fragmentos desde el archivo JSON
    with open(ruta_chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Extraer únicamente el texto de cada fragmento
    textos = [chunk["texto"] for chunk in chunks]

    # Inicializar el modelo de embeddings
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    # Generar embeddings para todos los textos
    # show_progress_bar=True muestra una barra de progreso durante el cálculo
    embeddings = modelo.encode(textos, show_progress_bar=True)

    # Guardar los embeddings en un archivo .npy para uso posterior
    np.save(salida_embeddings, embeddings)

    # Crear un índice FAISS con distancia euclidiana (L2)
    dimension = embeddings.shape[1]  # número de dimensiones de los vectores
    indice = faiss.IndexFlatL2(dimension)

    # Agregar los embeddings al índice (convertidos a float32)
    indice.add(embeddings.astype("float32"))

    # Guardar el índice FAISS en archivo
    faiss.write_index(indice, salida_indice)

    return embeddings, indice
