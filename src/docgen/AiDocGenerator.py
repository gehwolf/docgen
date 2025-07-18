import clang.cindex
import argparse
import sys
import time
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

    def _loadSourceCode(self, decl: DeclarationInfo):
        func_code = ''
        source_file = decl.file
        start_line = decl.line - 1
        end_line = decl.line

        if decl.definition is not None:
            source_file = decl.definition.file
            start_line = decl.definition.start_line - 1
            end_line = decl.definition.end_line

        with open(source_file, 'r') as f:
            source_lines = f.readlines()
            func_lines = source_lines[start_line: end_line]
            func_code = ''.join(func_lines)

        return func_code

    def generateFor(self, decl: DeclarationInfo) -> str:
        query = 'I give you the code of a C++ function and need a docstring for it. The docstring shall use doxygen format. The content and style of the content shall follow the typical manpage style. So paramter and there value range shall be explained, return vales and there meanig and implications, side effects like setting errno or if resources are returned if caller has to take owner ship and responsibility. Please answer only with the docstring as it shall placed int the code no other additions or comments. Please only answer with the plain doxgen comment no code repetition or comments from your side'

        func_code = self._loadSourceCode(decl)
        query += f"The code to create the docstrng for is as follows: \n```\n{
            func_code}\n```"

        start_time = time.time()
        result = self._query_ollama(query)
        end_time = time.time()
        execution_time = end_time - start_time

        # print(f"test case :\n{result}")
        # result = "TBD"
        with open(f"out_{decl.name}.txt", "w") as f:
            f.write("query:")
            f.write(query)
            f.write(f"\n result in ({execution_time:.4f}):")
            f.write(result)

        return result
