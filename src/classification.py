"""
Funciones de clasificacion de la relacion normativa entre dos textos.
Incluye la version zero shot de tres clases (usada como linea base) y
la version de cinco clases con el modelo ajustado con LoRA.
"""

import torch


ETIQUETAS_5CLASES = ["CONTRADICCION", "COMPATIBILIDAD", "ESPECIFICACION", "EXCEPCION", "NO_RELACION"]

MAPEO_5_A_3 = {
    "CONTRADICCION": "contradiction",
    "EXCEPCION": "contradiction",
    "ESPECIFICACION": "entailment",
    "COMPATIBILIDAD": "neutral",
    "NO_RELACION": "neutral",
}


def clasificar_zero_shot(texto_a, texto_b, modelo_nli, max_caracteres=512):
    """Clasifica un par de textos con el modelo NLI multilingue sin ajuste
    fino, en las tres clases nativas de NLI."""
    scores = modelo_nli.predict([[texto_a[:max_caracteres], texto_b[:max_caracteres]]], apply_softmax=True)[0]
    etiquetas = {i: l.lower() for i, l in modelo_nli.config.id2label.items()}
    distribucion = {etiquetas[i]: float(scores[i]) for i in range(len(scores))}
    etiqueta = max(distribucion, key=distribucion.get)
    return etiqueta, distribucion


def clasificar_5clases(texto_a, texto_b, modelo, tokenizer, device, max_length=384):
    """Clasifica un par de textos con el modelo ajustado con LoRA, en las
    cinco clases del proyecto."""
    modelo.eval()
    entrada = tokenizer(
        texto_a, texto_b,
        truncation=True, max_length=max_length, return_tensors="pt",
    ).to(device)
    with torch.no_grad():
        logits = modelo(**entrada).logits
        probabilidades = logits.softmax(dim=-1)[0].cpu().numpy()
    etiqueta = ETIQUETAS_5CLASES[int(probabilidades.argmax())]
    distribucion = {ETIQUETAS_5CLASES[i]: float(probabilidades[i]) for i in range(len(ETIQUETAS_5CLASES))}
    return etiqueta, distribucion
