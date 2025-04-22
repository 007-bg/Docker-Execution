import asyncio
import os

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console


# Define a basic web search tool that always returns "The sky is beautiful"
async def web_search(query: str) -> str:
    """Search the web for information"""
    print(f"Searching for: {query}")
    return "The sky is beautiful"


async def main():
    # Your async code goes here
    print("Hello from async main!")

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.environ["GEMINI_API_KEY"],
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
        },
    )

    # Create the agents for round-robin chat
    print("\n=== Round Robin Group Chat ===")
    # Demonstrating tool usage with AssistantAgent
    tool_using_agent = AssistantAgent(
        name="tool_assistant",
        model_client=model_client,
        tools=[web_search],
        system_message="Use tools to solve tasks when needed.",
    )
    user_proxy = UserProxyAgent(
        "user_proxy", input_func=input
    )  # Use input() to get user input from console.

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("APPROVE")

    # Create the team.
    team = RoundRobinGroupChat(
        [tool_using_agent, user_proxy], termination_condition=termination
    )

    # Run the conversation and stream to the console.
    stream = team.run_stream(task="Write a 4-line poem about the ocean.")
    # Use asyncio.run(...) when running in a script.
    await Console(stream)


if __name__ == "__main__":
    asyncio.run(main())
