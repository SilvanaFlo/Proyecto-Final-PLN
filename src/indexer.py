import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def generar_embeddings(ruta_chunks="data/processed/chunks.json",
                        salida_embeddings="data/processed/embeddings.npy",
                        salida_indice="data/processed/indice.faiss"):

    with open(ruta_chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    textos = [chunk["texto"] for chunk in chunks]

    modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    embeddings = modelo.encode(textos, show_progress_bar=True)

    np.save(salida_embeddings, embeddings)

    dimension = embeddings.shape[1]
    indice = faiss.IndexFlatL2(dimension)
    indice.add(embeddings.astype("float32"))

    faiss.write_index(indice, salida_indice)

    return embeddings, indice
