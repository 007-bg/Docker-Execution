import asyncio
import os

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

# Import tools from tools.py
from tools import create_dockerfile, build_docker_image, run_docker_container


def get_normalized_folder_path():
    """
    Prompt user for a folder path and normalize it for Windows.
    Handles paths with or without quotes and normalizes path separators.

    Returns:
        str: Normalized folder path
    """
    path = input("Please enter the folder path: ")

    # Remove quotes if present
    path = path.strip().strip("\"'")

    # Normalize path separators for Windows
    path = os.path.normpath(path)

    # Create the directory if it doesn't exist
    if not os.path.exists(path):
        create = input(f"Directory {path} doesn't exist. Create it? (y/n): ")
        if create.lower() == "y":
            try:
                os.makedirs(path, exist_ok=True)
                print(f"Created directory: {path}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                return get_normalized_folder_path()  # Try again
        else:
            return get_normalized_folder_path()  # Try again

    return path


async def custom_input() -> str:
    """Custom input function that allows collecting folder paths"""
    user_input = input(">>> ")

    # Check if user wants to create a Dockerfile
    if (
        "create dockerfile" in user_input.lower()
        or "generate dockerfile" in user_input.lower()
    ):
        print(
            "\nTo create a Dockerfile, I'll need the folder path where your application is located."
        )
        folder_path = get_normalized_folder_path()
        return f"{user_input} in directory: {folder_path}"

    return user_input


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
        tools=[create_dockerfile, build_docker_image, run_docker_container],
        system_message="You are a Docker expert assistant with access to Docker containerization tools. You can: 1) Create Dockerfiles for applications - use the directory path provided by users and ask about the application structure, dependencies, and requirements to create optimal configurations; 2) Build Docker images from existing Dockerfiles - specify directory and image name; 3) Run Docker containers from images - configure options like container name, port mappings, volume mounts, and environment variables. Use these tools to help users containerize and run their applications.",
    )

    user_proxy = UserProxyAgent("user_proxy", input_func=input)

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("END")

    # Create the team.
    team = RoundRobinGroupChat(
        [tool_using_agent, user_proxy], termination_condition=termination
    )

    user_input = await custom_input()
    # Run the conversation and stream to the console.
    stream = team.run_stream(task=user_input)
    # Use asyncio.run(...) when running in a script.
    await Console(stream)


if __name__ == "__main__":
    asyncio.run(main())
