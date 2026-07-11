# Deteccion automatica de contradicciones normativas en textos juridicos peruanos mediante RAG e inferencia de lenguaje natural

Proyecto 2, curso CC0C2 - Procesamiento de Lenguaje Natural.

## Problema

El Codigo Civil Peruano esta compuesto por miles de articulos que pueden guardar distintos tipos de relacion normativa entre si: contradiccion, compatibilidad, especificacion, excepcion o ausencia de relacion. Determinar esta relacion hoy requiere revision manual por parte de un profesional del derecho. Este proyecto construye y evalua un sistema que recupera articulos relacionados y clasifica automaticamente el tipo de relacion entre ellos.

Pregunta tecnica evaluada: dado un articulo de consulta, que tan bien puede un sistema de recuperacion mas un clasificador de lenguaje natural identificar el tipo de relacion normativa con un articulo relacionado, y que factores (idioma del modelo, ajuste fino, tamaño del retriever) afectan ese desempeno.

## Estructura del repositorio

```
data/         corpus, dataset de entrenamiento y gold set de evaluacion
notebooks/    cuadernos tecnicos ejecutables
src/          codigo fuente reutilizable (recuperacion, clasificacion, pipeline)
deploy/       script de despliegue minimo
docs/         documentacion tecnica, arquitectura y limitaciones
results/      metricas, tablas y evidencias de los experimentos
```

## Datos

- `data/corpus_cc_peru.json`: 2135 articulos del Codigo Civil Peruano, con metadatos de tema legal.
- `data/dataset_5clases_entrenamiento.json`: 211 pares de entrenamiento, construidos sobre articulos reales del corpus, en las 5 clases del proyecto.
- `data/gold_dataset_5clases_evaluacion.json`: 142 pares de evaluacion, anotados en las 5 clases, sin superposicion con el conjunto de entrenamiento.

Ver `data/README.md` para el detalle de como se construyo cada archivo.

## Instalacion

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Los cuadernos de entrenamiento con LoRA requieren GPU. Se ejecutaron en Google Colab con GPU T4 gratuita.

## Ejecucion

1. `notebooks/comparacion_rag_nli_3clases.ipynb`: pipeline de recuperacion (BM25, denso, hibrido) mas clasificacion NLI zero shot, evaluado como linea base del sistema.
2. `notebooks/lora_baseline_ingles_fallido.ipynb`: primer intento de ajuste fino con LoRA sobre un modelo NLI en ingles y un dataset sintetico. Se documenta como parte del proceso, con analisis de por que fallo.
3. `notebooks/lora_5clases_multilingue.ipynb`: ajuste fino con LoRA sobre un modelo NLI multilingue, con el dataset de 211 pares reales. Es la variante propuesta del proyecto.

Cada cuaderno contiene instrucciones de subida de datos y es ejecutable de principio a fin en Colab.

## Linea base y variante propuesta

- Linea base 1: similitud de coseno entre pares de texto, sin componente de inferencia.
- Linea base 2: clasificador NLI multilingue zero shot, sin ajuste fino.
- Variante propuesta: el mismo clasificador NLI multilingue, con ajuste fino LoRA sobre 211 pares reales del dominio.

Los tres se evaluan sobre el mismo gold set de 142 pares, para que la comparacion sea directa.

## Metricas

Precision, recall y F1 por clase, exactitud global, Recall@k y Precision@k del componente de recuperacion, porcentaje de citas correctas, e intervalos de confianza por bootstrap dado el tamano moderado del gold set. Ver `results/README.md` para las tablas completas.

## Despliegue minimo

`deploy/app.py` implementa una interfaz simple: se ingresa un articulo o fragmento de consulta, el sistema recupera los articulos mas relacionados del corpus, clasifica la relacion con cada uno, y devuelve la explicacion con el articulo citado como evidencia. Instrucciones de ejecucion en `deploy/README.md`.

## Video

Enlace al video de exposicion: PENDIENTE

## Limitaciones

Ver `docs/limitaciones.md` para la discusion completa. En resumen: el conjunto de entrenamiento de 211 pares es pequeno para ajuste fino, la clase de especificacion normativa presenta una divergencia conceptual con la nocion de entailment de NLI, y el componente de recuperacion no siempre ubica el articulo correcto en la primera posicion.

## Relacion con los cuadernos del curso

- **Cuaderno 15 (Ajuste fino de Transformers con PyTorch y Hugging Face)**: es la base metodologica directa del componente de clasificacion de este proyecto. Ese cuaderno entrena un modelo de clasificacion de 5 clases sobre BERT (tokenizacion, `DataLoader`, bucle de entrenamiento, evaluacion), que es exactamente el mismo tipo de tarea que resuelve `notebooks/lora_5clases_multilingue.ipynb`: clasificacion de secuencias en 5 clases, con la diferencia de que aqui se reemplaza la cabeza de clasificacion de un modelo NLI en lugar de partir de un encoder generico.

- **Cuaderno 16 (Tecnicas avanzadas de ajuste fino)**: aporta directamente la tecnica de PEFT/LoRA usada en el proyecto, incluyendo la logica de adaptar un modelo grande entrenando solo una fraccion pequena de parametros. La seccion de metodos de subconjuntos de ese cuaderno (como decidir que datos usar cuando no se puede entrenar con todo el dataset) es relevante para la discusion de este proyecto sobre el tamano reducido del conjunto de entrenamiento (211 pares) y su efecto en el desempeno.

- **Cuaderno 22 (Agentes LLM: herramientas, memoria, RAG y multiagentes)**: la seccion de RAG como herramienta de un agente es la base conceptual del modulo de recuperacion de este proyecto (BM25, denso e hibrido), que cumple el mismo rol: acotar el espacio de busqueda antes de que un componente de razonamiento (aqui, el clasificador NLI) procese el contenido recuperado.

- **Cuaderno 14 (LLMs causales, instruction tuning, alineamiento y agentes)**: la seccion de metodologia de evaluacion para investigacion (matriz de experimentos, intervalos de confianza por bootstrap, registro de errores y analisis cualitativo) es la que se sigue directamente en el diseno experimental de este proyecto: todas las metricas de F1 reportadas incluyen intervalo de confianza al 95 por ciento por bootstrap, y cada resultado negativo (chunking, agregacion multi candidato, reranking) se documenta con su propio analisis de por que no funciono, en lugar de omitirse.

- **Cuaderno 20 (Entrenamiento de alineacion y razonamiento con RLHF)**: la discusion sobre alucinaciones y la necesidad de fundamentar las respuestas de un sistema en evidencia verificable es la motivacion conceptual de por que el pipeline de este proyecto exige que toda clasificacion venga acompanada del articulo recuperado como evidencia citable, en lugar de una etiqueta sin sustento textual.

