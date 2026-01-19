"""
nlp_utils.py
------------
NLP leve para Português:
- spaCy para tokenização/lemmatização/remoção de stopwords
- Similaridade TF-IDF "caseira" (rápida e sem dependências extra)

Objectivo:
- Receber uma pergunta do aluno
- Comparar com perguntas guardadas (QAItem)
- Retornar melhor resposta e sugestões

Nota:
- Não usa LLM/Deep Learning.
- Roda bem em computador fraco.
"""

import math
from collections import Counter
import spacy

# Carrega modelo português (pequeno e leve)
# Certifica-te que instalaste: python -m spacy download pt_core_news_sm
NLP = spacy.load("pt_core_news_sm")


def normalize(text: str) -> list[str]:
    """
    Converte texto em lista de termos normalizados.
    - usa lemma quando possível
    - remove pontuação, stopwords e tokens muito curtos
    """
    doc = NLP(text.lower().strip())
    terms = []
    for t in doc:
        if t.is_space or t.is_punct or t.is_stop:
            continue
        lemma = (t.lemma_ or "").strip()
        if not lemma:
            continue
        if len(lemma) < 2:
            continue
        terms.append(lemma)
    return terms


def build_tfidf_vectors(texts: list[str]) -> tuple[list[dict[str, float]], dict[str, float]]:
    """
    Constrói vetores TF-IDF esparsos (dict termo->peso).
    Retorna:
      - lista de vetores (um por texto)
      - idf por termo

    Estratégia:
      TF = contagem / total
      IDF = log((N + 1) / (df + 1)) + 1  (suavizado)
    """
    tokenized = [normalize(t) for t in texts]
    N = max(1, len(tokenized))

    # df: em quantos documentos o termo aparece
    df = Counter()
    for terms in tokenized:
        for term in set(terms):
            df[term] += 1

    idf = {term: (math.log((N + 1) / (d + 1)) + 1.0) for term, d in df.items()}

    vectors = []
    for terms in tokenized:
        tf = Counter(terms)
        total = max(1, sum(tf.values()))
        vec = {}
        for term, c in tf.items():
            vec[term] = (c / total) * idf.get(term, 0.0)
        vectors.append(vec)

    return vectors, idf


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """
    Similaridade cosseno entre dois vetores esparsos.
    """
    if not vec_a or not vec_b:
        return 0.0

    # Produto escalar
    dot = 0.0
    # iterar pelo menor para ser mais rápido
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
    for k, v in vec_a.items():
        dot += v * vec_b.get(k, 0.0)

    # Normas
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def match_question(user_question: str, stored_questions: list[str], top_k: int = 3):
    """
    Faz matching da pergunta do aluno contra a lista de perguntas da BD.
    Retorna:
      - lista de tuplos (index, score) ordenada por score desc
    """
    if not stored_questions:
        return []

    vectors, _ = build_tfidf_vectors(stored_questions + [user_question])
    qa_vecs = vectors[:-1]
    user_vec = vectors[-1]

    scored = [(i, cosine_similarity(user_vec, qa_vecs[i])) for i in range(len(qa_vecs))]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max(1, top_k)]
