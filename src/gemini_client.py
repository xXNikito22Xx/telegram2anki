"""
Gemini API client for generating Anki flashcards from text.
"""
import json
import google.generativeai as genai
from typing import List, Dict, Optional


CARD_GENERATION_PROMPT = """Eres un experto en crear tarjetas de memoria (flashcards) efectivas para Anki.

Dado el siguiente dato curioso o información, genera una o más tarjetas de Anki.
Usa el formato que mejor se adapte al contenido:

1. **Pregunta/Respuesta (basic)**: Para hechos directos, fechas, definiciones simples
2. **Cloze (texto con huecos)**: Para definiciones con contexto, frases donde hay que recordar un elemento clave

REGLAS:
- Sé conciso pero informativo
- La pregunta debe ser clara y específica
- La respuesta debe ser memorable
- Para cloze, usa el formato {{c1::texto a ocultar}}
- Genera entre 1 y 3 tarjetas según la complejidad del dato
- Las tarjetas deben estar en el mismo idioma que el dato original

Responde ÚNICAMENTE con JSON válido en este formato exacto:
{
  "cards": [
    {"type": "basic", "front": "pregunta aquí", "back": "respuesta aquí"},
    {"type": "cloze", "text": "La capital de Francia es {{c1::París}}"}
  ]
}

DATO A CONVERTIR:
"""


class GeminiClient:
    """Client for Gemini API to generate flashcards."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_cards(self, text: str) -> List[Dict]:
        """
        Generate Anki cards from a piece of text.
        
        Returns a list of card dictionaries with 'type', 'front'/'back' or 'text'.
        """
        try:
            prompt = CARD_GENERATION_PROMPT + text
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Handle markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            data = json.loads(response_text)
            cards = data.get("cards", [])
            
            # Validate card structure
            valid_cards = []
            for card in cards:
                if card.get("type") == "basic":
                    if card.get("front") and card.get("back"):
                        valid_cards.append(card)
                elif card.get("type") == "cloze":
                    if card.get("text") and "{{c1::" in card.get("text", ""):
                        valid_cards.append(card)
            
            return valid_cards
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response was: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"Error generating cards: {e}")
            return []
    
    def generate_cards_batch(self, texts: List[str]) -> List[Dict]:
        """Generate cards for multiple texts."""
        all_cards = []
        for text in texts:
            cards = self.generate_cards(text)
            for card in cards:
                card["source_text"] = text
            all_cards.extend(cards)
        return all_cards


