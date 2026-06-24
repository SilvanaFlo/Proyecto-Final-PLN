# Importamos la librería Gradio, que permite crear interfaces gráficas
# accesibles desde el navegador para interactuar con modelos o funciones.
import gradio as gr

# Importamos la función principal del agente RAG definida en rag_agent.py.
# Esta función se encargará de procesar las preguntas y devolver respuestas.
from src.rag_agent import responder_pregunta

# Definimos la función que será conectada a la interfaz de Gradio.
# Recibe una pregunta como texto y devuelve la respuesta generada por el agente.
def chat_interface(pregunta):
    return responder_pregunta(pregunta)

# Configuración de la interfaz de Gradio:
# - fn: función que se ejecutará al recibir la entrada del usuario.
# - inputs: tipo de entrada (Textbox en este caso, con 2 líneas y un placeholder).
# - outputs: tipo de salida (texto plano).
# - title: título que aparece en la interfaz.
# - description: texto descriptivo que aparece debajo del título.
demo = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Haz tu pregunta..."),
    outputs="text",
    title="Buscador Semántico Corporativo",
    description="Pregunta sobre contratos o documentos y recibe análisis de riesgos y entidades."
)

# Punto de entrada del programa:
# Si este archivo se ejecuta directamente, se lanza la aplicación en un servidor local.
# Gradio abrirá la interfaz en el navegador en la dirección http://127.0.0.1:7860 por defecto.
if __name__ == "__main__":
    demo.launch()
