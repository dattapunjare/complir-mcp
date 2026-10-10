import re
from pathlib import Path
from rank_bm25 import BM25Okapi

DOCS_DIR = Path(__file__).parent / "data" / "regulations"

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())

def load_chunks():
    chunks = []
    for f in sorted(DOCS_DIR.glob("*.md")):
        market = f.stem.split("_")[0]          # eu_labelling.md -> "eu"
        for section in re.split(r"\n(?=## )", f.read_text(encoding="utf-8")):
            if section.startswith("## "):
                chunks.append({"market": market, "source": f.name, "text": section.strip()})
    return chunks

CHUNKS = load_chunks()
INDEX = BM25Okapi([tokenize(c["text"]) for c in CHUNKS])

def search(question, market=None, k=3):
    scores = INDEX.get_scores(tokenize(question))
    ranked = sorted(zip(scores, CHUNKS), key=lambda x: x[0], reverse=True)
    hits = []
    for score, chunk in ranked:
        if score <= 0:
            continue
        if market and chunk["market"] != market.lower():
            continue
        hits.append(chunk)
        if len(hits) == k:
            break
    return hits