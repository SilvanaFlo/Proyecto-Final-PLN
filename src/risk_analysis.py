# Rol 2: análisis de riesgos
# Este módulo aplica reglas lingüísticas y palabras clave para detectar riesgos en documentos corporativos/laborales.

import json
import re
import argparse
import unicodedata
from pathlib import Path

# Lista de reglas de riesgo con categorías, nivel, polaridad y palabras clave asociadas.
# Cada regla define qué términos indican un posible riesgo en el texto.
REGLAS_RIESGO = [
    {
        "categoria": "Confidencialidad y manejo de información",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "confidencial", "información confidencial", "informacion confidencial",
            "información privilegiada", "informacion privilegiada", "divulgación",
            "divulgacion", "revelada", "revelar", "secreto comercial",
            "uso indebido de información", "uso indebido de informacion", "listas de clientes"
        ]
    },
    # ... (otras reglas definidas con la misma estructura)
]

# Diccionario que asigna prioridad numérica a cada nivel de riesgo.
# Se usa para seleccionar el nivel más alto cuando hay múltiples coincidencias.
PRIORIDAD_NIVEL = {
    "Alto": 3,
    "Medio": 2,
    "Bajo": 1,
    "Sin riesgo detectado": 0
}

# Convierte texto a minúsculas y elimina acentos para facilitar la búsqueda de coincidencias.
def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

# Carga el archivo chunks.json generado por el Rol 1 (preprocesamiento de documentos).
def cargar_chunks(ruta_archivo):
    ruta_archivo = Path(ruta_archivo)

    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError("El archivo chunks.json debe contener una lista de fragmentos.")

    return datos

# Divide el texto en oraciones simples usando expresiones regulares.
def dividir_oraciones(texto):
    oraciones = re.split(r"(?<=[.!?])\s+", texto)
    oraciones = [oracion.strip() for oracion in oraciones if oracion.strip()]
    return oraciones

# Busca las reglas de riesgo que aparecen en un fragmento u oración.
def buscar_reglas_en_texto(texto):
    texto_normalizado = normalizar_texto(texto)
    coincidencias = []

    for regla in REGLAS_RIESGO:
        palabras_encontradas = []
        for palabra in regla["palabras_clave"]:
            palabra_normalizada = normalizar_texto(palabra)
            if palabra_normalizada in texto_normalizado:
                palabras_encontradas.append(palabra)

        if palabras_encontradas:
            coincidencias.append({
                "categoria": regla["categoria"],
                "nivel": regla["nivel"],
                "polaridad": regla["polaridad"],
                "palabras_clave": sorted(list(set(palabras_encontradas)))
            })

    return coincidencias

# Selecciona el nivel de mayor prioridad entre las coincidencias encontradas.
def seleccionar_nivel_mayor(coincidencias):
    if not coincidencias:
        return "Sin riesgo detectado"

    nivel_mayor = "Sin riesgo detectado"
    for coincidencia in coincidencias:
        nivel_actual = coincidencia["nivel"]
        if PRIORIDAD_NIVEL[nivel_actual] > PRIORIDAD_NIVEL[nivel_mayor]:
            nivel_mayor = nivel_actual
    return nivel_mayor

# Asigna una polaridad general de acuerdo con el nivel de riesgo.
def asignar_polaridad_por_nivel(nivel):
    if nivel == "Alto":
        return "Negativa"
    elif nivel == "Medio":
        return "Negativa moderada"
    elif nivel == "Bajo":
        return "Neutral preventiva"
    else:
        return "Neutral"

# Detecta riesgos dentro de un texto, analizando oración por oración.
def detectar_riesgos_en_texto(texto):
    oraciones = dividir_oraciones(texto)
    riesgos_detectados = []

    for oracion in oraciones:
        coincidencias = buscar_reglas_en_texto(oracion)
        if coincidencias:
            nivel_general = seleccionar_nivel_mayor(coincidencias)
            polaridad_general = asignar_polaridad_por_nivel(nivel_general)

            categorias = []
            palabras_clave = []
            for coincidencia in coincidencias:
                categorias.append(coincidencia["categoria"])
                palabras_clave.extend(coincidencia["palabras_clave"])

            riesgo = {
                "fragmento_riesgo": oracion,
                "nivel": nivel_general,
                "polaridad": polaridad_general,
                "categorias_riesgo": sorted(list(set(categorias))),
                "palabras_clave": sorted(list(set(palabras_clave)))
            }
            riesgos_detectados.append(riesgo)

    return riesgos_detectados

# Analiza todos los chunks y detecta riesgos en cada uno.
def analizar_chunks(chunks):
    resultados_por_chunk = []
    conteo_por_nivel = {"Alto": 0, "Medio": 0, "Bajo": 0}
    conteo_por_categoria = {}
    total_riesgos_detectados = 0

    for indice, chunk in enumerate(chunks):
        documento = chunk.get("documento", "documento_desconocido")
        texto = chunk.get("texto", "")
        riesgos = detectar_riesgos_en_texto(texto)

        for riesgo in riesgos:
            nivel = riesgo["nivel"]
            if nivel in conteo_por_nivel:
                conteo_por_nivel[nivel] += 1
            for categoria in riesgo["categorias_riesgo"]:
                conteo_por_categoria[categoria] = conteo_por_categoria.get(categoria, 0) + 1

        total_riesgos_detectados += len(riesgos)

        resultados_por_chunk.append({
            "chunk_id": indice,
            "documento": documento,
            "riesgos": riesgos
        })

    resultado_final = {
        "descripcion": "Análisis de riesgos mediante reglas lingüísticas y palabras clave en documentos corporativos/laborales.",
        "resumen": {
            "total_chunks_analizados": len(chunks),
            "total_riesgos_detectados": total_riesgos_detectados,
            "conteo_por_nivel": conteo_por_nivel,
            "conteo_por_categoria": conteo_por_categoria
        },
        "resultados_por_chunk": resultados_por_chunk
    }
    return resultado_final

# Función pública para que el Rol 3 pueda importar el análisis de riesgos.
def analyze_risks(chunks):
    return analizar_chunks(chunks)

# Guarda el análisis de riesgos en un archivo JSON.
def guardar_resultado(resultado, ruta_salida):
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=4)

# Punto de entrada principal para ejecución desde consola.
def main():
    parser = argparse.ArgumentParser(
        description="Análisis de riesgos en documentos corporativos y laborales."
    )
    parser.add_argument(
        "--input",
        default="data/processed/chunks.json",
        help="Ruta del archivo chunks.json generado por el Rol 1."
    )
    parser.add_argument(
        "--output",
        default="data/processed/riesgos.json",
        help="Ruta donde se guardará el archivo riesgos.json."
    )
    args = parser.parse_args()

    chunks = cargar_chunks(args.input)
    resultado = analizar_chunks(chunks)
    guardar_resultado(resultado, args.output)

    print("Análisis de riesgos finalizado correctamente.")
    print(f"Archivo generado: {args.output}")
    print(f"Total de chunks analizados: {resultado['resumen']['total_chunks_analizados']}")
    print(f"Total de riesgos detectados: {resultado['resumen']['total_riesgos_detectados']}")
    print(f"Conteo por nivel: {resultado['resumen']['conteo_por_nivel']}")

# Ejecuta la función principal si el archivo se corre directamente.
if __name__ == "__main__":
    main()
