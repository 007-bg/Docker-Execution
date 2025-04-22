import os
import subprocess


# Define a basic web search tool that always returns "The sky is beautiful"
async def web_search(query: str) -> str:
    """Search the web for information"""
    print(f"Searching for: {query}")
    return "The sky is beautiful"


async def create_dockerfile(directory: str) -> str:
    """
    Create a simple Dockerfile in the specified directory for a Python application.
    Uses python:3.9-slim as base image, copies all files, and sets CMD to run main.py.

    Args:
        directory: The directory where the Dockerfile will be created

    Returns:
        String with information about the created Dockerfile
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Start building Dockerfile content with fixed base image
    dockerfile_content = ["FROM python:3.9-slim"]

    # Set working directory
    dockerfile_content.append("WORKDIR /app")

    # Copy all files from the directory
    dockerfile_content.append("COPY . /app/")

    # Add pip install if requirements.txt exists
    dockerfile_content.append(
        'RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi'
    )

    # Set CMD to run main.py
    dockerfile_content.append('CMD ["python", "main.py"]')

    # Write content to Dockerfile
    dockerfile_path = os.path.join(directory, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("\n".join(dockerfile_content))

    print(f"Dockerfile created at: {dockerfile_path}")
    return f"Successfully created Dockerfile at {dockerfile_path}:\n\n{open(dockerfile_path).read()}"


async def build_docker_image(directory: str, image_name: str) -> str:
    """
    Build a Docker image from the Dockerfile in the specified directory.

    Args:
        directory: The directory where the Dockerfile is located
        image_name: name for the Docker image

    Returns:
        String with information about the built Docker image
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        return f"Error: Directory '{directory}' does not exist"

    # Check if Dockerfile exists in the directory
    dockerfile_path = os.path.join(directory, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        return f"Error: Dockerfile not found in '{directory}'"

    # Use directory name as image name if not provided
    if image_name is None:
        image_name = os.path.basename(os.path.abspath(directory)).lower()

    # Build the Docker image
    try:
        print(f"Building Docker image '{image_name}' from {dockerfile_path}...")
        result = subprocess.run(
            ["docker", "build", "-t", image_name, directory],
            capture_output=True,
            text=True,
            check=True,
        )

        # Get image ID for confirmation
        image_info = subprocess.run(
            ["docker", "image", "inspect", image_name, "--format", "{{.Id}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        return (
            f"Successfully built Docker image '{image_name}'\n"
            f"Image ID: {image_info.stdout.strip()}\n"
            f"Build output:\n{result.stdout}"
        )

    except subprocess.CalledProcessError as e:
        return f"Error building Docker image: {e.stderr}"


async def run_docker_container(image_name: str) -> str:
    """
    Run a Docker container from the specified image with default settings.
    Shows output in the terminal.

    Args:
        image_name: Name of the Docker image to run

    Returns:
        String with information about the running container
    """
    # Run container in interactive mode with terminal attached (not detached)
    command = ["docker", "run", "-it", image_name]

    try:
        print(f"Running Docker container from image '{image_name}'...")
        print("Container output will display below. Press Ctrl+C to stop.")

        # Run without capture_output to show output directly in terminal
        result = subprocess.run(
            command,
            text=True,
            check=True,
        )

        return "Docker container execution completed."

    except subprocess.CalledProcessError as e:
        return f"Error running Docker container: {e}"
    except KeyboardInterrupt:
        return "Container execution stopped by user."
