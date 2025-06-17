import os
import json
from typing import List, Dict, Any
import numpy as np

# Load environment variables for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import openai

def get_query_embedding(query: str, model: str = "text-embedding-3-large") -> List[float]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment or .env file.")
    response = openai.embeddings.create(input=[query], model=model)
    return response.data[0].embedding

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

def search_doc_knowledge(
    user_query: str,
    doc_knowledge: List[Dict[str, Any]],
    embedding_fn=get_query_embedding,
    threshold: float = 0.50,  # Lowered to be practical
    top_k: int = 5
) -> List[Dict[str, Any]]:
    user_emb = np.array(embedding_fn(user_query))
    scored_sections = []
    for entry in doc_knowledge:
        doc_emb = np.array(entry.get("embedding", []))
        if doc_emb.size == 0:
            continue
        score = cosine_similarity(user_emb, doc_emb)
        scored_sections.append((score, entry))

    scored_sections.sort(reverse=True, key=lambda x: x[0])

    # Debug: print top similarity scores for transparency
    print("\nTop 5 similarity scores:")
    for idx, (score, entry) in enumerate(scored_sections[:5]):
        print(f"{idx+1}. Score: {score:.4f}, Section: {entry.get('section')}")

    # Return only those above threshold
    filtered_results = [
        {"score": score, **entry}
        for score, entry in scored_sections[:top_k]
        if score >= threshold
    ]
    # If none above threshold, return top_k with a warning
    if not filtered_results and scored_sections:
        print("\n[INFO] No results above threshold. Returning top matches anyway.\n")
        filtered_results = [
            {"score": score, **entry}
            for score, entry in scored_sections[:top_k]
        ]
    return filtered_results

if __name__ == "__main__":
    user_question = input("Enter your question: ").strip()
    doc_path = "leavebot/data/combined_doc_knowledge.json"

    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"Doc knowledge file not found: {doc_path}")

    with open(doc_path, "r", encoding="utf-8") as f:
        doc_knowledge = json.load(f)

    results = search_doc_knowledge(user_question, doc_knowledge, threshold=0.50, top_k=5)

    if results:
        for result in results:
            print(f"\nMatched Section: {result.get('section', 'N/A')} (Score: {result['score']:.3f})\n")
            print(result.get('text', 'No text found.'))
    else:
        print("\nNo relevant policy found. Try rephrasing your question or contact HR.")
