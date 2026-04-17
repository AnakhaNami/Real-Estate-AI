import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))
from groq import Groq
from retriever import load_vectorstore, hybrid_search
from firebase_db import (get_user, save_message, get_history,
                         search_projects, search_builders, search_agents,
                         projects_to_text, builders_to_text, agents_to_text,
                         init_db)
from websearch import web_search
from intent   import detect_intent

client    = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL     = "llama-3.1-8b-instant"
_vs_cache = None

def get_vectorstore():
    global _vs_cache
    if _vs_cache is None:
        _vs_cache = load_vectorstore()
    return _vs_cache

def gather_context(query: str, user) -> dict:
    intent  = detect_intent(query)
    context = {}

    # 1 — PDF RAG (always)
    pdf_docs = hybrid_search(query, get_vectorstore(), top_k=4)
    context["pdf"] = "\n\n".join([d.page_content for d in pdf_docs]) if pdf_docs else ""

    # 2 — Projects from Firebase
    if intent["search_projects"]:
        projects = search_projects(
            city       = intent.get("city") or (user.city if user else None),
            max_budget = intent.get("max_budget") or (user.budget_lakhs if user else None),
            bhk        = intent.get("bhk") or (f"{user.bedrooms}BHK" if user else None),
        )
        context["projects"] = projects_to_text(projects)
    else:
        context["projects"] = ""

    # 3 — Builders from Firebase
    if intent["search_builders"]:
        builders = search_builders(city=intent.get("city"))
        context["builders"] = builders_to_text(builders)
    else:
        context["builders"] = ""

    # 4 — Agents from Firebase
    if intent["search_agents"]:
        agents = search_agents(city=intent.get("city") or (user.city if user else None))
        context["agents"] = agents_to_text(agents)
    else:
        context["agents"] = ""

    # 5 — Web search (only when needed)
    if intent["search_web"] or not context["pdf"]:
        context["web"] = web_search(query)
    else:
        context["web"] = ""

    return context, intent

def build_prompt(query, context, user, history) -> list:
    profile = ""
    if user:
        profile = (f"User: {user.name} | City: {user.city} | "
                   f"Budget: Rs.{user.budget_lakhs} lakhs | "
                   f"Looking for: {user.bedrooms}BHK")

    history_text = "\n".join(
        [f"{m.role.upper()}: {m.message}" for m in history]
    ) if history else ""

    ctx_parts = []
    if context.get("pdf"):
        ctx_parts.append(f"[KNOWLEDGE BASE]\n{context['pdf']}")
    if context.get("projects"):
        ctx_parts.append(f"[AVAILABLE PROJECTS]\n{context['projects']}")
    if context.get("builders"):
        ctx_parts.append(f"[BUILDERS]\n{context['builders']}")
    if context.get("agents"):
        ctx_parts.append(f"[AGENTS]\n{context['agents']}")
    if context.get("web"):
        ctx_parts.append(f"[WEB SEARCH]\n{context['web']}")

    full_context = "\n\n".join(ctx_parts)

    system = f"""You are PropAssist, an expert AI real estate advisor for Kerala, India.
You have access to a legal knowledge base, a live database of Kerala builders/agents/projects, and web search.

RULES:
- Answer in clear friendly conversational English
- Use Indian format: lakhs, crores, Rs.
- When listing projects mention price, location, builder, availability
- When recommending agents mention experience, rating, phone number
- Always be honest if information is not available
- Never invent prices, RERA numbers, or contact details

{f"USER PROFILE: {profile}" if profile else ""}
{f"HISTORY:{chr(10)}{history_text}" if history_text else ""}

{full_context}"""

    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": query}
    ]

def chat(query: str, user_id=None):
    user     = get_user(user_id) if user_id else None
    history  = get_history(user_id) if user_id else []
    context, intent = gather_context(query, user)
    messages = build_prompt(query, context, user, history)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1500,
    )
    answer = response.choices[0].message.content

    if user_id:
        save_message(user_id, "user", query)
        save_message(user_id, "assistant", answer)

    # Return string source labels — never Document objects
    sources = []
    if context.get("pdf"):      sources.append("PDF Knowledge Base")
    if context.get("projects"): sources.append("Project Database")
    if context.get("builders"): sources.append("Builder Database")
    if context.get("agents"):   sources.append("Agent Database")
    if context.get("web"):      sources.append("Web Search")

    return answer, sources

if __name__ == "__main__":
    init_db()
    print("PropAssist — Kerala Real Estate AI")
    print("Type 'quit' to exit\n")
    while True:
        q = input("You: ").strip()
        if not q: continue
        if q.lower() == "quit": break
        answer, sources = chat(q, user_id=None)
        print(f"\nPropAssist: {answer}")
        print(f"\n[Sources: {', '.join(sources)}]\n")
        print("-" * 60)