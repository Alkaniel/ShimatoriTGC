import pygame
from constants.enums import CardType, Faction, Rarity, Keyword

class Card:
    """Classe parente pour toutes les cartes"""
    def __init__(self, data: dict):
        self.id = data.get("id", "unknown")
        self.name = data.get("nom", "Inconnu")
        self.description = data.get("description", "")
        self.mana_cost = data.get("cout", 0)
        self.image_path = data.get("image", None)
        
        # Gestion Faction (Conversion String JSON -> Enum)
        faction_str = data.get("classe", "Neutre")
        # Petite astuce pour mapper tes strings JSON vers l'Enum Faction
        # On essaie de trouver la valeur correspondante
        found = False
        for f in Faction:
            if f.value == faction_str:
                self.faction = f
                found = True
                break
        if not found:
            self.faction = Faction.NEUTRAL
            
        self.rarity = Rarity(data.get("rarete", 1))

    def __repr__(self):
        return f"<{self.name} ({self.mana_cost})>"

class UnitCard(Card):
    """Une créature sur le plateau"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = CardType.UNIT
        
        # Stats
        self.base_attack = data.get("puissance", 0)
        self.base_health = data.get("vitalite", 0)
        
        # État dynamique (changera pendant la partie)
        self.current_attack = self.base_attack
        self.current_health = self.base_health
        self.max_health = self.base_health
        
        self.is_dead = False
        self.can_attack = False # False par défaut (Mal d'invocation)
        self.attacks_left = 0
        
        # Gestion des Mots-Clés (ex: ["Charge", "Provocation"])
        self.keywords = []
        raw_keywords = data.get("competences", [])
        for k_str in raw_keywords:
            # On cherche si le mot-clé existe dans l'Enum
            for k in Keyword:
                if k.value == k_str:
                    self.keywords.append(k)
                    break
        
        # Application immédiate de la Charge
        if Keyword.CHARGE in self.keywords:
            self.can_attack = True

    def take_damage(self, amount: int):
        self.current_health -= amount
        # Gestion Rage (Akaryu) : Si blessé et survit -> Bonus ?
        if self.current_health <= 0:
            self.current_health = 0
            self.is_dead = True
    
    def heal(self, amount: int):
        if not self.is_dead:
            self.current_health = min(self.max_health, self.current_health + amount)

class SpellCard(Card):
    """Un sort (Effet immédiat)"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = CardType.SPELL
        # On utilisera un ID d'effet pour coder la logique plus tard
        # ex: "deal_3_dmg", "draw_2"
        self.effect_id = data.get("effect_id", "none")