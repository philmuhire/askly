from app.services.retrieval import search_knowledge
from app.db.main import get_db
from agents import function_tool



@function_tool
async def search_support_knowledge(
    query: str,
) -> str:

    results = await search_knowledge(
        db=get_db,
        organization_id=current_user.organization_id,
        query=query,
        limit=5,
    )

    return "\n\n".join(
        f"""
Source: {document.title}
Page: {chunk.page_number}

{chunk.content}
"""
        for chunk, document, distance in results
    )
