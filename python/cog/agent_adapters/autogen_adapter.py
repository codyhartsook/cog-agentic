from typing import Any, Callable

from autogen import ConversableAgent, register_function
from pydantic import BaseModel


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

    if agents is None:
        return

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

    print(f"Agent now has {len(caller.llm_config["tools"])} tools")

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
    caller: ConversableAgent,
    executor: ConversableAgent,
) -> None:
    caller.update_tool_signature(name, is_remove=True)
    # remove from executor?

    print(f"Agent now has {len(caller.llm_config['tools'])} tools")
