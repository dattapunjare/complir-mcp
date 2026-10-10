from mcp.server.fastmcp import FastMCP
import rag
import checks
mcp = FastMCP("complir-compliance")

@mcp.tool()
def search_regulations(question: str, market: str = "") -> str:
    """Search the compliance rule documents and return only the most relevant rule sections.
    Use this when asked what a rule or regulation requires.
    question: plain-language question. market: optional, one of 'eu', 'india', 'us'."""
    hits = rag.search(question, market or None, k=3)
    if not hits:
        return "No relevant sections found."
    return "\n\n---\n\n".join(f"(source: {h['source']})\n{h['text']}" for h in hits)

@mcp.tool()
def list_products() -> str:
    """List all products in the catalog with their id, name, category and target markets.
    Use this first when you need a product id before checking a product."""
    lines = []
    for p in checks.load_products():
        lines.append(f"{p['id']}: {p['name']} ({p['category']}), markets: {', '.join(p['target_markets'])}")
    return "\n".join(lines)

@mcp.tool()
def check_product_against_market(product_id: str, market: str) -> str:
    """Check one product's label and claims against one market's compliance rules.
    Use this when asked whether a product can be sold in a market.
    product_id: e.g. 'P001' (use list_products to find ids). market: one of 'eu', 'india', 'us'.
    Returns a list of gaps, each with the rule id it breaks."""
    market = market.lower()
    if market not in ("eu", "india", "us"):
        return "Unknown market. Use one of: eu, india, us."
    product = checks.get_product(product_id)
    if product is None:
        return f"No product with id '{product_id}'. Use list_products to see valid ids."
    gaps = checks.check_product(product, market)
    if not gaps:
        return f"{product['name']} ({market}): no gaps found by the automated checks."
    lines = [f"{product['name']} ({market}): {len(gaps)} gap(s) found"]
    for g in gaps:
        lines.append(f"- [{g['rule_id']}] {g['issue']}")
    return "\n".join(lines)

@mcp.tool()
def compliance_gap_report(product_id: str) -> str:
    """Create a draft compliance gap report for one product across all of its target markets.
    Use this when asked for a full pre-launch review or report on a product.
    product_id: e.g. 'P001' (use list_products to find ids).
    The report is a DRAFT and must be reviewed and signed off by a compliance officer."""
    product = checks.get_product(product_id)
    if product is None:
        return f"No product with id '{product_id}'. Use list_products to see valid ids."
    lines = [
        f"DRAFT COMPLIANCE GAP REPORT: {product['name']} ({product['id']})",
        "Status: NOT APPROVED. Needs compliance officer review and sign-off.",
        "",
    ]
    total = 0
    for market in product["target_markets"]:
        gaps = checks.check_product(product, market)
        total += len(gaps)
        lines.append(f"Market: {market.upper()} - {len(gaps)} gap(s)")
        for g in gaps:
            lines.append(f"  - [{g['rule_id']}] {g['issue']}")
        lines.append("")
    lines.append(f"Total gaps: {total}")
    lines.append("Automated checks only. A human must verify each gap before any launch decision.")
    return "\n".join(lines)

@mcp.resource("complir://coverage")
def coverage() -> str:
    """List the markets and rule documents this server covers."""
    docs = {}
    for c in rag.CHUNKS:
        key = (c["market"], c["source"])
        docs[key] = docs.get(key, 0) + 1
    lines = ["Complir rule coverage (mock rules, not real law):"]
    for (market, source), count in sorted(docs.items()):
        lines.append(f"- {market}: {source} ({count} rules)")
    return "\n".join(lines)

@mcp.prompt()
def pre_launch_review(product_id: str) -> str:
    """Run a pre-launch compliance review for one product."""
    return (
        f"Run a pre-launch compliance review for product {product_id}.\n"
        "1. Call compliance_gap_report to get the draft gaps for every target market.\n"
        "2. For each gap, call search_regulations with the rule topic to quote the exact rule text.\n"
        "3. Summarise the gaps by market, citing the rule IDs.\n"
        "4. State clearly that this is a DRAFT and a compliance officer must review and sign off "
        "before any launch decision. Do not say the product is approved."
    )

if __name__ == "__main__":
    mcp.run()