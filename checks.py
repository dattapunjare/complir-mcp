import json
from pathlib import Path

PRODUCTS_FILE = Path(__file__).parent / "data" / "products.json"

# which rule ID to cite for each market
LABEL_RULE_ID = {"eu": "EU-LAB-1", "india": "IND-LAB-1", "us": "US-LAB-1"}

# label fields each market requires
REQUIRED_FIELDS = {
    "eu": ["net_quantity", "batch_number", "importer_address"],
    "india": ["net_quantity", "batch_number", "importer_address", "mrp"],
    "us": ["net_quantity", "batch_number", "importer_address"],
}

def load_products():
    return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))

def get_product(product_id):
    for p in load_products():
        if p["id"] == product_id:
            return p
    return None

def check_required_fields(product, market):
    gaps = []
    for field in REQUIRED_FIELDS[market]:
        if not product["label"].get(field):
            gaps.append({"rule_id": LABEL_RULE_ID[market], "issue": f"Label is missing '{field}'"})
    return gaps

# which rule IDs to cite for claims, per market
CLAIM_RULE_ID = {
    "eu": {"prohibited": "EU-LAB-2", "unsubstantiated": "EU-LAB-3"},
    "india": {"prohibited": "IND-LAB-2", "unsubstantiated": "IND-LAB-3"},
    "us": {"prohibited": "US-LAB-2", "unsubstantiated": "US-LAB-3"},
}

# words that make a claim a medical claim (simple keyword match)
PROHIBITED_WORDS = ["cure", "treat", "miracle", "hair loss"]

def check_claims(product, market):
    gaps = []
    for claim in product["claims"]:
        text = claim.lower()
        if any(word in text for word in PROHIBITED_WORDS):
            gaps.append({
                "rule_id": CLAIM_RULE_ID[market]["prohibited"],
                "issue": f"Prohibited medical claim: '{claim}'",
            })
        if "clinically proven" in text and not product["has_test_report"]:
            gaps.append({
                "rule_id": CLAIM_RULE_ID[market]["unsubstantiated"],
                "issue": f"Claim '{claim}' has no test report on file",
            })
    return gaps

# safety mark each market requires, and which product categories need it
SAFETY_MARK = {
    "eu": {"mark": "CE", "categories": ["electrical", "toy"], "rule_id": "EU-SAF-1"},
    "india": {"mark": "BIS", "categories": ["electrical", "toy"], "rule_id": "IND-SAF-1"},
    "us": {"mark": "UL", "categories": ["electrical"], "rule_id": "US-SAF-1"},
}

def check_safety_mark(product, market):
    rule = SAFETY_MARK[market]
    if product["category"] in rule["categories"] and rule["mark"] not in product["certifications"]:
        return [{
            "rule_id": rule["rule_id"],
            "issue": f"Missing {rule['mark']} mark for a {product['category']} product",
        }]
    return []

# which rule ID to cite for the small parts warning, per market
SMALL_PARTS_RULE_ID = {"eu": "EU-SAF-2", "india": "IND-SAF-2", "us": "US-SAF-2"}

def check_small_parts_warning(product, market):
    if not product["has_small_parts"]:
        return []
    warnings_text = " ".join(product["label"]["warnings"]).lower()
    if "choking" not in warnings_text:
        return [{
            "rule_id": SMALL_PARTS_RULE_ID[market],
            "issue": "Product has small parts but the label has no choking hazard warning",
        }]
    return []

def check_product(product, market):
    gaps = []
    gaps += check_required_fields(product, market)
    gaps += check_claims(product, market)
    gaps += check_safety_mark(product, market)
    gaps += check_small_parts_warning(product, market)
    return gaps