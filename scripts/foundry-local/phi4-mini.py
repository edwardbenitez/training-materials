# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "foundry-local-sdk",
#     "openai",
# ]
# ///

import openai
from foundry_local import FoundryLocalManager

# By using an alias, the most suitable model will be downloaded
# to your end-user's device.
alias = "phi-4-mini"

# Create a FoundryLocalManager instance. This will start the Foundry
# Local service if it is not already running and load the specified model.
manager = FoundryLocalManager(alias)

# The remaining code uses the OpenAI Python SDK to interact with the local model.
print("==================================")
print(f"endpoint: {manager.endpoint}")
print(f"key: {manager.api_key}")
print(f"model: {manager.get_model_info(alias).id}")
# Configure the client to use the local Foundry service
client = openai.OpenAI(
    base_url="http://127.0.0.1:56272/v1",
    api_key="OPENAI_API_KEY"  # API key is not required for local usage
)

# Set the model to use and generate a streaming response
client = openai.OpenAI(base_url=manager.endpoint, api_key=manager.api_key)
text='every single day is a new day to learn something new and exciting. Embrace the opportunities that come your way and make the most out of each moment.'
response = client.chat.completions.create(
            model="Phi-4-mini-instruct-generic-gpu:5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful translator. Provide a concise translation to spanish.",
                },
                {"role": "user", "content": f"Please translate the following text to spanish:\n\n{text}"},
            ],
        )
print(response.choices[0].message.content)