import os
import re
import json
from pypdf import PdfReader

def extraer_texto_pdf(ruta_pdf):
    reader = PdfReader(ruta_pdf)
    texto = ""

    for pagina in reader.pages:
        contenido = pagina.extract_text()
        if contenido:
            texto += contenido + " "

    return texto

def limpiar_texto(texto):
    texto = re.sub(r'\n+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ.,;:()%-]', '', texto)
    return texto.strip()

def procesar_documentos(carpeta_raw="data/raw", salida="data/processed/documentos_limpios.json"):
    documentos = {}

    for archivo in os.listdir(carpeta_raw):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(carpeta_raw, archivo)
            texto = extraer_texto_pdf(ruta)
            documentos[archivo] = limpiar_texto(texto)

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=4)

    return documentos

def crear_chunks(documentos, tamano=250, salida="data/processed/chunks.json"):
    chunks = []

    for nombre_doc, texto in documentos.items():
        palabras = texto.split()

        for i in range(0, len(palabras), tamano):
            fragmento = " ".join(palabras[i:i+tamano])

            if len(fragmento) > 100:
                chunks.append({
                    "documento": nombre_doc,
                    "texto": fragmento
                })

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)

    return chunks
