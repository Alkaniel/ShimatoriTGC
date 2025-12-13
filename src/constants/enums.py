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

class Keyword(Enum):
    CHARGE = "Charge"
    TAUNT = "Provocation"
    STEALTH = "Furtivité"
    LIFESTEAL = "Vol de vie"
    BATTLECRY = "Cri de guerre"
    DEATHRATTLE = "Dernier souffle"
    RAGE = "Rage"
    FREZZE = "Gel"
    
