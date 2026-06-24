#rol 2 análisis de riesgos
import json
import re
import argparse
import unicodedata
from pathlib import Path


REGLAS_RIESGO = [
    {
        "categoria": "Confidencialidad y manejo de información",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "confidencial",
            "información confidencial",
            "informacion confidencial",
            "información privilegiada",
            "informacion privilegiada",
            "divulgación",
            "divulgacion",
            "revelada",
            "revelar",
            "secreto comercial",
            "uso indebido de información",
            "uso indebido de informacion",
            "listas de clientes"
        ]
    },
    {
        "categoria": "Sanciones, multas y consecuencias legales",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "sanción",
            "sancion",
            "sanciones",
            "multa",
            "multas",
            "penalización",
            "penalizacion",
            "responsabilidad legal",
            "acciones legales",
            "delito",
            "ilícito",
            "ilicito",
            "ilegal",
            "violación",
            "violacion",
            "falta grave"
        ]
    },
    {
        "categoria": "Terminación laboral o rescisión",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "rescisión",
            "rescision",
            "terminación",
            "terminacion",
            "despido",
            "separación",
            "separacion",
            "baja",
            "relación de trabajo",
            "relacion de trabajo"
        ]
    },
    {
        "categoria": "Acoso, violencia o amenazas",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "acoso",
            "sexual",
            "amenaza",
            "amenazas",
            "violencia",
            "intimidación",
            "intimidacion",
            "hostil",
            "ofensiva",
            "presión",
            "presion",
            "arma",
            "armas"
        ]
    },
    {
        "categoria": "Sustancias prohibidas y seguridad personal",
        "nivel": "Alto",
        "polaridad": "Negativa",
        "palabras_clave": [
            "drogas",
            "alcohol",
            "sustancia controlada",
            "sustancias controladas",
            "enervantes",
            "efectos nocivos",
            "trabajo seguro",
            "peligro",
            "vida del personal"
        ]
    },
    {
        "categoria": "Conflicto de intereses",
        "nivel": "Medio",
        "polaridad": "Negativa moderada",
        "palabras_clave": [
            "conflicto de intereses",
            "intereses personales",
            "beneficio personal",
            "beneficio económico",
            "beneficio economico",
            "familiares",
            "amigos",
            "regalos",
            "obsequios",
            "gratificaciones",
            "cortesías",
            "cortesias"
        ]
    },
    {
        "categoria": "Incumplimiento de obligaciones",
        "nivel": "Medio",
        "polaridad": "Negativa moderada",
        "palabras_clave": [
            "incumplimiento",
            "obligación",
            "obligacion",
            "obligaciones",
            "deberá",
            "debera",
            "deberán",
            "deberan",
            "no deberá",
            "no debera",
            "prohibido",
            "no está permitido",
            "no esta permitido"
        ]
    },
    {
        "categoria": "Denuncias, investigaciones y reportes",
        "nivel": "Medio",
        "polaridad": "Negativa moderada",
        "palabras_clave": [
            "denuncia",
            "denuncias",
            "investigación",
            "investigacion",
            "reportado",
            "reportar",
            "notificar",
            "notificación",
            "notificacion",
            "comité de ética",
            "comite de etica",
            "auditoría",
            "auditoria"
        ]
    },
    {
        "categoria": "Seguridad laboral y salud",
        "nivel": "Medio",
        "polaridad": "Negativa moderada",
        "palabras_clave": [
            "seguridad",
            "salud",
            "riesgo",
            "riesgos",
            "actos inseguros",
            "equipo de protección",
            "equipo de proteccion",
            "medidas disciplinarias",
            "instalaciones",
            "accidente"
        ]
    },
    {
        "categoria": "Cumplimiento normativo",
        "nivel": "Bajo",
        "polaridad": "Neutral preventiva",
        "palabras_clave": [
            "ley",
            "leyes",
            "reglamento",
            "reglamentos",
            "normas",
            "políticas",
            "politicas",
            "lineamientos",
            "procedimientos",
            "cumplimiento",
            "código de ética",
            "codigo de etica"
        ]
    },
    {
        "categoria": "Prevención y control interno",
        "nivel": "Bajo",
        "polaridad": "Neutral preventiva",
        "palabras_clave": [
            "prevenir",
            "prevención",
            "prevencion",
            "control interno",
            "medidas de control",
            "recomendaciones",
            "capacitación",
            "capacitacion",
            "difusión",
            "difusion",
            "actualización",
            "actualizacion"
        ]
    }
]


PRIORIDAD_NIVEL = {
    "Alto": 3,
    "Medio": 2,
    "Bajo": 1,
    "Sin riesgo detectado": 0
}

# Convierte texto a minúsculas y elimina acentos para facilitar la búsqueda.
def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

#Carga el archivo chunks.json generado por el Rol 1.
def cargar_chunks(ruta_archivo):
    ruta_archivo = Path(ruta_archivo)

    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError("El archivo chunks.json debe contener una lista de fragmentos.")

    return datos


#divide el texto en oraciones simples
def dividir_oraciones(texto):
    oraciones = re.split(r"(?<=[.!?])\s+", texto)
    oraciones = [oracion.strip() for oracion in oraciones if oracion.strip()]

    return oraciones

#Busca las reglas de riesgo que aparecen en un fragmento u oración.
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


#selecciona  el nivel de mayor prioridad
def seleccionar_nivel_mayor(coincidencias):
    if not coincidencias:
        return "Sin riesgo detectado"

    nivel_mayor = "Sin riesgo detectado"

    for coincidencia in coincidencias:
        nivel_actual = coincidencia["nivel"]

        if PRIORIDAD_NIVEL[nivel_actual] > PRIORIDAD_NIVEL[nivel_mayor]:
            nivel_mayor = nivel_actual

    return nivel_mayor

#Asigna una polaridad general de acuerdo con el nivel de riesgo.
def asignar_polaridad_por_nivel(nivel):
    if nivel == "Alto":
        return "Negativa"
    elif nivel == "Medio":
        return "Negativa moderada"
    elif nivel == "Bajo":
        return "Neutral preventiva"
    else:
        return "Neutral"


#Detecta riesgos dentro de un texto y analiza oracion por oracion para regresar fragmentos mas claros
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

#analiza todos los chunks y detecta riesgos en cada uno
def analizar_chunks(chunks):
    resultados_por_chunk = []

    conteo_por_nivel = {
        "Alto": 0,
        "Medio": 0,
        "Bajo": 0
    }

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


# Aútil para que el Rol 3 pueda importar la función con nombre general
def analyze_risks(chunks):
    return analizar_chunks(chunks)


#guarda el análisis de riesgos en formato JSON
def guardar_resultado(resultado, ruta_salida):
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=4)


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


if __name__ == "__main__":
    main()