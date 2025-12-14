from enum import Enum, auto

class CardType(Enum):
    UNIT = "Unit"
    SPELL = "Spell"
    WEAPON = "Weapon"

class Faction(Enum):
    RYUSEI = "Ryūsei"
    MIZUTORI = "Mizutori"
    HOSHIKAWA = "Hoshikawa"
    KUROGAMI = "Kurogami"
    AKARYU = "Akaryū"
    YUKIKAGE = "Yukikage"
    MONGOL = "Mongol"
    NEUTRAL = "Neutre"

class Rarity(Enum):
    COMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4
    MYTHICAL = 5


class Keyword(Enum):
    TAUNT = "Provocation"
    CHARGE = "Charge"
    DIVINE_SHIELD = "Bouclier Divin"
    STEALTH = "Furtivité"
    POISONOUS = "Toxique"
    LIFESTEAL = "Vol de vie"
    HEAL="Soins"
    FORGE = "Forge" 
    SACRIFICE = "Sacrifice"
    BATTLECRY = "Cri de guerre"
    DEATHRATTLE = "Râle d'agonie"
    
