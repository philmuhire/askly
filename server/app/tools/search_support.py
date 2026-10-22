import logging

from agents import RunContextWrapper, function_tool

from app.agents.context import AgentContext
from app.services.retrieval import search_knowledge

logger = logging.getLogger(__name__)


def _clean(text: str) -> str:
    # Stop retrieved content from closing our <source> wrapper early.
    return text.replace("</source", "<\\/source")


def _attr(text: str) -> str:
    return text.replace('"', "'").replace("\n", " ")[:200]


@function_tool
async def search_knowledge_base(ctx: RunContextWrapper[AgentContext], query: str) -> str:
    """Search the organization's internal IT documentation.

    Call this before answering any question about IT systems, policies or
    procedures. You may call it multiple times with different queries.

    Args:
        query: A specific, self-contained search query. Include product names,
            error messages and key terms; resolve pronouns from the conversation.
    """
    app_ctx = ctx.context
    try:
        async with app_ctx.session_factory() as db:
            chunks = await search_knowledge(db, app_ctx.organization_id, query)
    except Exception:
        logger.exception("knowledge search failed")
        return "The documentation search is temporarily unavailable."

    if not chunks:
        return "No relevant documentation found for this query."

    blocks = []
    for chunk in chunks:
        src = app_ctx.register(chunk)
        page = f' page="{src.page_number}"' if src.page_number is not None else ""
        blocks.append(
            f'<source id="{src.id}" title="{_attr(src.title)}"{page}>\n'
            f"{_clean(src.content)}\n</source>"
        )
    return "\n\n".join(blocks)