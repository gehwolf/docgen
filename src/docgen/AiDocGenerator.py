import clang.cindex
import argparse
import sys
from DeclarationInfo import DeclarationInfo
import requests


class AiDocGenerator(object):

    def __init__(self):
        """
        Args:
            host (str): The Ollama host (default: "localhost").
            port (int): The Ollama port (default: 11434).
            model (str): The model to use (e.g., "llama3", "mistral", etc.).
        """
        self.host = "localhost"
        self.port = 11434
        self.model = "llama3.1"

    def _query_ollama(self, prompt: str) -> str:
        """
        Send a prompt to an Ollama instance and return the response.

        Args:
            prompt (str): The input prompt string.

        Returns:
            str: The generated response from Ollama.
        """
        url = f"http://{self.host}:{self.port}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            # Set to True if you want streamed responses (more complex handling)
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.RequestException as e:
            return f"Error communicating with Ollama: {e}"

    def generateFor(self, decl: DeclarationInfo) -> str:
        query = 'I give you the code of a C function and need a docstring for it. The docstring shall use the Napoleon syntax. The content and style of the content shall follow the typical manpage style. So paramter and there value range shall be explained, return vales and there meanig and implications, side effects like setting errno or if resources are returned if caller has to take owner ship and responsibility. Please answer only with the docstring as it shall placed int the code no other additions or comments.'
        query += f"The code to create the docstrng for is as follows: \n```\n{
            func_code}\n```"
        result = query_ollama(query)
        print(f"test case :\n{result}")
        with open(f"out_{func[0]}.txt", "w") as f:
            f.write("query:")
            f.write(query)
            f.write("\n result:")
            f.write(result)

        return result
