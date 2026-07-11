# Despliegue

`app.py` levanta una interfaz web simple (Gradio) que recibe el texto de un articulo o consulta juridica y devuelve los articulos relacionados encontrados en el corpus, junto con la relacion normativa clasificada para cada uno y la evidencia textual correspondiente.

## Ejecucion

Desde la raiz del repositorio, con las dependencias instaladas y el modelo ajustado con LoRA disponible en `notebooks/lora_5clases_multilingue` (generado por el cuaderno de entrenamiento):

```
python deploy/app.py
```

La primera ejecucion indexa el corpus completo en una base de datos vectorial local, lo que puede tardar varios minutos. Las ejecuciones posteriores reutilizan el indice ya construido.

`demo.launch(share=True)` genera un enlace publico temporal ademas del enlace local, util para dejar evidencia de que el despliegue funciona sin necesidad de acceso a la maquina donde corre.

## Evidencia de despliegue

Agregar en esta carpeta una captura de pantalla de la interfaz en funcionamiento (`evidencia_despliegue.jpeg`), con al menos un ejemplo de consulta y su resultado.
