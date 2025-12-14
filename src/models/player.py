import random
import copy
from models.card_types import UnitCard

class Player:
    def __init__(self, name, collection_cards, is_ai=False):
        self.name = name
        self.is_ai = is_ai

        self.health = 30
        self.max_health = 30
        self.mana = 0
        self.max_mana = 0

        self.deck = []
        self.hand = []
        self.board = []
        self.graveyard = []

        self.build_random_deck(collection_cards)

    def build_random_deck(self, collection_cards, deck_size=30):
        """Create a random deck from the player's collection."""
        if not collection_cards:
            print(f"Error: {self.name} has no cards in their collection to build a deck.")
            return
        
        drafted_cards = random.choices(collection_cards, k=deck_size)

        self.deck = [copy.deepcopy(card) for card in drafted_cards]

        print(f"{self.name}'s deck built with {len(self.deck)} cards.")

    def draw_card(self, amount=1):
        """Draw x cards from the deck to the hand."""
        for _ in range(amount):
            if len(self.deck) > 0:
                if len(self.hand) < 10:
                    card = self.deck.pop(0)
                    self.hand.append(card)
                else:
                    print(f"{self.name}'s hand is full! Cannot draw more cards.")
                    # Here you could implement discarding the drawn card or other mechanics.
            else:
                print(f"{self.name}'s deck is empty! Cannot draw more cards.")
                # Here you could implement fatigue damage or other mechanics.

    def start_turn(self):
        """Start of turn logic."""
        if self.max_mana < 10:
            self.max_mana += 1
        self.mana = self.max_mana
        self.draw_card()

        for unit in self.board:
            unit.can_attack = True
            unit.attacks_left = 1

    def play_unit(self, index):
        """Essaie de jouer une unité depuis la main vers le plateau"""
        if 0 <= index < len(self.hand):
            card = self.hand[index]
            
            # 1. Vérif Mana
            if self.mana >= card.mana_cost:
                # 2. Vérif Type (On ne pose que les Unités pour l'instant)
                if isinstance(card, UnitCard):
                    # 3. Vérif Place sur le plateau (Max 7 unités style Hearthstone)
                    if len(self.board) < 7:
                        self.mana -= card.mana_cost
                        played_card = self.hand.pop(index)
                        self.board.append(played_card)
                        print(f"{self.name} joue {played_card.name}")
                        return True
                    else:
                        print("Plateau plein !")
                else:
                    print("Impossible de jouer un Sort comme une Unité (pour l'instant).")
            else:
                print("Pas assez de mana !")
        return False
    
    def play_ritual(self, index, target):
        """Joue un Rituel sur une cible spécifique"""
        if 0 <= index < len(self.hand):
            card = self.hand[index]
            
            # 1. Vérif Mana
            if self.mana >= card.mana_cost:
                
                # 2. Application de l'effet selon le type
                effect_applied = False
                
                # CAS A : Dégâts (sur Unité ou Joueur)
                if card.effect_type == "damage_target":
                    if hasattr(target, 'take_damage'): # C'est une unité
                        target.take_damage(card.effect_value)
                        effect_applied = True
                    elif hasattr(target, 'health'): # C'est un joueur
                        target.health -= card.effect_value
                        effect_applied = True
                        
                # CAS B : Buff (Uniquement sur Unité)
                elif card.effect_type == "buff_target":
                    if hasattr(target, 'current_attack'): # Vérif que c'est une unité
                        target.current_attack += card.effect_value
                        effect_applied = True
                    else:
                        print("Impossible : Ce rituel cible uniquement les unités !")

                # 3. Si l'effet a marché : On paie et on défausse
                if effect_applied:
                    self.mana -= card.mana_cost
                    played_card = self.hand.pop(index)
                    self.graveyard.append(played_card)
                    print(f"{self.name} lance le rituel {played_card.name} sur {getattr(target, 'name', 'Cible')}")
                    return True
            else:
                print("Pas assez de mana pour ce rituel !")
        return False