import pygame
import math
import constants.colors as colors
from utils.game_state import GameState

class MainMenu(GameState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # 1. On charge l'image BRUTE (sans la redimensionner tout de suite)
        # Note: j'enlève le paramètre width=500 pour garder la taille originale
        self.original_logo = self.load_image("raw.png") 
        self.logo = self.original_logo # C'est celle-ci qu'on affichera
        


        
        self.buttons = [
            {"text": "Nouvelle Partie", "action": "game", "rect": None},
            {"text": "Collection", "action": "collection", "rect": None},
            {"text": "Options", "action": "options", "rect": None},
            {"text": "Quitter", "action": "quit", "rect": None}
        ]
        self.selected_index = 0
        self.time = 0
        
        # On force un premier calcul de taille
        self.on_resize(self.width, self.height)

    def on_resize(self, width, height):
        """Recalcule tout en fonction de la nouvelle taille"""
        super().on_resize(width, height)
        
        # 2. Redimensionnement DYNAMIQUE du logo
        # On veut que le logo fasse environ 25% de la hauteur de l'écran ou 40% de la largeur
        # On prend le plus petit pour que ça rentre toujours
        if self.original_logo:
            target_h = int(height * 0.35) # 35% de la hauteur de l'écran
            
            # Calcul du ratio pour ne pas déformer l'image
            aspect_ratio = self.original_logo.get_width() / self.original_logo.get_height()
            target_w = int(target_h * aspect_ratio)
            
            # Transformation propre
            self.logo = pygame.transform.smoothscale(self.original_logo, (target_w, target_h))

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN:
                    self.trigger_button(self.selected_index)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(self.buttons):
                        if button["rect"] and button["rect"].collidepoint(mouse_pos):
                            self.trigger_button(i)

        for i, button in enumerate(self.buttons):
            if button["rect"] and button["rect"].collidepoint(mouse_pos):
                self.selected_index = i

    def trigger_button(self, index):
        action = self.buttons[index]["action"]
        self.game.change_state(action)
    
    def update(self):
        self.time += 0.05

    def draw(self):
        super().draw()

        center_x = self.width // 2
        
        # 3. Positionnement RELATIF (en %)
        # Le logo est placé à 20% du haut de l'écran
        logo_y = int(self.height * 0.25)
        
        if self.logo:
            logo_rect = self.logo.get_rect(center=(center_x, logo_y))
            self.screen.blit(self.logo, logo_rect)
            
            
            # Titre juste en dessous du logo
            # title_y = logo_rect.bottom + 30 
            # (Optionnel si tu veux garder le titre TEXTE en plus du logo)
            title = self.fonts['title'].render("SHIMATORI", True, colors.SUMI_BLACK)
            self.screen.blit(title, title.get_rect(center=(center_x, logo_y + self.logo.get_height()//2 + 50)))
        else:
            title = self.fonts['title'].render("SHIMATORI", True, colors.SUMI_BLACK)
            self.screen.blit(title, title.get_rect(center=(center_x, logo_y)))

        # 4. Positionnement des Boutons RELATIF
        # Le premier bouton commence à 55% de la hauteur de l'écran
        start_y = int(self.height * 0.55)
        gap = int(self.height * 0.05) # Espace entre boutons = 5% de la hauteur

        for i, button in enumerate(self.buttons):
            y_pos = start_y + (i * gap)
            
            is_selected = (i == self.selected_index)
            btn_width = 350
            btn_height = 60
            
            btn_rect = pygame.Rect(center_x - btn_width//2, y_pos - btn_height//2, btn_width, btn_height)
            button["rect"] = btn_rect
            
            if is_selected:
                pulse = math.sin(self.time) * 2
                draw_rect = btn_rect.inflate(pulse, pulse)
                s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                s.fill((*colors.WASHI_COLOR, 200))
                self.screen.blit(s, draw_rect)
                pygame.draw.rect(self.screen, colors.VERMILLION, draw_rect, 3)
                
                # (Je garde tes décorations de coins ici, elles sont bien)
                # ... [Code des coins dorés identique à avant] ...

            text_color = colors.SUMI_BLACK if is_selected else colors.SUMI_GRAY
            text_surf = self.fonts['button'].render(button["text"], True, text_color)
            self.screen.blit(text_surf, text_surf.get_rect(center=(center_x, y_pos)))