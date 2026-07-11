"""
Funciones de recuperacion de articulos: lexica (BM25), densa (embeddings)
e hibrida. Se usan tanto en el pipeline de linea base como en el modulo
de despliegue.
"""

import numpy as np
from rank_bm25 import BM25Okapi


class IndiceRecuperacion:
    def __init__(self, corpus, embedding_model, qdrant_client, collection_name):
        self.corpus = corpus
        self.embedding_model = embedding_model
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name

        self.articulo_por_numero = {str(a["articulo"]): a for a in corpus}
        self.articulo_por_indice = {i: corpus[i] for i in range(len(corpus))}

        tokens = [self._tokenizar(a["texto"]) for a in corpus]
        self.bm25 = BM25Okapi(tokens)

    @staticmethod
    def _tokenizar(texto):
        return texto.lower().split()

    def recuperar_denso(self, texto, top_k=10, excluir_articulo=None):
        vector = self.embedding_model.encode(texto, normalize_embeddings=True).tolist()
        resultados = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k + 2,
            with_payload=True,
        ).points
        candidatos = [
            {"articulo": r.payload["articulo"], "texto": r.payload["texto"], "score": round(r.score, 4)}
            for r in resultados
            if not excluir_articulo or r.payload["articulo"] != excluir_articulo
        ]
        return candidatos[:top_k]

    def recuperar_bm25(self, texto, top_k=10, excluir_articulo=None):
        scores = self.bm25.get_scores(self._tokenizar(texto))
        resultado = []
        for indice in np.argsort(scores)[::-1]:
            articulo = self.articulo_por_indice[indice]
            if excluir_articulo and str(articulo["articulo"]) == str(excluir_articulo):
                continue
            resultado.append({
                "articulo": str(articulo["articulo"]),
                "texto": articulo["texto"],
                "score": round(float(scores[indice]), 4),
            })
            if len(resultado) == top_k:
                break
        return resultado

    def recuperar_hibrido(self, texto, top_k=10, excluir_articulo=None, alpha=0.6):
        densos = self.recuperar_denso(texto, top_k=top_k * 2, excluir_articulo=excluir_articulo)
        lexicos = self.recuperar_bm25(texto, top_k=top_k * 2, excluir_articulo=excluir_articulo)

        score_denso = {r["articulo"]: r["score"] for r in densos}
        max_lexico = max((r["score"] for r in lexicos), default=1.0) + 1e-10
        score_lexico = {r["articulo"]: r["score"] / max_lexico for r in lexicos}

        articulos = set(score_denso) | set(score_lexico)
        combinados = [
            {
                "articulo": a,
                "texto": self.articulo_por_numero.get(a, {}).get("texto", ""),
                "score": round(alpha * score_denso.get(a, 0) + (1 - alpha) * score_lexico.get(a, 0), 4),
            }
            for a in articulos
            if self.articulo_por_numero.get(a)
        ]
        combinados.sort(key=lambda x: -x["score"])
        return combinados[:top_k]
