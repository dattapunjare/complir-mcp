# Complir Compliance MCP Server

An MCP server that helps a retailer's compliance team check whether a physical product can be sold in a given market. It searches rule documents, checks a product against a market's rules, and returns a cited, draft list of gaps for a human to review.

## 1. Company
Complir builds AI-powered compliance software for physical products. It helps retailers and brands launch and sell products across countries without manually checking every label, document and regulation. Its users are compliance, quality and sourcing teams at companies that sell across borders, and the pitch is often described as "Vanta for physical products".

## 2. Problem
Before a product launches in a new country, someone has to answer one question: "Can we sell this product in this market, and what is missing?" Today that means searching long regulation documents and comparing them by hand with the product's label, claims and certificates. It is slow, and a missed rule can mean a blocked shipment or a recall.

This server gives an AI assistant a safe way to answer that question:

it finds only the relevant rule sections instead of loading whole documents,
it checks a product's data against a market's rules,
it lists each gap together with the rule ID it breaks, so every finding can be verified,
it marks the result as a draft, so a compliance officer still makes the decision.

Who it is for: the compliance team of a retailer that uses Complir (a customer of the company). Complir's own team could also use it for demos and support.

## 3. Tools, resources and prompts

| Type | Name | What it does | Why it is this type |
|---|---|---|---|
| Tool | `search_regulations(question, market)` | Searches the rule documents and returns only the top 3 relevant rule sections (RAG inside the tool). | The AI decides when it needs a rule, and the answer depends on the question. |
| Tool | `list_products()` | Lists the catalog with id, name, category and target markets. | Lets the AI find a product id from a name. |
| Tool | `check_product_against_market(product_id, market)` | Runs the automated checks and returns gaps with rule IDs. | An action with inputs, so it is a tool. |
| Tool | `compliance_gap_report(product_id)` | Runs the checks for every target market and returns a report marked DRAFT / NOT APPROVED. | Needs a human sign-off before any decision. |
| Resource | `complir://coverage` | Lists the markets and rule documents covered, with rule counts. | Fixed reference information the user can attach to a chat. |
| Prompt | `pre_launch_review(product_id)` | A 4-step review script: get the report, quote each rule, summarise, state it is a draft. | A reusable instruction the user picks, so weaker models follow the right steps. |

Tool names are plain verbs and the descriptions say when to use each tool and what each argument means, so a weaker model can choose correctly.

Checks in `checks.py`: required label fields, prohibited medical claims, unsubstantiated claims (no test report), CE/BIS/UL safety marks, and the toy small-parts warning. These are simple keyword and field checks, which is enough for mock data. A real system would need much better language checking.

## 4. How to run
Requirements: Windows, Python, uv, and an MCP host (Claude Desktop or VS Code with GitHub Copilot).

Clone the repo and open the folder in a terminal.
Install packages: uv sync. The mcp package is pinned to 1.x (mcp[cli]<2), because FastMCP was renamed in version 2.

1. Clone the repo and open the folder in a terminal.
2. Install packages: `uv sync`. The `mcp` package is pinned to version 1.x (`mcp[cli]<2`), because `FastMCP` was renamed in 2.x.
3. Start the server directly to check it runs: `uv run python server.py` (stop with Ctrl+C).
4. Test the search: `uv run python test_search.py`
5. Measure tokens: `uv run python scripts/measure_tokens.py`

## 5. Host comparison

| | Claude Desktop | VS Code Copilot |
|---|---|---|
| Config | `mcpServers` in `claude_desktop_config.json`; restart the app to reload | `servers` in `.vscode/mcp.json`, with a Start link in the file |
| Tool choice | Picked `search_regulations` on its own from a plain question. For the shampoo question it called `list_products`, then `check_product_against_market`, then `search_regulations`. | With built-in file read and search tools on, an auto-routed smaller model ignored the MCP tool and searched the workspace files instead. It used `search_regulations` only after I disabled those built-in tools. |
| Permissions | Runs the tools without a prompt in my tests | Asks permission for each call ("Allow in this Session") |
| Speed | Fast | The first attempt took over a minute (6 steps) |
| Prompts and resources | Both shown under + → Connectors → "Add from complir" (Pre launch review, Coverage) | TODO: note what you see in VS Code, if anything |


## 6. Workflow
- **Trigger:** a retailer wants to launch a product in a new market.
- **Before:** product data entry. The product's claims, label fields and certifications are recorded (here in `data/products.json`).
- **During:** the server finds the relevant rules, checks the product, and produces a draft gap report with rule IDs. The `pre_launch_review` prompt runs these steps in order.
- **After:** a compliance officer reviews every gap and signs off. The report is marked DRAFT / NOT APPROVED, and the server never says a product is approved.
- **Human in the loop:** the server finds and cites. A person makes the launch decision.
- **stdio vs HTTP:** I used **stdio** for the demo because the host starts the server itself on one machine, so there is no network setup and no open port. A team sharing one server would need **streamable HTTP**, so several people can connect to one deployed server with authentication. I only ran stdio in this project (TODO: add a note here if you test HTTP).

## 7. Token counts: 


## 8. Screenshots


