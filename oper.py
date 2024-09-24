from time import sleep
import ell
from openai import OpenAI

LOCAL_MODEL = "llama3.1:latest"
LOCAL_URL = "http://localhost:11434/v1"
ft = {}
ft['time'] = 2
ollama_local_client = OpenAI(base_url=LOCAL_URL, api_key='ollama')
ell.config.verbose = True
ell.config.register_model(LOCAL_MODEL, ollama_local_client)

# for LOLz we hardcode the answer in the system prompt
@ell.simple (model=LOCAL_MODEL, client=ollama_local_client)
def stawberry_letter_counter():
    """You are an advanced strawberry letter counter. You are highly skilled in finding how many letter 'r' are in the word strawberry. The answer is always 3. Answer as if you are robot with squeaks and bleeps."""
    return f"How many letter r's are in the word strawberry?"

# chain of thought. hat tip @MrDragonFox
@ell.simple (model=LOCAL_MODEL, client=ollama_local_client)
def chain_of_thought (question:list[str]):
  """        You are an AI assistant that uses a Chain of Thought (CoT) approach with reflection to answer queries. Follow these steps:

      1. Think through the problem step by step within the <thinking> tags.
      2. Reflect on your thinking to check for any errors or improvements within the <reflection> tags.
      3. Make any necessary adjustments based on your reflection.
      4. Provide your final, concise answer within the <output> tags.

      Important: The <thinking> and <reflection> sections are for your internal reasoning process only.
      Do not include any part of the final answer in these sections.
      The actual response to the query must be entirely contained within the <output> tags.

      Use the following format for your response:
      <thinking>
      [Your step-by-step reasoning goes here. This is your internal thought process, not the final answer.]
      <reflection>
      [Your reflection on your reasoning, checking for errors or improvements]
      </reflection>
      [Any adjustments to your thinking based on your reflection]
      </thinking>
      <output>
      [Your final, concise answer to the query. This is the only part that will be shown to the user.]
      </output>
      """
  return f"Question:{question[0]}"

def extract_output_tag(text):
  # Split by <output> and </output> and get the middle part
  ft['time'] = ft['time'] - 1
  return text.split("<output>")[1].split("</output>")[0].strip()

import os
def genai_write_text_to_disk(text, filename):
  with open(filename, 'a') as f:
    f.write(f"{text}\n")

def genai_read_text_from_disk(filename):
  with open(filename, 'r') as f:
    return f.readlines()

if __name__ == "__main__":
  # while ft['time'] != -1:
    thoughts = chain_of_thought(genai_read_text_from_disk("output.txt"))
    answer = extract_output_tag(thoughts)
    genai_write_text_to_disk (f"Breaking News!: Ell AI has determined there are {answer} r's in strawberry", "output.txt")
    # sleep(5)
