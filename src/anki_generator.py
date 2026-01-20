"""
Anki deck generator using genanki library.
"""
import genanki
import random
from typing import List, Dict
from datetime import datetime


# Unique IDs for the deck and models (must stay constant)
DECK_ID = 1607392319
BASIC_MODEL_ID = 1607392320
CLOZE_MODEL_ID = 1607392321


# Basic card model (front/back)
BASIC_MODEL = genanki.Model(
    BASIC_MODEL_ID,
    'Telegram2Anki Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
        },
    ],
    css='''
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
    }
    '''
)


# Cloze deletion model
CLOZE_MODEL = genanki.Model(
    CLOZE_MODEL_ID,
    'Telegram2Anki Cloze',
    model_type=genanki.Model.CLOZE,
    fields=[
        {'name': 'Text'},
        {'name': 'Extra'},
    ],
    templates=[
        {
            'name': 'Cloze',
            'qfmt': '{{cloze:Text}}',
            'afmt': '{{cloze:Text}}<br>{{Extra}}',
        },
    ],
    css='''
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
    }
    .cloze {
        font-weight: bold;
        color: blue;
    }
    '''
)


class AnkiGenerator:
    """Generate Anki deck files from card data."""
    
    def __init__(self, deck_name: str = "Datos"):
        self.deck_name = deck_name
        self.deck = genanki.Deck(DECK_ID, deck_name)
    
    def add_card(self, card: Dict) -> bool:
        """
        Add a card to the deck.
        
        Card format:
        - {"type": "basic", "front": "...", "back": "..."}
        - {"type": "cloze", "text": "... {{c1::...}} ..."}
        """
        try:
            if card.get("type") == "basic":
                note = genanki.Note(
                    model=BASIC_MODEL,
                    fields=[card["front"], card["back"]]
                )
                self.deck.add_note(note)
                return True
                
            elif card.get("type") == "cloze":
                note = genanki.Note(
                    model=CLOZE_MODEL,
                    fields=[card["text"], ""]
                )
                self.deck.add_note(note)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error adding card: {e}")
            return False
    
    def add_cards(self, cards: List[Dict]) -> int:
        """Add multiple cards to the deck. Returns count of successfully added cards."""
        count = 0
        for card in cards:
            if self.add_card(card):
                count += 1
        return count
    
    def save(self, filepath: str) -> str:
        """
        Save the deck to an .apkg file.
        
        Returns the filepath if successful.
        """
        package = genanki.Package(self.deck)
        package.write_to_file(filepath)
        return filepath
    
    def generate_filename(self) -> str:
        """Generate a filename with current date."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"datos_{date_str}.apkg"
