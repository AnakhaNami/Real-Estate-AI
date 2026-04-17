import re

def detect_intent(query: str) -> dict:
    q = query.lower()

    intent = {
        "search_projects": False,
        "search_builders": False,
        "search_agents":   False,
        "search_web":      False,
        "search_pdf":      True,
        "city":            None,
        "max_budget":      None,
        "bhk":             None,
        "locality":        None,
    }

    project_words = ["flat", "apartment", "project", "available", "buy",
                     "property", "bhk", "units", "possession", "price",
                     "cost", "budget", "listing", "floor", "room"]
    if any(w in q for w in project_words):
        intent["search_projects"] = True

    builder_words = ["builder", "developer", "company", "construct",
                     "sobha", "confident", "skyline", "puravankara",
                     "asset", "ubl"]
    if any(w in q for w in builder_words):
        intent["search_builders"] = True

    agent_words = ["agent", "broker", "contact", "recommend",
                   "who can help", "find me an agent", "realtor"]
    if any(w in q for w in agent_words):
        intent["search_agents"] = True

    web_words = ["current price", "latest", "today", "2024", "2025",
                 "news", "interest rate", "market", "trend", "recent"]
    if any(w in q for w in web_words):
        intent["search_web"] = True

    cities = {
        "kochi": "Kochi", "ernakulam": "Kochi",
        "kozhikode": "Kozhikode", "calicut": "Kozhikode",
        "thrissur": "Thrissur", "trichur": "Thrissur",
        "thiruvananthapuram": "Thiruvananthapuram",
        "trivandrum": "Thiruvananthapuram",
        "kannur": "Kannur", "kollam": "Kollam",
        "palakkad": "Palakkad", "alappuzha": "Alappuzha"
    }
    for key, value in cities.items():
        if key in q:
            intent["city"] = value
            break

    bhk_match = re.search(r"(\d)\s*bhk", q)
    if bhk_match:
        intent["bhk"] = bhk_match.group(1) + "BHK"

    budget_match = re.search(r"(\d+)\s*lakh", q)
    if budget_match:
        intent["max_budget"] = float(budget_match.group(1))

    return intent