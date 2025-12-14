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
        
        # Mapping Faction
        faction_str = data.get("classe", "Neutre")
        self.faction = Faction.NEUTRAL
        for f in Faction:
            if f.value == faction_str or f.name == faction_str.upper():
                self.faction = f
                break
            
        self.rarity = Rarity(data.get("rarete", 1))

    def __repr__(self):
        return f"<{self.name} ({self.faction.value})>"

class UnitCard(Card):
    """Une créature / unité sur le plateau"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = CardType.UNIT
        
        self.base_attack = data.get("puissance", 0)
        self.base_health = data.get("vitalite", 0)
        self.current_attack = self.base_attack
        self.current_health = self.base_health
        self.max_health = self.base_health
        
        self.is_dead = False
        self.can_attack = False 
        self.attacks_left = 0
        
        self.keywords = []
        raw_keywords = data.get("competences", [])
        for k_str in raw_keywords:
            for k in Keyword:
                if k.value == k_str:
                    self.keywords.append(k)
                    break
        
        if Keyword.CHARGE in self.keywords:
            self.can_attack = True
            self.attacks_left = 1

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.is_dead = True

class SpellCard(Card):
    """Un Rituel à effet immédiat"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = CardType.SPELL
        
        self.effect_type = data.get("effect_type", "none")

        self.effect_value = data.get("effect_value", 0)