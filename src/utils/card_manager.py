import json
import os

class CardManager:
    def __init__(self):
        self.cards = []
        self.filepath = os.path.join(os.path.dirname(__file__), '..', "..", 'cards.json')
        self.load_cards()

    def load_cards(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    raw_list = data.get('cards', [])
                    
                    self.cards = []
                    for item in raw_list:
                        if "puissance" in item:
                            self.cards.append(UnitCard(item))
                        else:
                            self.cards.append(SpellCard(item))
                            
                    print(f"Chargé {len(self.cards)} cartes (Objets).")
            except Exception as e:
                print(f"Erreur JSON : {e}")
                self.cards = []
        else:
            self.cards = []

    def _generate_test_cards(self):
        """Génère des fausses cartes si le fichier manque (Fallback)"""
        return [
            {
                "id": i,
                "nom": f"Guerrier {i}", 
                "puissance": i*10, 
                "vitalite": i*5, 
                "cout": i % 10,
                "description": "Un guerrier puissant du clan Shimatori.", 
                "rarete": (i%5)+1
            } 
            for i in range(1, 21)
        ]

    def get_all_cards(self):
        """Renvoie toutes les cartes"""
        return self.cards

    def get_card_by_id(self, card_id):
        """Utile pour le futur système de jeu"""
        for card in self.cards:
            if card.get("id") == card_id:
                return card
        return None