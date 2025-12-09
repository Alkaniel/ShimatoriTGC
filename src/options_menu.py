import pygame
import sys
import math
import json
import os


class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Couleurs (même palette que le menu principal)
        self.washi_color = (242, 235, 220)
        self.sumi_black = (25, 20, 18)
        self.sumi_gray = (80, 75, 70)
        self.vermillion = (227, 66, 52)
        self.gold_leaf = (212, 175, 55)
        self.indigo = (38, 67, 72)
        
        # Animation
        self.time = 0
        
        # Configuration des options
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.settings = self.load_settings()
        
        # Options disponibles
        self.options = [
            {
                "name": "Volume Musique",
                "type": "slider",
                "key": "music_volume",
                "min": 0,
                "max": 100,
                "step": 5
            },
            {
                "name": "Volume Effets",
                "type": "slider",
                "key": "sfx_volume",
                "min": 0,
                "max": 100,
                "step": 5
            },
            {
                "name": "Plein Écran",
                "type": "toggle",
                "key": "fullscreen"
            },
            {
                "name": "Résolution",
                "type": "choice",
                "key": "resolution",
                "choices": ["1280x720", "1600x900", "1920x1080", "2560x1440"]
            },
            {
                "name": "Qualité Graphique",
                "type": "choice",
                "key": "graphics_quality",
                "choices": ["Faible", "Moyenne", "Élevée", "Ultra"]
            },
            {
                "name": "Particules",
                "type": "toggle",
                "key": "particles"
            },
            {
                "name": "Animations",
                "type": "toggle",
                "key": "animations"
            },
            {
                "name": "Vibration Manette",
                "type": "toggle",
                "key": "vibration"
            },
            {
                "name": "Langue",
                "type": "choice",
                "key": "language",
                "choices": ["Français", "English", "日本語"]
            },
            {
                "name": "Limite FPS",
                "type": "choice",
                "key": "fps_limit",
                "choices": ["30", "60", "120", "Illimité"]
            },
            {
                "name": "Vsync",
                "type": "toggle",
                "key": "vsync"
            },
            {
                "name": "Conseils Tutoriel",
                "type": "toggle",
                "key": "tutorial_tips"
            }
        ]
        
        self.selected_option = 0
        self.is_adjusting = False
        
        # Message de confirmation
        self.save_message = ""
        self.save_message_timer = 0
        
        # Polices
        try:
            self.title_font = pygame.font.SysFont('cinzel, trajan, georgia', 70, bold=True)
            self.option_font = pygame.font.SysFont('cinzel, trajan, georgia', 32)
            self.value_font = pygame.font.SysFont('cinzel, trajan, georgia', 28, bold=True)
            self.button_font = pygame.font.SysFont('cinzel, trajan, georgia', 36)
        except:
            self.title_font = pygame.font.Font(None, 70)
            self.option_font = pygame.font.Font(None, 32)
            self.value_font = pygame.font.Font(None, 28)
            self.button_font = pygame.font.Font(None, 36)
        
        # Zone de défilement
        self.scroll_offset = 0
        self.max_visible_options = 6
    
    def load_settings(self):
        """Charge les paramètres depuis le fichier config"""
        default_settings = {
            "music_volume": 70,
            "sfx_volume": 80,
            "fullscreen": False,
            "resolution": "1280x720",
            "graphics_quality": "Élevée",
            "particles": True,
            "animations": True,
            "vibration": True,
            "language": "Français",
            "fps_limit": "60",
            "vsync": True,
            "tutorial_tips": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Fusionner avec les paramètres par défaut
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Sauvegarde les paramètres dans le fichier config"""
        try:
            # S'assurer que le dossier parent existe
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            print(f"Paramètres sauvegardés dans : {self.config_file}")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")
            print(f"Chemin du fichier: {self.config_file}")
            return False
    
    def draw_background(self):
        """Dessine le fond style papier washi"""
        self.screen.fill(self.washi_color)
        
        # Bordures
        border_width = 40
        pygame.draw.rect(self.screen, self.indigo, (0, 0, border_width, self.height))
        pygame.draw.line(self.screen, self.gold_leaf, (border_width-2, 0), (border_width-2, self.height), 2)
        pygame.draw.rect(self.screen, self.indigo, (self.width - border_width, 0, border_width, self.height))
        pygame.draw.line(self.screen, self.gold_leaf, (self.width - border_width+2, 0), (self.width - border_width+2, self.height), 2)
    
    def draw_title(self):
        """Dessine le titre"""
        title_text = "OPTIONS"
        
        # Cartouche
        cartouche_width = 350
        cartouche_height = 100
        cartouche_y = 80
        
        cart_surf = pygame.Surface((cartouche_width, cartouche_height), pygame.SRCALPHA)
        pygame.draw.rect(cart_surf, (*self.vermillion, 220), (0, 0, cartouche_width, cartouche_height))
        pygame.draw.rect(cart_surf, self.gold_leaf, (0, 0, cartouche_width, cartouche_height), 4)
        
        cart_rect = cart_surf.get_rect(center=(self.width // 2, cartouche_y))
        self.screen.blit(cart_surf, cart_rect)
        
        # Titre
        title_surf = self.title_font.render(title_text, True, self.washi_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, cartouche_y))
        self.screen.blit(title_surf, title_rect)
    
    def draw_option(self, option, index, y_pos):
        """Dessine une option individuelle"""
        is_selected = (index == self.selected_option)
        center_x = self.width // 2
        mouse_pos = pygame.mouse.get_pos()
        
        # Zone cliquable pour l'option
        option_rect = pygame.Rect(center_x - 350, y_pos - 27, 700, 55)
        option["rect"] = option_rect
        
        # Détection du survol de la souris (instantanée)
        is_hovered = option_rect.collidepoint(mouse_pos)
        if is_hovered:
            self.selected_option = index
            is_selected = True
        
        # Fond si sélectionné
        if is_selected:
            bg_width = 700
            bg_height = 55
            bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*self.washi_color, 240), (0, 0, bg_width, bg_height))
            pygame.draw.rect(bg_surf, self.vermillion, (0, 0, bg_width, bg_height), 3)
            
            bg_rect = bg_surf.get_rect(center=(center_x, y_pos))
            self.screen.blit(bg_surf, bg_rect)
        
        # Nom de l'option (à gauche)
        color = self.sumi_black if is_selected else self.sumi_gray
        name_surf = self.option_font.render(option["name"], True, color)
        name_rect = name_surf.get_rect(midleft=(center_x - 320, y_pos))
        self.screen.blit(name_surf, name_rect)
        
        # Valeur de l'option (à droite)
        value_color = self.vermillion if is_selected else self.sumi_gray
        
        if option["type"] == "slider":
            # Barre de progression
            slider_width = 200
            slider_height = 10
            slider_x = center_x + 50
            
            # Zone cliquable du slider
            slider_rect = pygame.Rect(slider_x, y_pos - 15, slider_width, 30)
            option["slider_rect"] = slider_rect
            
            # Fond de la barre
            pygame.draw.rect(self.screen, self.sumi_gray, 
                           (slider_x, y_pos - slider_height//2, slider_width, slider_height))
            
            # Barre de progression
            value = self.settings[option["key"]]
            progress = value / option["max"]
            pygame.draw.rect(self.screen, self.vermillion, 
                           (slider_x, y_pos - slider_height//2, 
                            int(slider_width * progress), slider_height))
            
            # Texte de valeur
            value_text = f"{value}%"
            value_surf = self.value_font.render(value_text, True, value_color)
            value_rect = value_surf.get_rect(midleft=(slider_x + slider_width + 15, y_pos))
            self.screen.blit(value_surf, value_rect)
        
        elif option["type"] == "toggle":
            # Bouton toggle
            toggle_width = 80
            toggle_height = 30
            toggle_x = center_x + 150
            
            value = self.settings[option["key"]]
            bg_color = self.vermillion if value else self.sumi_gray
            
            # Zone cliquable du toggle
            toggle_rect = pygame.Rect(toggle_x, y_pos - toggle_height//2, toggle_width, toggle_height)
            option["toggle_rect"] = toggle_rect
            
            # Fond du toggle
            pygame.draw.rect(self.screen, bg_color, 
                           (toggle_x, y_pos - toggle_height//2, toggle_width, toggle_height),
                           border_radius=15)
            
            # Cercle du toggle
            circle_x = toggle_x + (toggle_width - 20) if value else toggle_x + 10
            pygame.draw.circle(self.screen, self.washi_color, 
                             (circle_x, y_pos), 12)
            
            # Texte ON/OFF
            text = "ON" if value else "OFF"
            text_surf = self.value_font.render(text, True, value_color)
            text_rect = text_surf.get_rect(midleft=(toggle_x + toggle_width + 15, y_pos))
            self.screen.blit(text_surf, text_rect)
        
        elif option["type"] == "choice":
            # Flèches et choix
            value = self.settings[option["key"]]
            
            # Zone cliquable pour les flèches
            left_arrow_rect = pygame.Rect(center_x + 50, y_pos - 15, 40, 30)
            right_arrow_rect = pygame.Rect(center_x + 240, y_pos - 15, 40, 30)
            option["left_arrow_rect"] = left_arrow_rect
            option["right_arrow_rect"] = right_arrow_rect
            
            # Flèche gauche
            if is_selected:
                left_arrow = "◄"
                right_arrow = "►"
                arrow_surf = self.value_font.render(left_arrow, True, self.gold_leaf)
                arrow_rect = arrow_surf.get_rect(midright=(center_x + 80, y_pos))
                self.screen.blit(arrow_surf, arrow_rect)
            
            # Valeur actuelle
            value_surf = self.value_font.render(str(value), True, value_color)
            value_rect = value_surf.get_rect(center=(center_x + 165, y_pos))
            self.screen.blit(value_surf, value_rect)
            
            # Flèche droite
            if is_selected:
                arrow_surf = self.value_font.render(right_arrow, True, self.gold_leaf)
                arrow_rect = arrow_surf.get_rect(midleft=(center_x + 250, y_pos))
                self.screen.blit(arrow_surf, arrow_rect)
    
    def draw_options(self):
        """Dessine toutes les options visibles"""
        start_y = 200
        spacing = 70
        
        # Calculer quelles options sont visibles
        visible_start = self.scroll_offset
        visible_end = min(visible_start + self.max_visible_options, len(self.options))
        
        for i in range(visible_start, visible_end):
            y_pos = start_y + (i - visible_start) * spacing
            self.draw_option(self.options[i], i, y_pos)
        
        # Indicateurs de défilement
        if self.scroll_offset > 0:
            # Flèche haut
            arrow_surf = self.option_font.render("▲", True, self.vermillion)
            arrow_rect = arrow_surf.get_rect(center=(self.width // 2, start_y - 40))
            self.screen.blit(arrow_surf, arrow_rect)
        
        if visible_end < len(self.options):
            # Flèche bas
            arrow_surf = self.option_font.render("▼", True, self.vermillion)
            arrow_rect = arrow_surf.get_rect(center=(self.width // 2, start_y + self.max_visible_options * spacing + 20))
            self.screen.blit(arrow_surf, arrow_rect)
    
    def draw_buttons(self):
        """Dessine les boutons Sauvegarder et Retour"""
        button_y = self.height - 80
        
        # Message de confirmation si présent
        if self.save_message and self.save_message_timer > 0:
            msg_surf = self.button_font.render(self.save_message, True, self.vermillion)
            msg_rect = msg_surf.get_rect(center=(self.width // 2, button_y - 60))
            
            # Fond pour le message
            padding = 15
            bg_rect = pygame.Rect(msg_rect.x - padding, msg_rect.y - padding//2,
                                 msg_rect.width + padding*2, msg_rect.height + padding)
            pygame.draw.rect(self.screen, (*self.washi_color, 240), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.vermillion, bg_rect, 2, border_radius=5)
            
            self.screen.blit(msg_surf, msg_rect)
        
        # Bouton Sauvegarder
        save_text = "Sauvegarder"
        save_surf = self.button_font.render(save_text, True, self.sumi_black)
        save_rect = save_surf.get_rect(center=(self.width // 2 - 150, button_y))
        
        pygame.draw.rect(self.screen, self.washi_color, 
                        (save_rect.x - 20, save_rect.y - 10, save_rect.width + 40, save_rect.height + 20))
        pygame.draw.rect(self.screen, self.vermillion, 
                        (save_rect.x - 20, save_rect.y - 10, save_rect.width + 40, save_rect.height + 20), 3)
        self.screen.blit(save_surf, save_rect)
        
        # Bouton Retour
        back_text = "Retour"
        back_surf = self.button_font.render(back_text, True, self.sumi_black)
        back_rect = back_surf.get_rect(center=(self.width // 2 + 150, button_y))
        
        pygame.draw.rect(self.screen, self.washi_color, 
                        (back_rect.x - 20, back_rect.y - 10, back_rect.width + 40, back_rect.height + 20))
        pygame.draw.rect(self.screen, self.indigo, 
                        (back_rect.x - 20, back_rect.y - 10, back_rect.width + 40, back_rect.height + 20), 3)
        self.screen.blit(back_surf, back_rect)
        
        # Stocker les rectangles pour la détection de clic
        self.save_button_rect = pygame.Rect(save_rect.x - 20, save_rect.y - 10, 
                                            save_rect.width + 40, save_rect.height + 20)
        self.back_button_rect = pygame.Rect(back_rect.x - 20, back_rect.y - 10, 
                                            back_rect.width + 40, back_rect.height + 20)
    
    def adjust_option(self, direction):
        """Ajuste la valeur de l'option sélectionnée"""
        option = self.options[self.selected_option]
        key = option["key"]
        
        if option["type"] == "slider":
            current = self.settings[key]
            step = option["step"]
            new_value = current + (step * direction)
            self.settings[key] = max(option["min"], min(option["max"], new_value))
        
        elif option["type"] == "toggle":
            self.settings[key] = not self.settings[key]
        
        elif option["type"] == "choice":
            choices = option["choices"]
            current_index = choices.index(self.settings[key])
            new_index = (current_index + direction) % len(choices)
            self.settings[key] = choices[new_index]
    
    def handle_events(self):
        """Gère les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = max(0, self.selected_option - 1)
                    # Ajuster le défilement
                    if self.selected_option < self.scroll_offset:
                        self.scroll_offset = self.selected_option
                
                elif event.key == pygame.K_DOWN:
                    self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
                    # Ajuster le défilement
                    if self.selected_option >= self.scroll_offset + self.max_visible_options:
                        self.scroll_offset = self.selected_option - self.max_visible_options + 1
                
                elif event.key == pygame.K_LEFT:
                    self.adjust_option(-1)
                
                elif event.key == pygame.K_RIGHT:
                    self.adjust_option(1)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    option = self.options[self.selected_option]
                    if option["type"] == "toggle":
                        self.adjust_option(0)
                
                elif event.key == pygame.K_ESCAPE:
                    self.save_settings()
                    return "back"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # Vérifier les boutons de contrôle
                    if hasattr(self, 'save_button_rect') and self.save_button_rect.collidepoint(event.pos):
                        if self.save_settings():
                            self.save_message = "✓ Paramètres sauvegardés!"
                            self.save_message_timer = 120  # ~2 secondes à 60 FPS
                        else:
                            self.save_message = "✗ Erreur de sauvegarde"
                            self.save_message_timer = 120
                        return "back"  # Retour au menu principal après sauvegarde
                    elif hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(event.pos):
                        self.save_settings()
                        return "back"
                    
                    # Vérifier les clics sur les options
                    for i, option in enumerate(self.options):
                        # Vérifier si on clique sur le slider
                        if option["type"] == "slider" and "slider_rect" in option:
                            if option["slider_rect"].collidepoint(event.pos):
                                self.selected_option = i
                                # Calculer la nouvelle valeur basée sur la position du clic
                                slider_x = self.width // 2 + 50
                                slider_width = 200
                                click_x = event.pos[0] - slider_x
                                progress = max(0, min(1, click_x / slider_width))
                                new_value = int(progress * option["max"])
                                # Arrondir à l'incrément le plus proche
                                step = option["step"]
                                new_value = round(new_value / step) * step
                                self.settings[option["key"]] = max(option["min"], min(option["max"], new_value))
                        
                        # Vérifier si on clique sur le toggle
                        elif option["type"] == "toggle" and "toggle_rect" in option:
                            if option["toggle_rect"].collidepoint(event.pos):
                                self.selected_option = i
                                self.adjust_option(0)
                        
                        # Vérifier si on clique sur les flèches des choix
                        elif option["type"] == "choice":
                            if "left_arrow_rect" in option and option["left_arrow_rect"].collidepoint(event.pos):
                                self.selected_option = i
                                self.adjust_option(-1)
                            elif "right_arrow_rect" in option and option["right_arrow_rect"].collidepoint(event.pos):
                                self.selected_option = i
                                self.adjust_option(1)
            
            # Support de la molette de souris pour le défilement
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Molette vers le haut
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.y < 0:  # Molette vers le bas
                    max_scroll = max(0, len(self.options) - self.max_visible_options)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        return None
    
    def run(self):
        """Boucle principale du menu options"""
        while self.running:
            self.time += 0.016
            
            # Décrémenter le timer du message de sauvegarde
            if self.save_message_timer > 0:
                self.save_message_timer -= 1
            
            action = self.handle_events()
            
            if action == "quit":
                return "quit"
            elif action == "back":
                return "back"
            
            # Rendu
            self.draw_background()
            self.draw_title()
            self.draw_options()
            self.draw_buttons()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "back"
