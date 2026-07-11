"""
Despliegue minimo del sistema. Levanta una interfaz donde se ingresa un
articulo o fragmento de consulta y se devuelve la lista de articulos
relacionados del corpus, la relacion normativa clasificada para cada
uno, y la evidencia textual que sustenta esa clasificacion.

Ejecucion local:
    python deploy/app.py

Requiere los archivos de datos en data/ y el modelo ajustado con LoRA
guardado en la ruta indicada en RUTA_MODELO_LORA.
"""

import json
import sys
from pathlib import Path

import gradio as gr
import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src import IndiceRecuperacion, analizar_articulo, formatear_reporte

RUTA_CORPUS = "data/corpus_cc_peru.json"
RUTA_MODELO_LORA = "sinai1carlos/mdeberta-lora-nli-juridico-peru-5clases"
MODELO_BASE = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# QDRANT LOCAL: CREAR / REUTILIZAR ÍNDICE
import gc
from pathlib import Path

#LIMPIAR CLIENTE PREVIO
print("Limpiando cliente previo...")
try:
    if 'qdrant' in globals():
        qdrant.close()
        del qdrant
        print("   Cliente cerrado")
except Exception as e:
    print(f"   {e}")

# Forzar garbage collection
gc.collect()

# Eliminar archivo de lock
try:
    lock_file = Path("./qdrant_storage_despliegue") / '.lock'
    if lock_file.exists():
        lock_file.unlink()
        print("   Lock file eliminado")
    else:
        print("   No había lock file")
except Exception as e:
    print(f"   Error al eliminar lock: {e}")
    
def cargar_recursos():
    with open(RUTA_CORPUS, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)

    qdrant_client = QdrantClient(path="./qdrant_storage_despliegue")
    coleccion = "corpus_despliegue"
    if not qdrant_client.collection_exists(coleccion):
        qdrant_client.create_collection(
            collection_name=coleccion,
            vectors_config=VectorParams(size=embedding_model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
        )
        vectores = embedding_model.encode([a["texto"] for a in corpus], normalize_embeddings=True, batch_size=32)
        qdrant_client.upsert(collection_name=coleccion, points=[
            PointStruct(id=i, vector=vectores[i].tolist(), payload={"articulo": corpus[i]["articulo"], "texto": corpus[i]["texto"]})
            for i in range(len(corpus))
        ])

    indice = IndiceRecuperacion(corpus, embedding_model, qdrant_client, coleccion)

    tokenizer = AutoTokenizer.from_pretrained(RUTA_MODELO_LORA)
    modelo_base = AutoModelForSequenceClassification.from_pretrained(MODELO_BASE, num_labels=5, ignore_mismatched_sizes=True)
    modelo = PeftModel.from_pretrained(modelo_base, RUTA_MODELO_LORA).to(DEVICE)

    return indice, modelo, tokenizer


def responder(texto_consulta, indice, modelo, tokenizer):
    if not texto_consulta or not texto_consulta.strip():
        return "Ingrese el texto de un articulo o fragmento de consulta."
    resultados = analizar_articulo(texto_consulta, indice, modelo, tokenizer, DEVICE, top_k=5)
    return formatear_reporte(texto_consulta, resultados)


def main():
    indice, modelo, tokenizer = cargar_recursos()

    with gr.Blocks(title="Deteccion de contradicciones normativas") as demo:
        gr.Markdown("# Deteccion de relaciones normativas en el Codigo Civil Peruano")
        gr.Markdown("Ingrese el texto de un articulo o consulta juridica para encontrar articulos relacionados y su tipo de relacion normativa.")
        entrada = gr.Textbox(label="Articulo o consulta", lines=4)
        boton = gr.Button("Analizar")
        salida = gr.Textbox(label="Resultado", lines=20)
        boton.click(
            fn=lambda texto: responder(texto, indice, modelo, tokenizer),
            inputs=entrada,
            outputs=salida,
        )

    demo.launch(share=True)


if __name__ == "__main__":
    main()
