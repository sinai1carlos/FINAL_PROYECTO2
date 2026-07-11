"""
Pipeline completo: recibe un articulo o fragmento de consulta, recupera
los articulos mas relacionados del corpus, clasifica la relacion con
cada uno, y arma una explicacion con la evidencia textual usada.
"""

from .classification import clasificar_5clases, ETIQUETAS_5CLASES


def analizar_articulo(texto_consulta, indice_recuperacion, modelo, tokenizer, device, top_k=5):
    """Devuelve, para un articulo o fragmento de consulta, la lista de
    articulos relacionados encontrados junto con la relacion normativa
    clasificada y la evidencia textual correspondiente."""

    candidatos = indice_recuperacion.recuperar_hibrido(texto_consulta, top_k=top_k)

    resultados = []
    for candidato in candidatos:
        etiqueta, distribucion = clasificar_5clases(
            texto_consulta, candidato["texto"], modelo, tokenizer, device
        )
        resultados.append({
            "articulo_relacionado": candidato["articulo"],
            "texto_relacionado": candidato["texto"],
            "score_recuperacion": candidato["score"],
            "relacion_normativa": etiqueta,
            "confianza": distribucion[etiqueta],
            "distribucion_completa": distribucion,
            "evidencia": (
                f"El articulo {candidato['articulo']} fue recuperado con un puntaje de "
                f"similitud de {candidato['score']:.3f} y clasificado como '{etiqueta}' "
                f"con una confianza de {distribucion[etiqueta]:.3f}."
            ),
        })

    resultados.sort(key=lambda r: -r["confianza"] if r["relacion_normativa"] == "CONTRADICCION" else 0)
    return resultados


def formatear_reporte(texto_consulta, resultados):
    """Arma un texto legible con el resultado del analisis, para mostrar
    en la interfaz de despliegue."""
    lineas = [f"Consulta: {texto_consulta}", ""]
    for r in resultados:
        lineas.append(f"Articulo {r['articulo_relacionado']}: {r['relacion_normativa']}")
        lineas.append(f"  {r['evidencia']}")
        lineas.append(f"  Texto: {r['texto_relacionado'][:200]}")
        lineas.append("")
    return "\n".join(lineas)
