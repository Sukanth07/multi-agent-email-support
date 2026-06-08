"""Render typed objects into prompt-ready text, shared across agents."""

from support_agent.models.schemas import ResponsePlan, RetrievedDoc


def format_bullets(items: list[str]) -> str:
    """Render a list as a bullet block, or '(none)' when empty."""
    return "\n".join(f"- {item}" for item in items) or "(none)"


def format_documents(docs: list[RetrievedDoc]) -> str:
    """Render retrieved documents as a readable, source-labeled block."""
    if not docs:
        return "(no documents retrieved)"
    return "\n\n".join(f"[{doc.source}] {doc.title}\n{doc.content}" for doc in docs)


def format_plan(plan: ResponsePlan) -> str:
    """Render a response plan as readable text."""
    return (
        f"Goal: {plan.goal}\n"
        f"Must include:\n{format_bullets(plan.must_include)}\n"
        f"Key facts:\n{format_bullets(plan.key_facts)}"
    )
