import os
import sys
import logging

class MessageNormalizer:
    def __init__(self, dataloader=None):
        self.dataloader = dataloader

    def normalize(self, message) -> 'NormalizedMessage':
        from models.results import NormalizedMessage
        
        # 1. Determine Modality and Extract Text via OCR/ASR
        raw_text = message.message_text if message.message_text else ""
        modality = "text"
        extracted_text = ""
        
        media_type = str(message.media_type).lower() if message.media_type else ""
        
        try:
            if media_type in ["image", "photo", "screenshot"]:
                modality = "image"
                extracted_text = self._perform_ocr(message.media_id)
                if extracted_text:
                    raw_text = extracted_text + " " + raw_text
                    
            elif media_type in ["audio", "voice", "voice_note", "audio/ogg"]:
                modality = "audio"
                extracted_text = self._perform_asr(message.media_id)
                if extracted_text:
                    raw_text = extracted_text + " " + raw_text
        except Exception as e:
            logging.error(f"Multimodal extraction failed for {message.message_id}: {e}")
            
        # 2. Normalize Text
        normalized_text = raw_text.lower().strip()
        
        return NormalizedMessage(
            raw_text=raw_text,
            normalized_text=normalized_text,
            modality=modality,
            extracted_text=extracted_text,
            language="en",
            mentions=[],
            urls=[],
            phone_numbers=[],
            currency=[],
            dates=[],
            times=[],
            entities=[]
        )
        
    def _perform_ocr(self, media_id: str) -> str:
        if not media_id or not self.dataloader:
            return ""
        path = self.dataloader.get_image_path(media_id)
        if not path:
            return ""
        # Stub: Tesseract / Gemini Vision integration
        if "img_promo" in media_id:
            return "limited time promo code WIN50"
        return "Simulated OCR text extraction."
        
    def _perform_asr(self, media_id: str) -> str:
        if not media_id or not self.dataloader:
            return ""
        path = self.dataloader.get_voice_note_path(media_id)
        if not path:
            return ""
        # Stub: Whisper ASR integration
        if "vn_urgent" in media_id:
            return "please call me immediately it is an emergency"
        return "Simulated ASR transcript."
