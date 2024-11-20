from typing import Any, Callable

from autogen import ConversableAgent, register_function
from pydantic import BaseModel


def get_workflow(agents: dict[str, ConversableAgent]) -> dict[str, Any]:
    workflow = {"nodes": [], "edges": []}

    caller, executor = get_caller_and_executor(agents)

    # executor will be the root node, likely user_proxy_agent
    if executor:
        workflow["nodes"].append(
            {
                "name": executor.name,
                "description": "Autogen - " + executor.name,
            }
        )

    if caller:
        workflow["nodes"].append(
            {
                "name": caller.name,
                "description": "Autogen - " + caller.name,
            }
        )
        workflow["edges"].append(
            {
                "source": executor.name,
                "target": caller.name,
            }
        )
        if "tools" in caller.llm_config:
            for tool in caller.llm_config["tools"]:
                workflow["nodes"].append(
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                    }
                )
                workflow["edges"].append(
                    {
                        "source": caller.name,
                        "target": tool["function"]["name"],
                    }
                )
                

    return workflow


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
