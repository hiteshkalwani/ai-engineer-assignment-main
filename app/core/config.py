from openai import OpenAI
import os
import docker

# Define the OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define the docker client
dockerClient = docker.from_env()

# Define the setup message for client
setup_message = {
    "role": "system",
    "content": "you are a kind helpful programming language assistant",
}
