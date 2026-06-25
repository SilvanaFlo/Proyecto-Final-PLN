Les parece bien que quede así el README? 

# Proyecto Final PLN - Buscador Semántico Corporativo
Este proyecto implementa un agente RAG (Recuperación + Generación) para analizar documentos corporativos en formato PDF. El sistema permite realizar preguntas en lenguaje natural y obtener respuestas con fragmentos relevantes, entidades extraídas y análisis de riesgos.

## Instalación
1. Clonar el repositorio:
   	```bash
   	git clone <URL-del-repositorio>
   	cd Proyecto-Final-PLN
2.	Crear y activar entorno virtual:
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    .\venv\Scripts\Activate.ps1 # Windows PowerShell
3.	Instalar dependencias:
    pip install -r requirements.txt
4.	Descargar modelo de spaCy:
    python -m spacy download es_core_news_sm

## Ejecución
1.	Procesar documentos PDF:
   python src/ingest.py
3.	Generar embeddings e índice FAISS:
	python src/indexer.py
5.	Lanzar la interfaz:
	python app.py
7.	Abrir en navegador:
	http://127.0.0.1:7860

## Ejemplo de uso
Pregunta:
¿Cuáles son los riesgos mencionados en el contrato X?
Respuesta:
•	Fragmento relevante del documento.
•	Riesgos detectados con categoría, nivel y polaridad.
•	Entidades extraídas (personas, organizaciones, fechas, etc.).

## Dependencias principales
•	gradio
•	faiss-cpu
•	sentence-transformers
•	spacy
•	pypdf
•	numpy

## Enlace al video de presentación
https://canva.link/19k1x1vnpb4vbiv](https://drive.google.com/file/d/1TifKrEiFYgPDBRuwRxXC5BNkhm_PiUz3/view?usp=sharing)
