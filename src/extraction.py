import json
import re
import argparse
from pathlib import Path

import spacy

#ROL 2- Este script toma como entrada los fragmentos generados por el rol 1.

#funcion 1- el mdelo es_core_news_sm permite detectar entidades nombracas en textos escritos en español.
def cargar_modelo_spacy():

    try:
        # Se intenta cargar el modelo pequeño de español de spaCy.
        nlp = spacy.load("es_core_news_sm")
        return nlp

    except OSError:
        # Si el modelo no existe, se lanza un error claro para el usuario.
        raise OSError(
            "No se encontró el modelo es_core_news_sm. "
            "Instálalo con: python -m spacy download es_core_news_sm"
        )

#funcion 2 cargo los chunks generados por el rol 1
def cargar_chunks(ruta_archivo):
     # Convierte la ruta recibida en un objeto Path para manejarla mejor.
    ruta_archivo = Path(ruta_archivo)

    # Verifica que el archivo realmente exista.
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    # Abre el archivo JSON con codificación UTF-8 para respetar acentos y caracteres en español.
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    # Valida que el JSON contenga una lista.
    # Esto es importante porque el script espera recorrer varios fragmentos.
    if not isinstance(datos, list):
        raise ValueError("El archivo chunks.json debe contener una lista de fragmentos.")

    return datos

#función 3 eliminar elementos repetidos conservando el orden original
def eliminar_duplicados(lista):
     # Conjunto auxiliar para registrar elementos ya vistos.
    vistos = set()

    # Lista final sin elementos repetidos.
    resultado = []

    for elemento in lista:
        # Convierte cada elemento a texto y elimina espacios al inicio y al final.
        elemento = str(elemento).strip()

        # Si el elemento no está vacío y no ha sido visto antes, se agrega.
        if elemento and elemento.lower() not in vistos:
            vistos.add(elemento.lower())
            resultado.append(elemento)

    return resultado

