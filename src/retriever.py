import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class BuscadorSemantico:
    def __init__(self,
                 ruta_chunks="data/processed/chunks.json",
                 ruta_indice="data/processed/indice.faiss"):

        with open(ruta_chunks, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.indice = faiss.read_index(ruta_indice)
        self.modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    def buscar(self, pregunta, k=3):
        vector = self.modelo.encode([pregunta])
        distancias, indices = self.indice.search(vector.astype("float32"), k)

        resultados = []

        for idx in indices[0]:
            resultados.append(self.chunks[idx])

        return resultados
