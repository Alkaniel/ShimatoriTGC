import pygame
import sys
import os
import json
from menus.main_menu import MainMenu
from menus.options_menu import OptionsMenu
from menus.collection_menu import CollectionMenu
from utils.card_manager import CardManager

class Game:
    def __init__(self):
        pygame.init()
        
        # 1. Charger la config AVANT de créer la fenêtre
        self.config = self.load_config()

        self.card_manager = CardManager()

        # 2. Déterminer la résolution et les flags selon la config
        if self.config["fullscreen"]:
            # Mode "Plein écran fenêtré" (Borderless)
            info = pygame.display.Info()
            self.width = info.current_w
            self.height = info.current_h
            flags = pygame.NOFRAME
        else:
            # Mode Fenêtré classique
            # On transforme "1280x720" en deux entiers width et height
            try:
                res_string = self.config["resolution"]
                w, h = map(int, res_string.split('x'))
                self.width = w
                self.height = h
            except:
                # Valeur de secours si le fichier est mal écrit
                self.width = 1280
                self.height = 720
            flags = 0

        # 3. Créer la fenêtre avec les paramètres chargés
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        
        pygame.display.set_caption("Shimatori TCG")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 4. Appliquer le volume sonore immédiatement
        # (Sinon la musique explosera les oreilles avant que le menu options ne se charge)
        try:
            vol = self.config["music_volume"] / 100
            pygame.mixer.music.set_volume(vol)
        except:
            pass

        # 5. Initialiser les états (Menus)
        # Ils vont utiliser self.screen qui est maintenant à la bonne taille !
        self.states = {
            "menu": MainMenu(self),
            "options": OptionsMenu(self),
            "collection": CollectionMenu(self)
        }

        self.current_state = self.states["menu"]

    def load_config(self):
        """Charge la config depuis le fichier JSON"""
        # On suppose que config.json est à la racine du projet (un dossier au-dessus de main.py)
        # Ajuste '..' si ton main.py est à la racine
        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        
        default = {
            "music_volume": 70, "sfx_volume": 80, "fullscreen": False,
            "resolution": "1280x720", "language": "Français", "vsync": True
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default, **json.load(f)}
        except Exception as e:
            print(f"Info: Utilisation configuration par défaut ({e})")
        
        return default

    def change_state(self, state_name: str):
        if state_name == "quit":
            self.running = False
        elif state_name in self.states:
            self.current_state = self.states[state_name]
            
            # Petit bonus : On force un redimensionnement quand on arrive sur un menu
            # pour être sûr que tout est bien calé
            if hasattr(self.current_state, 'on_resize'):
                self.current_state.on_resize(self.width, self.height)

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            if self.current_state:
                self.current_state.handle_events(events)
                self.current_state.update()
                self.current_state.draw()

            pygame.display.flip()
            self.clock.tick(60) # Limite à 60 FPS pour éviter de surchauffer le CPU

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()