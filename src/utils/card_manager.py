import json
import os
import sys

# --- FIX DES CHEMINS (IMPORTANT) ---
# 1. On récupère le dossier où se trouve ce fichier (src/utils)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. On récupère le dossier parent (src)
src_dir = os.path.dirname(current_dir)
# 3. On ajoute 'src' aux chemins de recherche de Python
if src_dir not in sys.path:
    sys.path.append(src_dir)

# --- IMPORTS ---
try:
    # Maintenant Python trouve 'models' car il connait 'src'
    from models.card_types import UnitCard, SpellCard
except ImportError as e:
    print(f"CRITICAL ERROR: Impossible d'importer les modèles. ({e})")
    # On affiche les chemins connus pour aider au debug
    print(f"Chemins Python: {sys.path}")
    sys.exit(1)

class CardManager:
    def __init__(self):
        self.cards = []
        # Chemin vers cards.json (remonte de utils/ vers la racine du projet)
        self.filepath = os.path.join(src_dir, '..', 'cards.json')
        self.load_cards()

    def load_cards(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    raw_list = data.get('cards', [])
                    
                    self.cards = []
                    for item in raw_list:
                        # Détection automatique du type
                        if "puissance" in item:
                            self.cards.append(UnitCard(item))
                        else:
                            self.cards.append(SpellCard(item))
                            
                    print(f"Succès : {len(self.cards)} cartes chargées.")
            except Exception as e:
                print(f"Erreur lors du chargement JSON : {e}")
                self.cards = []
        else:
            print(f"Attention : Fichier introuvable à {self.filepath}")
            # On cherche à comprendre où il cherche
            print(f"Dossier actuel : {os.getcwd()}")
            self.cards = []

    def get_all_cards(self):
        return self.cards