# Limitaciones

## Tamaño del conjunto de ajuste fino

El conjunto de entrenamiento real construido para el ajuste fino tiene 211 pares, un numero reducido para ajustar un modelo de varios cientos de millones de parametros, incluso usando LoRA. Se uso validacion cruzada estratificada para obtener una estimacion mas confiable dado el tamaño, pero el resultado sigue teniendo una varianza considerable entre particiones.

## Divergencia conceptual en la clase especificacion

En la version zero shot del sistema, la clase de especificacion normativa (mapeada a la clase entailment de NLI) obtuvo un desempeno marcadamente inferior al de las demas clases, con recall cercano a cero. Este patron se observo de forma consistente en distintas configuraciones del clasificador zero shot. La interpretacion mas plausible es que la nocion juridica de especificacion (una norma que detalla o precisa otra sin contradecirla) no coincide completamente con la definicion operacional de entailment (implicacion logica estricta) que usan los modelos NLI convencionales.

Esta interpretacion se ve reforzada por el resultado del ajuste fino supervisado: incluso entrenando el modelo directamente sobre las cinco clases originales del proyecto, con pesos de clase para corregir el desbalance de datos, la clase especificacion obtuvo F1 de 0, sin una sola prediccion correcta sobre 142 casos de evaluacion. En total, esta clase fallo de forma equivalente en cinco configuraciones experimentales independientes (modelo NLI en ingles, modelo NLI multilingue zero shot, gold set balanceado, con segmentacion de texto largo, y ajuste fino supervisado de cinco clases), lo que descarta el desbalance de datos y el ruido de una corrida particular como explicacion suficiente.

Adicionalmente, se identifico una limitacion de diseno en el mapeo de cinco a tres clases usado para comparar contra el modelo zero shot: la relacion de excepcion normativa (por ejemplo, una norma que establece una regla general y otra que exceptua un caso especifico) se mapeo a la clase contradiction de NLI por ser la opcion menos inadecuada entre las tres disponibles, pero en sentido logico estricto una excepcion bien delimitada no constituye una contradiccion entre las normas leidas en conjunto. De manera similar, la relacion entre especificacion y entailment es direccional en la definicion de NLI (la premisa implica la hipotesis, no al reves), mientras que el pipeline no distingue de forma consistente cual de los dos textos del par cumple el rol de norma general y cual el de norma especifica.

## Componente de recuperacion

El articulo correcto se encuentra entre los primeros diez candidatos recuperados en aproximadamente la mitad de los casos evaluados, pero rara vez ocupa exactamente la primera posicion. Esto introduce un costo de error de recuperacion en el sistema completo, medido explicitamente en la evaluacion comparando el desempeno del clasificador contra el par correcto conocido frente a su desempeno contra el candidato realmente recuperado.

Se probaron varias estrategias para reducir este costo (agregacion de multiples candidatos, y tres modelos distintos de reordenamiento de candidatos), sin que ninguna mejorara el resultado del sistema con seleccion simple del primer candidato. Este resultado negativo se documenta en los cuadernos de experimentacion.

## Casos fuera del alcance del sistema

Se identificaron en el gold set original casos que comparan la version derogada de un articulo contra su version vigente tras una reforma legislativa. Determinar la relacion correcta en estos casos requiere informacion sobre la vigencia temporal de cada version del texto, que no es inferible del contenido textual por si solo. Estos casos se excluyeron de la evaluacion principal por estar fuera del alcance de un clasificador que opera unicamente sobre el contenido sincronico de los textos.

## Uso responsable del sistema

La precision obtenida en la clase contradiccion no es suficiente para que el sistema tome decisiones sin supervision. El sistema se propone como una herramienta de apoyo para reducir el espacio de revision manual, priorizando candidatos para que un profesional del derecho confirme o descarte la contradiccion señalada, no como un reemplazo del criterio juridico.