#funcion 4- extrae fechas usando expresiones regulares
def extraer_fechas(texto):
    # Lista de meses en español para detectar fechas escritas con texto.
    meses = (
        "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
        "septiembre|setiembre|octubre|noviembre|diciembre"
    )

    # Patrones de fechas que el programa buscará dentro del texto.
    patrones = [
        # Detecta fechas como: 15 de mayo de 2026.
        rf"\b\d{{1,2}}\s+de\s+({meses})\s+(de\s+)?\d{{4}}\b",

        # Detecta fechas como: mayo de 2026.
        rf"\b({meses})\s+de\s+\d{{4}}\b",

        # Detecta fechas numéricas como: 30/06/2026 o 30-06-2026.
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        # Detecta fechas relacionadas con publicaciones en el Diario Oficial.
        r"\bDOF\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    ]

    fechas = []

    #recorre cada patron y busca coincidencias en el texto
    for patron in patrones:
        coincidencias = re.finditer(patron, texto, flags=re.IGNORECASE)

        # Cada coincidencia encontrada se agrega a la lista de fechas.
        for coincidencia in coincidencias:
            fechas.append(coincidencia.group(0))

    # Se eliminan fechas repetidas antes de regresar el resultado.
    return eliminar_duplicados(fechas)

#Función 5- extrae referencias legales o reglamentarias
def extraer_articulos_legales(texto):
    patrones = [
        # Detecta expresiones como: Artículo 1, Artículo 25, Artículo 47.
        r"\bArtículo\s+\d+[A-Za-z]*\.?",

        # Detecta abreviaturas como: Art. 10.
        r"\bArt\.\s*\d+[A-Za-z]*\.?",

        # Detecta capítulos como: Capítulo Primero.
        r"\bCap[ií]tulo\s+[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+",

        # Detecta fracciones en números romanos como: Fracción IV.
        r"\bFracci[oó]n\s+[IVXLCDM]+",

        # Detecta nombre específico de la ley.
        r"\bLey Federal del Trabajo\b",

        # Detecta nombre específico del reglamento.
        r"\bReglamento Interior de Trabajo\b",

        # Detecta nombre específico del código.
        r"\bCódigo de Ética\b"
    ]

    articulos = []

    # Recorre todos los patrones definidos.
    for patron in patrones:
        coincidencias = re.finditer(patron, texto, flags=re.IGNORECASE)

        # Guarda cada coincidencia encontrada.
        for coincidencia in coincidencias:
            articulos.append(coincidencia.group(0))

    return eliminar_duplicados(articulos)

#función 6- extrae correos electronicos si aparecen en los documentos.
def extraer_correos(texto):
    # Patrón básico para detectar correos electrónicos.
    patron = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"

    # re.findall devuelve todas las coincidencias encontradas.
    correos = re.findall(patron, texto)

    return eliminar_duplicados(correos)


#funcion 7- extrae posibles numeros telefónicos
def extraer_telefonos(texto):
    # Patrón flexible para detectar teléfonos con o sin lada.
    patron = r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{3,4}[\s-]?\d{4}\b"

    telefonos = re.findall(patron, texto)

    return eliminar_duplicados(telefonos)

#función 8- extrae posibles montos economicos
def extraer_montos(texto):
    patrones = [
        # Detecta cantidades con símbolo de pesos.
        r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?",

        # Detecta cantidades escritas como: 1000 pesos.
        r"\b\d+(?:,\d{3})*(?:\.\d{2})?\s?pesos\b",

        # Detecta expresiones como: 15 salarios mínimos.
        r"\b\d+\s?salarios mínimos\b"
    ]

    montos = []

    # Busca coincidencias con cada patrón.
    for patron in patrones:
        coincidencias = re.finditer(patron, texto, flags=re.IGNORECASE)

        for coincidencia in coincidencias:
            montos.append(coincidencia.group(0))

    return eliminar_duplicados(montos)

#funcion 10 - extrae entidades nombradas y datos relevantes del texto
def extraer_entidades(texto, nlp):
     # Procesa el texto con spaCy para detectar entidades nombradas.
    doc = nlp(texto)

    # Listas donde se guardarán las entidades detectadas por spaCy.
    personas = []
    organizaciones = []
    lugares = []
    miscelaneas = []

    # doc.ents contiene las entidades que spaCy encontró en el texto.
    for entidad in doc.ents:
        etiqueta = entidad.label_

        # PER o PERSON representa personas.
        if etiqueta in ["PER", "PERSON"]:
            personas.append(entidad.text)

        # ORG representa organizaciones o instituciones.
        elif etiqueta == "ORG":
            organizaciones.append(entidad.text)

        # LOC o GPE representa lugares, ubicaciones o entidades geopolíticas.
        elif etiqueta in ["LOC", "GPE"]:
            lugares.append(entidad.text)

        # Cualquier otra entidad se guarda como miscelánea.
        else:
            miscelaneas.append(entidad.text)

    # Diccionario final con toda la información extraída.
    entidades = {
        "personas": eliminar_duplicados(personas),
        "organizaciones": eliminar_duplicados(organizaciones),
        "lugares": eliminar_duplicados(lugares),

        # Estas entidades se extraen mediante expresiones regulares.
        "fechas": extraer_fechas(texto),
        "articulos_legales": extraer_articulos_legales(texto),
        "correos": extraer_correos(texto),
        "telefonos": extraer_telefonos(texto),
        "montos": extraer_montos(texto),

        # Entidades detectadas por spaCy que no entraron en las categorías anteriores.
        "otras_entidades": eliminar_duplicados(miscelaneas)
    }

    return entidades

#afuncion 11 - analiza todos los fragmentos del archivo chubks.json
def analizar_chunks(chunks):
    # Carga el modelo de spaCy una sola vez para no hacerlo en cada fragmento.
    nlp = cargar_modelo_spacy()

    # Lista donde se guardará el análisis individual de cada chunk.
    resultados_por_chunk = []

    # Diccionario acumulador para guardar todas las entidades encontradas.
    resumen_global = {
        "personas": [],
        "organizaciones": [],
        "lugares": [],
        "fechas": [],
        "articulos_legales": [],
        "correos": [],
        "telefonos": [],
        "montos": [],
        "otras_entidades": []
    }

    # Recorre todos los chunks del archivo.
    for indice, chunk in enumerate(chunks):
        # Obtiene el nombre del documento.
        # Si no existe la clave, usa "documento_desconocido".
        documento = chunk.get("documento", "documento_desconocido")

        # Obtiene el texto del fragmento.
        # Si no existe la clave, usa una cadena vacía.
        texto = chunk.get("texto", "")

        # Extrae entidades del fragmento actual.
        entidades = extraer_entidades(texto, nlp)

        # Guarda el resultado del chunk actual.
        resultado_chunk = {
            "chunk_id": indice,
            "documento": documento,
            "entidades": entidades
        }

        resultados_por_chunk.append(resultado_chunk)

        # Agrega las entidades del chunk al resumen global.
        for clave in resumen_global:
            resumen_global[clave].extend(entidades.get(clave, []))

    # Elimina duplicados en el resumen global.
    for clave in resumen_global:
        resumen_global[clave] = eliminar_duplicados(resumen_global[clave])

    # Construye el resultado final que se guardará en entidades.json.
    resultado_final = {
        "descripcion": "Extracción de entidades nombradas e información relevante para documentos corporativos/laborales.",
        "total_chunks_analizados": len(chunks),
        "resumen_global": resumen_global,
        "resultados_por_chunk": resultados_por_chunk
    }

    return resultado_final

#funcion 12 - es la funcion auxiliar para integracion con el rol 3
def extract_information(chunks):
     return analizar_chunks(chunks)

#funcion 13- guarda los resultados en formato JSON
def guardar_resultado(resultado, ruta_salida):
    # Convierte la ruta de salida en objeto Path.
    ruta_salida = Path(ruta_salida)

    # Crea la carpeta de salida si todavía no existe.
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    # Guarda el resultado en formato JSON.
    # ensure_ascii=False permite conservar acentos y ñ.
    # indent=4 hace que el archivo sea más legible.
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=4)

#Es la función principal del script
def main():
    # Configura los argumentos que puede recibir el script desde terminal.
    parser = argparse.ArgumentParser(
        description="Extracción de entidades y datos relevantes en documentos corporativos."
    )

    # Argumento que indicar la ruta de entrada.
    parser.add_argument(
        "--input",
        default="data/processed/chunks.json",
        help="Ruta del archivo chunks.json generado por el Rol 1."
    )

    # Argumento opcional para indicar la ruta de salida.
    # Si no se proporciona, genera data/processed/entidades.json.
    parser.add_argument(
        "--output",
        default="data/processed/entidades.json",
        help="Ruta donde se guardará el archivo entidades.json."
    )

    # Lee los argumentos escritos en la terminal.
    args = parser.parse_args()

    # Carga los chunks desde el archivo JSON.
    chunks = cargar_chunks(args.input)

    # Analiza los chunks y extrae entidades.
    resultado = analizar_chunks(chunks)

    # Guarda el resultado en el archivo de salida.
    guardar_resultado(resultado, args.output)

    # Mensajes para confirmar que el proceso terminó correctamente.
    print("Extracción de entidades finalizada correctamente.")
    print(f"Archivo generado: {args.output}")
    print(f"Total de chunks analizados: {resultado['total_chunks_analizados']}")

if __name__ == "__main__":
    main()

