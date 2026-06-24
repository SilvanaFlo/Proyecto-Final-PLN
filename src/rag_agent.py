# Rol 3: agente RAG (Recuperación + Generación)
# Este módulo integra los componentes de búsqueda semántica (Rol 1),
# extracción de entidades (Rol 2) y análisis de riesgos (Rol 2),
# para responder preguntas en lenguaje natural.

from src.retriever import BuscadorSemantico      # Importa el buscador semántico basado en FAISS y embeddings
from src.extraction import extract_information   # Importa la función de extracción de entidades
from src.risk_analysis import analyze_risks      # Importa la función de análisis de riesgos

# Crear instancia del buscador semántico
# Este objeto se encargará de recuperar fragmentos relevantes según la pregunta
buscador = BuscadorSemantico()

def responder_pregunta(pregunta: str) -> str:
    """
    Función principal del agente RAG.
    Recibe una pregunta en texto, recupera fragmentos relevantes,
    extrae entidades y analiza riesgos, y finalmente construye una respuesta.
    """
    print(f" Procesando pregunta: {pregunta}")
    fragmentos = buscador.buscar(pregunta)  # Recupera fragmentos relevantes usando el buscador semántico
    print(f" Se recuperaron {len(fragmentos)} fragmentos.")

    resultados = []
    for frag in fragmentos:
        print(f"Analizando fragmento: {frag['texto'][:60]}...")

        # Entidades (Rol 2 de extracción)
        # Se aplica la función de extracción sobre el fragmento
        entidades_result = extract_information([frag])
        entidades = entidades_result["resultados_por_chunk"][0]["entidades"]

        # Riesgos (Rol 2 de análisis)
        # Se aplica el análisis de riesgos sobre el fragmento
        riesgos_result = analyze_risks([frag])
        riesgos = riesgos_result["resultados_por_chunk"][0]["riesgos"]

        # Se guarda el resultado combinado de cada fragmento
        resultados.append({
            "texto": frag["texto"],
            "entidades": entidades,
            "riesgos": riesgos
        })

    # Construcción de la respuesta final en lenguaje natural
    respuesta = f"Pregunta: {pregunta}\n\n"
    for r in resultados:
        respuesta += f"Fragmento: {r['texto']}\n"
        if r["riesgos"]:
            # Se listan los riesgos encontrados con sus atributos
            for riesgo in r["riesgos"]:
                respuesta += (
                    f"- Riesgo: {', '.join(riesgo['categorias_riesgo'])} "
                    f"| Nivel: {riesgo['nivel']} "
                    f"| Polaridad: {riesgo['polaridad']}\n"
                )
        if r["entidades"]:
            # Se listan las entidades extraídas, agrupadas por tipo
            for tipo, lista in r["entidades"].items():
                if lista:
                    respuesta += f"  {tipo.capitalize()}: {', '.join(lista)}\n"
        respuesta += "\n"

    return respuesta

# Bloque de ejecución directa
# Permite probar el agente desde consola sin necesidad de la interfaz gráfica
if __name__ == "__main__":
    pregunta = "¿Cuáles son los riesgos mencionados en el contrato X?"
    print(responder_pregunta(pregunta))
