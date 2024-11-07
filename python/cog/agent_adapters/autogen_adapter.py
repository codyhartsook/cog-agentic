from typing import Any, Callable

from autogen import ConversableAgent, register_function
from pydantic import BaseModel

from ..schema import RemotePredictor


def get_tools(agent: ConversableAgent) -> list[RemotePredictor]:
    tools = []

    if (
        hasattr(agent, "llm_config")
        and agent.llm_config
        and "tools" in agent.llm_config
    ):
        for tool in agent.llm_config["tools"]:
            # create a remote predictor object from the tool
            remote_predictor = RemotePredictor(
                metadata={
                    "name": tool["function"]["name"],
                    "namespace": "unknown",
                    "description": tool["function"]["description"],
                },
                spec={},
            )

            tools.append(remote_predictor)

    return tools


def add_tool(
    name: str,
    desc: str,
    schema: BaseModel,
    func: Callable[..., Any],
    agents: dict[str, ConversableAgent],
) -> None:
    """
    Add a tool to this agent executor and update tool partial variables
    """

    if len(agents) < 2:
        return

    print(f"Adding tool: {name}")

    caller, executor = get_caller_and_executor(agents)

    register_function(
        func,  # The function to be registered.
        caller=caller,  # The caller agent can call the calculator.
        executor=executor,  # The executor agent can execute the calculator.
        name=name,  # The name of the tool.
        description=desc,  # The description of the tool.
    )

    num_tools = len(caller.llm_config["tools"])
    print(f"Agent now has {num_tools} tools")


def get_caller_and_executor(
    agents: dict[str, ConversableAgent],
) -> [ConversableAgent, ConversableAgent]:
    caller = None
    executor = None

    for name, agent in agents.items():
        # check if agent has attribute llm_config
        if hasattr(agent, "llm_config") and agent.llm_config:
            print("setting caller to", name)
            caller = agent
        if caller is not None and agent != caller:
            print("setting executor to", name)
            executor = agent
            break

    return caller, executor


def remove_tool(
    name: str,
    desc: str,
    agents: dict[str, ConversableAgent],
) -> None:
    caller, _ = get_caller_and_executor(agents)

    if (
        hasattr(caller, "llm_config")
        and caller.llm_config
        and "tools" in caller.llm_config
    ):
        try:
            num_tools = len(caller.llm_config["tools"])
            caller.update_tool_signature(name, is_remove=True)
            print(f"Agent now has {num_tools-1} tools")
        except Exception as e:
            print(f"Error removing tool {name}: {e}")
    else:
        print("Agent now has 0 tools")
