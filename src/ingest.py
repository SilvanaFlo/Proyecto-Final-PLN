# Importamos las librerías necesarias
import os
import re
import json
from pypdf import PdfReader

def extraer_texto_pdf(ruta_pdf):
    """
    Extrae el texto de un archivo PDF.
    - ruta_pdf: ruta al archivo PDF.
    Retorna: texto concatenado de todas las páginas.
    """
    reader = PdfReader(ruta_pdf)
    texto = ""

    # Iteramos sobre cada página y extraemos el contenido
    for pagina in reader.pages:
        contenido = pagina.extract_text()
        if contenido:
            texto += contenido + " "

    return texto

def limpiar_texto(texto):
    """
    Limpia el texto eliminando saltos de línea, espacios múltiples y caracteres no deseados.
    - texto: cadena de entrada.
    Retorna: texto normalizado y limpio.
    """
    texto = re.sub(r'\n+', ' ', texto)  # reemplaza múltiples saltos de línea por un espacio
    texto = re.sub(r'\s+', ' ', texto)  # reemplaza múltiples espacios por uno solo
    texto = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ.,;:()%-]', '', texto)  # elimina caracteres especiales no permitidos
    return texto.strip()

def procesar_documentos(carpeta_raw="data/raw", salida="data/processed/documentos_limpios.json"):
    """
    Procesa todos los documentos PDF en la carpeta indicada.
    - carpeta_raw: carpeta donde se encuentran los archivos PDF originales.
    - salida: archivo JSON donde se guardarán los textos limpios.
    Retorna: diccionario con nombre de archivo y texto limpio.
    """
    documentos = {}

    # Iteramos sobre todos los archivos en la carpeta
    for archivo in os.listdir(carpeta_raw):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(carpeta_raw, archivo)
            texto = extraer_texto_pdf(ruta)
            documentos[archivo] = limpiar_texto(texto)

    # Guardamos los textos procesados en un archivo JSON
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=4)

    return documentos

def crear_chunks(documentos, tamano=250, salida="data/processed/chunks.json"):
    """
    Divide los documentos en fragmentos (chunks) de tamaño fijo.
    - documentos: diccionario con nombre de archivo y texto limpio.
    - tamano: número máximo de palabras por fragmento.
    - salida: archivo JSON donde se guardarán los chunks.
    Retorna: lista de fragmentos con referencia al documento original.
    """
    chunks = []

    # Iteramos sobre cada documento y lo dividimos en fragmentos
    for nombre_doc, texto in documentos.items():
        palabras = texto.split()

        for i in range(0, len(palabras), tamano):
            fragmento = " ".join(palabras[i:i+tamano])

            # Solo guardamos fragmentos suficientemente largos
            if len(fragmento) > 100:
                chunks.append({
                    "documento": nombre_doc,
                    "texto": fragmento
                })

    # Guardamos los fragmentos en un archivo JSON
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)

    return chunks
