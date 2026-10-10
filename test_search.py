import rag

question = "toy small parts warning"

for market in ["eu", "india", "us"]:
    print("=== MARKET:", market)
    for h in rag.search(question, market):
        print(h["source"], "|", h["text"][:80].replace("\n", " "))
    print()