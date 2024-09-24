from typing import List, Dict, Optional
from datetime import datetime
import hashlib

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

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

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

class EvaluationCriteria:
    def __init__(self):
        self.criteria = {
            "Grammatically Complete": {"reason": "", "confidence": 0.0, "boolean": False},
            "Logically Consistent": {"reason": "", "confidence": 0.0, "boolean": False},
            "AI Inquiry": {"reason": "", "confidence": 0.0, "boolean": False},
            "Content Language": {"reason": "", "confidence": 0.0, "boolean": False}
        }

    def update_criterion(self, criterion: str, reason: str, confidence: float, boolean_value: bool) -> None:
        if criterion in self.criteria:
            self.criteria[criterion] = {"reason": reason, "confidence": confidence, "boolean": boolean_value}
        else:
            raise ValueError(f"Invalid criterion: {criterion}")

    def calculate_overall_confidence(self) -> float:
        return sum(c["confidence"] for c in self.criteria.values()) / len(self.criteria)

class NLPResponse:
    def __init__(self, response_type: str, content: Dict, evaluation: EvaluationCriteria):
        self.response_type = response_type
        self.content = content
        self.evaluation = evaluation

class SummaryResponse(NLPResponse):
    def __init__(self, summary: str, key_points: Optional[List[str]], evaluation: EvaluationCriteria):
        super().__init__("Summary", {"summary": summary, "key_points": key_points}, evaluation)

class TranslationResponse(NLPResponse):
    def __init__(self, translated_text: str, source_language: str, target_language: str, evaluation: EvaluationCriteria):
        super().__init__("Translation", {
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language
        }, evaluation)

class SentimentResponse(NLPResponse):
    def __init__(self, sentiment: str, score: float, explanation: str, evaluation: EvaluationCriteria):
        super().__init__("Sentiment", {
            "sentiment": sentiment,
            "score": score,
            "explanation": explanation
        }, evaluation)

class NLPBlockchain(Blockchain):
    def add_nlp_response(self, response: NLPResponse) -> None:
        data = {
            "response_type": response.response_type,
            "content": response.content,
            "evaluation": response.evaluation.criteria,
            "overall_confidence": response.evaluation.calculate_overall_confidence()
        }
        self.add_block(data)

    def query_knowledge(self, query: str) -> List[Dict]:
        results = []
        for block in self.chain[1:]:  # Skip genesis block
            if query.lower() in str(block.data).lower():
                results.append(block.data)
        return results

# Usage example
nlp_chain = NLPBlockchain()

# Create and add a summary response
summary_eval = EvaluationCriteria()
summary_eval.update_criterion("Grammatically Complete", "Well-formed sentences", 0.95, True)
summary_eval.update_criterion("Logically Consistent", "Ideas flow coherently", 0.9, True)
summary_response = SummaryResponse(
    "This is a summary of the text.",
    ["Key point 1", "Key point 2"],
    summary_eval
)
nlp_chain.add_nlp_response(summary_response)

# Create and add a translation response
translation_eval = EvaluationCriteria()
translation_eval.update_criterion("Content Language", "Correctly translated to target language", 0.98, True)
translation_response = TranslationResponse(
    "Это перевод текста.",
    "English",
    "Russian",
    translation_eval
)
nlp_chain.add_nlp_response(translation_response)

# Query the blockchain
results = nlp_chain.query_knowledge("summary")
for result in results:
    print(f"Found response of type: {result['response_type']}")
    print(f"Content: {result['content']}")
    print(f"Overall confidence: {result['overall_confidence']}")
    print("---")
