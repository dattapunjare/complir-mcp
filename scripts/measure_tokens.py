import sys
from pathlib import Path

# let this script import rag.py from the project folder above scripts\
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rag
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count(text):
    return len(enc.encode(text))

# approach 1: dump every rule document into the prompt
full_dump = "\n\n".join(
    f.read_text(encoding="utf-8") for f in sorted(rag.DOCS_DIR.glob("*.md"))
)
full_tokens = count(full_dump)

print(f"Rule documents: {len(list(rag.DOCS_DIR.glob('*.md')))} files, {len(rag.CHUNKS)} chunks")
print(f"Full dump of all documents: {full_tokens} tokens\n")

questions = [
    ("What label fields are required in the EU?", "eu"),
    ("Can a shampoo say clinically proven to stop hair loss in India?", "india"),
    ("What warning does a toy with small parts need in the US?", "us"),
]

for question, market in questions:
    hits = rag.search(question, market, k=3)
    returned = "\n\n---\n\n".join(f"(source: {h['source']})\n{h['text']}" for h in hits)
    tokens = count(returned)
    saved = 100 * (full_tokens - tokens) / full_tokens
    print(f"Q: {question} [{market}]")
    print(f"   chunks returned: {len(hits)}, tokens: {tokens}, saved vs full dump: {saved:.0f}%")