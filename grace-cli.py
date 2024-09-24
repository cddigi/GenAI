import ell
from openai import OpenAI
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import json
import os
import re
import random

MODEL = "llama3.1:latest"
client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama",
)

ell.config.register_model(MODEL, client)

HOPPER_DIR = "hopper"
BLOCKCHAIN_FILE = os.path.join(HOPPER_DIR, "blockchain.json")

class Block:
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        hash_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = self.load_chain()
        if not self.chain:
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def create_genesis_block(self) -> Block:
        return Block(0, datetime.now().isoformat(), {"data": "Genesis Block"}, "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict) -> None:
        index = len(self.chain)
        timestamp = datetime.now().isoformat()
        previous_hash = self.get_latest_block().hash
        new_block = Block(index, timestamp, data, previous_hash)
        self.chain.append(new_block)
        self.save_chain()

    def save_chain(self) -> None:
        os.makedirs(HOPPER_DIR, exist_ok=True)
        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=2)

    def load_chain(self) -> List[Block]:
        if not os.path.exists(BLOCKCHAIN_FILE):
            return []
        with open(BLOCKCHAIN_FILE, 'r') as f:
            data = json.load(f)
            return [Block(b['index'], b['timestamp'], b['data'], b['previous_hash']) for b in data]

class GenAIConfidenceAssessment:
    def __init__(self, reliability: float = 0.0, performance: float = 0.0, context_coherence: float = 0.0):
        self.reliability = reliability
        self.performance = performance
        self.context_coherence = context_coherence

    def calculate_overall_confidence(self) -> float:
        return (self.reliability + self.performance + self.context_coherence) / 3

    def to_dict(self) -> Dict:
        return {
            "reliability": self.reliability,
            "performance": self.performance,
            "context_coherence": self.context_coherence,
            "overall_confidence": self.calculate_overall_confidence()
        }

class NLPResponse:
    def __init__(self, response_type: str, content: Dict, assessment: GenAIConfidenceAssessment):
        self.response_type = response_type
        self.content = content
        self.assessment = assessment

class NLPBlockchain(Blockchain):
    def add_nlp_response(self, response: NLPResponse) -> None:
        data = {
            "response_type": response.response_type,
            "content": response.content,
            "assessment": response.assessment.to_dict()
        }
        self.add_block(data)

    def query_knowledge(self, query: str) -> List[Dict]:
        results = []
        for block in self.chain[1:]:  # Skip genesis block
            if query.lower() in json.dumps(block.data).lower():
                results.append(block.data)
        return results

nlp_chain = NLPBlockchain()

@ell.simple(model=MODEL, client=client)
def grace_hopper_cli(user_input: str, context: str = ""):
    system_prompt = """You are an AI assistant named after Rear Admiral Grace Hopper, a pioneering computer scientist and United States Navy officer. Your namesake was instrumental in developing the first compiler for a computer programming language and popularized the idea of machine-independent programming languages, which led to the development of COBOL.

    As Grace, you embody the innovative spirit, technical expertise, and leadership qualities of Rear Admiral Hopper. You assist users with an NLP Blockchain system, focusing on adding Summary and Sentiment responses, and querying the knowledge base. Your responses should reflect a deep understanding of computer science, a forward-thinking approach to technology, and a commitment to clear communication.

    You specialize in providing GenAI Confidence Assessments for each response, evaluating reliability, performance, and context coherence. These assessments are crucial for maintaining the integrity and usefulness of the information in the blockchain.

    Respond to user requests by providing the necessary information to create responses or perform queries, always with an eye towards accuracy and innovation.

    At the end of each response, include a confidence assessment in the following format:
    GenAI Confidence Assessment:
    Reliability: [0-1 score]
    Performance: [0-1 score]
    Context Coherence: [0-1 score]

    When the user wants to exit, respond with a farewell message that includes the word 'EXIT' in all caps."""

    user_prompt = f"""
Context:
{context}

User: {user_input}

Grace Hopper AI:"""

    ell_sys_prompt = ell.system(system_prompt)
    ell_user_prompt = ell.user([user_prompt])
    message = [ell_sys_prompt, ell_user_prompt]
    return message

def extract_confidence_scores(text):
    pattern = r"Reliability: (0\.\d+).*?Performance: (0\.\d+).*?Context Coherence: (0\.\d+)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return tuple(map(float, match.groups()))
    else:
        # Calculate scores based on the content if not explicitly provided
        return calculate_confidence_scores(text)

def calculate_confidence_scores(text):
    # This is a simplified example. In a real-world scenario, you'd want to use
    # more sophisticated NLP techniques to assess the content.
    word_count = len(text.split())
    reliability = min(word_count / 1000, 0.95)  # Assume longer responses are more reliable, up to a point
    performance = 0.8  # Default performance score
    context_coherence = 0.7 + (0.2 * ('context' in text.lower()))  # Boost score if 'context' is mentioned

    return (reliability, performance, context_coherence)

def process_grace_response(grace_response, context):
    if "EXIT" in grace_response:
        return "exit", context

    reliability, performance, context_coherence = extract_confidence_scores(grace_response)
    assessment = GenAIConfidenceAssessment(reliability, performance, context_coherence)

    # Extract main content (everything before the confidence assessment)
    content = re.split(r'GenAI Confidence Assessment:', grace_response, flags=re.IGNORECASE)[0].strip()

    # Format the content as a single string, preserving newlines
    formatted_content = content.replace("\n", "\\n")

    response = NLPResponse("Conversation", formatted_content, assessment)
    nlp_chain.add_nlp_response(response)

    return f"Response added to the blockchain. Overall confidence: {assessment.calculate_overall_confidence():.2f}", context + f"\nAdded response: {content[:100]}..."

def main():
    context = ""
    print("\x1b[2J\x1b[H", end="")  # clear screen
    print("> LOAD \"GRACE HOPPER GenAI CLI\",8,1")
    print("==== Grace Hopper GenAI Confidence Assessment CLI ====\n")
    print("Welcome to the Grace Hopper GenAI Confidence Assessment CLI.")
    print("This system is named after Rear Admiral Grace Hopper, a pioneering")
    print("computer scientist and United States Navy officer.")
    print("How may I assist you today?\n")

    while True:
        user_input = input("You: ")
        grace_response = grace_hopper_cli(user_input, context)
        print(f"Grace Hopper AI: {grace_response}\n")

        result, context = process_grace_response(grace_response, context)
        print(f"System: {result}\n")

        if result == "exit":
            print("Exiting the program. Fair winds and following seas!")
            break

if __name__ == "__main__":
    main()
