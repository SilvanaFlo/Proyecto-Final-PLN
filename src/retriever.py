# Importamos las librerías necesarias
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Nombre del modelo de embeddings que se utilizará para representar las preguntas y fragmentos
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class BuscadorSemantico:
    """
    Clase que implementa un buscador semántico usando FAISS y SentenceTransformers.
    - Carga los fragmentos (chunks) procesados desde un archivo JSON.
    - Carga el índice FAISS previamente generado.
    - Convierte las preguntas en embeddings y busca los fragmentos más relevantes.
    """

    def __init__(self,
                 ruta_chunks="data/processed/chunks.json",
                 ruta_indice="data/processed/indice.faiss"):
        """
        Constructor de la clase.
        - ruta_chunks: ruta al archivo JSON con los fragmentos preprocesados.
        - ruta_indice: ruta al archivo FAISS con el índice vectorial.
        """
        # Cargar los fragmentos desde el archivo JSON
        with open(ruta_chunks, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        # Cargar el índice FAISS desde archivo
        self.indice = faiss.read_index(ruta_indice)

        # Inicializar el modelo de embeddings
        self.modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    def buscar(self, pregunta, k=3):
        """
        Busca los fragmentos más relevantes para una pregunta.
        - pregunta: texto de la consulta del usuario.
        - k: número de fragmentos relevantes a devolver (por defecto 3).
        Retorna: lista de fragmentos (diccionarios) que coinciden semánticamente.
        """
        # Convertir la pregunta en vector de embeddings
        vector = self.modelo.encode([pregunta])

        # Realizar la búsqueda en el índice FAISS
        distancias, indices = self.indice.search(vector.astype("float32"), k)

        resultados = []
        # Recuperar los fragmentos correspondientes a los índices encontrados
        for idx in indices[0]:
            resultados.append(self.chunks[idx])

        return resultados
