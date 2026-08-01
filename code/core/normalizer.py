import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.domain import Message
from models.results import NormalizedMessage

class MessageNormalizer:
    def normalize(self, message: Message) -> NormalizedMessage:
        # Stub implementation: Passes through text without deep extraction
        text = str(message.message_text) if message.message_text else ""
        return NormalizedMessage(
            raw_text=text,
            normalized_text=text.lower().strip(),
            language="en",
            mentions=[],
            urls=[],
            phone_numbers=[],
            currency=[],
            dates=[],
            times=[],
            entities=[]
        )
