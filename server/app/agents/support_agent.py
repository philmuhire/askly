from datetime import date

from agents import Agent, RunContextWrapper
from agents import ModelSettings

from app.agents.context import AgentContext
from app.agents.instructions import SYSTEM_PROMPT
from app.core.llm import chat_model
from app.tools.search_support import search_knowledge_base


def _instructions(ctx: RunContextWrapper[AgentContext], agent: Agent[AgentContext]) -> str:
    """Dynamic instructions: the static prompt plus per-request facts."""
    return f"{SYSTEM_PROMPT}\nToday's date: {date.today().isoformat()}."


# One module-level instance is fine: all per-request state lives in AgentContext.
# Don't set tool_choice="required" here: it forces a tool call even for "thanks!",
# and errors out when no tools are attached. (If you want a forced first search,
# the SDK resets the choice to "auto" after the first tool call.)
support_agent = Agent[AgentContext](
    name="SupportBot",
    instructions=_instructions,
    tools=[search_knowledge_base],
    model=chat_model,
    model_settings=ModelSettings(temperature=0.2),
)