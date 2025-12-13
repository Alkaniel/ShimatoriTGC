import pygame
import os
import constants.colors as colors

class GameState:
    def __init__(self, game_manager):
        self.game = game_manager
        self.screen = game_manager.screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # --- Polices (Fonts) ---
        self.fonts = {
            'title': self.get_font(90, bold=True),
            'subtitle': self.get_font(32),
            'button': self.get_font(44),
            'small': self.get_font(24)
        }

    def get_font(self, size, bold=False):
        try:
            return pygame.font.SysFont('cinzel, trajan, georgia', size, bold=bold)
        except:
            return pygame.font.Font(None, size)

    def load_image(self, filename, width=None):
        """Charge une image depuis assets/images/"""
        # On remonte de 2 dossiers (utils -> src -> root) pour trouver assets
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            if width: # Redimensionnement proportionnel automatique
                aspect_ratio = img.get_width() / img.get_height()
                new_height = int(width / aspect_ratio)
                img = pygame.transform.scale(img, (width, new_height))
            return img
        except Exception as e:
            print(f"Erreur chargement image {filename}: {e}")
            return None

    def draw_background(self):
        """Le fond commun Washi + Bordures"""
        self.screen.fill(colors.WASHI_COLOR)
        
        # Bordures
        border_width = 40
        # Gauche
        pygame.draw.rect(self.screen, colors.INDIGO, (0, 0, border_width, self.height))
        pygame.draw.line(self.screen, colors.GOLD_LEAF, (border_width-2, 0), (border_width-2, self.height), 2)
        # Droite
        pygame.draw.rect(self.screen, colors.INDIGO, (self.width - border_width, 0, border_width, self.height))
        pygame.draw.line(self.screen, colors.GOLD_LEAF, (self.width - border_width+2, 0), (self.width - border_width+2, self.height), 2)
        
        # Motif Vagues (Seigaiha) en haut et bas
        self.draw_waves(0, True)
        self.draw_waves(self.height - 40, False)

    def draw_waves(self, y, top=True):
        """Dessine les petites vagues bleues (optionnel mais joli)"""
        wave_color = (*colors.INDIGO, 80) # Indigo transparent
        surf = pygame.Surface((self.width, 40), pygame.SRCALPHA)
        for i in range(0, self.width, 40):
            if top:
                pygame.draw.arc(surf, wave_color, (i, -10, 40, 40), 3.14, 6.28, 2)
            else:
                pygame.draw.arc(surf, wave_color, (i, 10, 40, 40), 0, 3.14, 2)
        self.screen.blit(surf, (0, y))

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self):
        self.draw_background()

    def on_resize(self, width, height):
        """Called when the window is resized"""
        self.width = width
        self.height = height
        # Update the reference to the screen
        self.screen = self.game.screen