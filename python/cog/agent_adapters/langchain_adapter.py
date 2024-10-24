from typing import Any, Callable

from langchain.tools import StructuredTool
from langchain.tools.render import render_text_description
from langchain_core.runnables import Runnable
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel


def add_tool(
    name: str,
    desc: str,
    schema: BaseModel,
    func: Callable[..., Any],
    agents: dict[str, Runnable],
) -> None:
    """
    Add a tool to this agent executor and update tool partial variables
    """

    if agents is None:
        return

    if len(agents) == 0:
        return

    runnable = list(agents.values())[0]

    print(f"Adding tool: {name}")
    print(f"schema: {schema}")

    tool = StructuredTool.from_function(
        func=func,
        name=name,
        description=desc,
        args_schema=schema,
        # tags=tags,
    )

    # add the tool to the agent executor and update the partial variables
    _update_agent_tooling_internals(tool, runnable)


def remove_tool(name: str, desc: str, runnable: Runnable) -> None:
    for tool in runnable.tools:
        if tool.name == name and tool.description == desc:
            runnable.tools.remove(tool)


def _update_agent_tooling_internals(tool: StructuredTool, runnable: Runnable) -> None:
    """
    Add the new tool to this agent executor. For langchain agents we
    must update the prompt partial variables to achieve dynamic tool changes.
    """
    if runnable is None:
        return

    runnable.tools.append(tool)

    if "agent" not in runnable.__dict__:
        return

    for _, chain_sequence in runnable.__dict__["agent"].runnable:
        if chain_sequence is None:
            continue

        for component in chain_sequence:
            if hasattr(component, "kwargs"):
                # TODO: handle the case where the component has open-ai-functions kwargs
                component.kwargs = {
                    "tools": [convert_to_openai_tool(t) for t in runnable.tools],
                }

            # check if component has partial variables
            if hasattr(component, "partial_variables"):
                component.partial_variables = {
                    "tools": render_text_description(list(runnable.tools)),
                    "tool_names": ", ".join([t.name for t in runnable.tools]),
                }
