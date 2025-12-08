import pygame
import sys
import math
import random
import os
from options_menu import OptionsMenu


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Palette Japon féodal - couleurs traditionnelles
        self.washi_color = (242, 235, 220)  # Couleur papier washi (beige crème)
        self.sumi_black = (25, 20, 18)  # Noir encre de Chine
        self.sumi_gray = (80, 75, 70)  # Gris encre diluée
        self.vermillion = (227, 66, 52)  # Vermillon (shu-iro)
        self.gold_leaf = (212, 175, 55)  # Or feuille d'or
        self.indigo = (38, 67, 72)  # Indigo (ai-iro)
        self.bamboo_green = (104, 125, 90)  # Vert bambou
        
        # Charger le logo
        self.logo = None
        self.logo_rect = None
        self.load_logo()
        
        # Animation
        self.time = 0
        self.particles = []
        self.brush_strokes = []
        self.init_particles()
        self.create_brush_strokes()
        
        # Boutons du menu avec kanjis
        self.buttons = [
            {"text": "Nouvelle Partie", "action": "new_game", "y_offset": -80},
            {"text": "Collection", "action": "collection", "y_offset": -20},
            {"text": "Options", "action": "options", "y_offset": 40},
            {"text": "Quitter", "action": "quit", "y_offset": 100}
        ]
        self.selected_button = 0
        
        # Bouton plein écran
        self.fullscreen_button_rect = pygame.Rect(self.width - 70, self.height - 70, 50, 50)
        self.fullscreen_hover = False
        self.is_fullscreen = False
        
        # Polices - style Ghost of Tsushima / calligraphie
        try:
            # Chercher une police système style asiatique/calligraphie
            # Similaire à Ghost of Tsushima qui utilise des polices élégantes
            self.title_font = pygame.font.SysFont('cinzel, trajan, georgia, times new roman', 90, bold=True)
            self.button_font = pygame.font.SysFont('cinzel, trajan, georgia, times new roman', 44, bold=False)
            self.subtitle_font = pygame.font.SysFont('cinzel, trajan, georgia, times new roman', 32)
        except:
            self.title_font = pygame.font.Font(None, 90)
            self.button_font = pygame.font.Font(None, 44)
            self.subtitle_font = pygame.font.Font(None, 32)
    
    def load_logo(self):
        """Charge l'image du logo"""
        try:
            # Chemin relatif depuis src/ vers assets/images/
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'raw.png')
            self.logo = pygame.image.load(logo_path).convert_alpha()
            
            # Redimensionner le logo pour qu'il soit adapté au menu
            # Hauteur maximale de 250 pixels
            logo_height = 250
            aspect_ratio = self.logo.get_width() / self.logo.get_height()
            logo_width = int(logo_height * aspect_ratio)
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
            
            # Position du logo
            self.logo_rect = self.logo.get_rect(center=(self.width // 2, 150))
            
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            self.logo = None
    
    def create_brush_strokes(self):
        """Crée des traits de pinceau décoratifs"""
        # Traits de pinceau horizontaux et verticaux style sumi-e
        self.brush_strokes = [
            {"x": 50, "y": 100, "width": 200, "height": 3, "angle": -5},
            {"x": self.width - 250, "y": 150, "width": 180, "height": 4, "angle": 3},
            {"x": 80, "y": self.height - 120, "width": 150, "height": 3, "angle": 2},
            {"x": self.width - 200, "y": self.height - 100, "width": 160, "height": 3, "angle": -3},
        ]
    
    def init_particles(self):
        """Initialise les particules de pétales de cerisier et feuilles"""
        for i in range(40):
            self.particles.append({
                "x": random.randint(0, self.width),
                "y": random.randint(-self.height, 0),
                "speed": 0.3 + random.random() * 0.5,
                "offset": random.random() * math.pi * 2,
                "size": 3 + random.randint(0, 4),
                "type": random.choice(["sakura", "leaf", "ink"])
            })
    
    def update_particles(self):
        """Met à jour la position des particules"""
        for particle in self.particles:
            particle["y"] += particle["speed"]
            particle["x"] += math.sin(self.time * 0.8 + particle["offset"]) * 0.8
            
            # Rotation pour effet de chute
            particle["rotation"] = (self.time * 2 + particle["offset"]) % (math.pi * 2)
            
            # Réinitialiser la particule en haut si elle sort de l'écran
            if particle["y"] > self.height + 20:
                particle["y"] = -20
                particle["x"] = random.randint(0, self.width)
    
    def draw_brush_stroke(self, x, y, width, height, angle, alpha=180):
        """Dessine un trait de pinceau avec effet sumi-e"""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Créer un dégradé pour simuler l'encre qui s'estompe
        for i in range(width):
            fade = 1.0 - abs((i - width/2) / (width/2)) * 0.5
            color_alpha = int(alpha * fade)
            color = (*self.sumi_gray, color_alpha)
            pygame.draw.line(surf, color, (i, 0), (i, height))
        
        # Rotation du trait
        surf = pygame.transform.rotate(surf, angle)
        rect = surf.get_rect(center=(x, y))
        self.screen.blit(surf, rect)
    
    def draw_particles(self):
        """Dessine les particules style japonais"""
        for particle in self.particles:
            if particle["type"] == "sakura":
                # Pétale de cerisier rose pâle
                alpha = int(160 + 95 * math.sin(self.time * 0.5 + particle["offset"]))
                color = (255, 190, 200, alpha)
            elif particle["type"] == "leaf":
                # Feuille d'érable (momiji)
                alpha = int(140 + 80 * math.sin(self.time * 0.3 + particle["offset"]))
                color = (200, 80, 60, alpha)
            else:
                # Goutte d'encre
                alpha = int(100 + 60 * math.sin(self.time * 0.4 + particle["offset"]))
                color = (*self.sumi_gray, alpha)
            
            surf = pygame.Surface((particle["size"] * 3, particle["size"] * 2), pygame.SRCALPHA)
            
            if particle["type"] == "sakura":
                # Forme de pétale
                points = [
                    (particle["size"] * 1.5, 0),
                    (particle["size"] * 3, particle["size"]),
                    (particle["size"] * 1.5, particle["size"] * 2),
                    (0, particle["size"])
                ]
                pygame.draw.polygon(surf, color, points)
            else:
                # Ellipse simple
                pygame.draw.ellipse(surf, color, (0, 0, particle["size"] * 3, particle["size"] * 2))
            
            # Rotation
            surf = pygame.transform.rotate(surf, math.degrees(particle.get("rotation", 0)))
            rect = surf.get_rect(center=(int(particle["x"]), int(particle["y"])))
            self.screen.blit(surf, rect)
    
    def draw_background(self):
        """Dessine le fond style papier washi ancien"""
        # Fond couleur washi (papier japonais)
        self.screen.fill(self.washi_color)
        
        # Texture papier - petites taches aléatoires
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            alpha = random.randint(5, 20)
            size = random.randint(1, 3)
            color = (self.sumi_black[0], self.sumi_black[1], self.sumi_black[2], alpha)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill(color)
            self.screen.blit(surf, (x, y))
        
        # Bordure style kakejiku (rouleau suspendu)
        border_width = 40
        # Bord gauche
        pygame.draw.rect(self.screen, self.indigo, (0, 0, border_width, self.height))
        pygame.draw.line(self.screen, self.gold_leaf, (border_width-2, 0), (border_width-2, self.height), 2)
        # Bord droit
        pygame.draw.rect(self.screen, self.indigo, (self.width - border_width, 0, border_width, self.height))
        pygame.draw.line(self.screen, self.gold_leaf, (self.width - border_width+2, 0), (self.width - border_width+2, self.height), 2)
        
        # Motif vagues en haut et en bas (seigaiha)
        self.draw_wave_pattern(0, 0, self.width, 60, True)
        self.draw_wave_pattern(0, self.height - 60, self.width, 60, False)
        
        # Traits de pinceau décoratifs
        for stroke in self.brush_strokes:
            self.draw_brush_stroke(stroke["x"], stroke["y"], stroke["width"], 
                                  stroke["height"], stroke["angle"], 120)
        
        # Cercle zen (ensō) en filigrane au centre
        pulse = math.sin(self.time * 0.3) * 3
        circle_center = (self.width // 2, self.height // 2 + 50)
        circle_radius = 180 + pulse
        # Cercle incomplet style calligraphie zen
        for angle in range(20, 340, 2):
            start_angle = math.radians(angle)
            end_angle = math.radians(angle + 1.5)
            start_pos = (circle_center[0] + circle_radius * math.cos(start_angle),
                        circle_center[1] + circle_radius * math.sin(start_angle))
            end_pos = (circle_center[0] + circle_radius * math.cos(end_angle),
                      circle_center[1] + circle_radius * math.sin(end_angle))
            # Variation d'épaisseur pour effet pinceau
            width = 2 + int(abs(math.sin(angle * 0.1)) * 2)
            alpha = 40 + int(abs(math.sin(angle * 0.05)) * 20)
            color = (*self.sumi_gray, alpha)
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(surf, color, start_pos, end_pos, width)
            self.screen.blit(surf, (0, 0))
    
    def draw_wave_pattern(self, x, y, width, height, top=True):
        """Dessine un motif de vagues seigaiha"""
        wave_color = (*self.indigo, 80)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Motif de vagues concentriques
        for i in range(0, width + 60, 60):
            for j in range(3):
                radius = 20 + j * 15
                if top:
                    pygame.draw.arc(surf, wave_color, (i - 30, height - 40, 60, 60), 
                                  0, math.pi, 2)
                else:
                    pygame.draw.arc(surf, wave_color, (i - 30, -20, 60, 60), 
                                  math.pi, math.pi * 2, 2)
        
        self.screen.blit(surf, (x, y))
    
    def draw_title(self):
        """Dessine le logo et le titre avec style calligraphie japonaise"""
        subtitle_text = "Shimatori TCG"
        
        center_x = self.width // 2
        
        # Si le logo est chargé, l'afficher sans décorations
        if self.logo and self.logo_rect:
            logo_y = 150
            
            # Afficher le logo simplement
            logo_rect_positioned = self.logo.get_rect(center=(center_x, logo_y))
            self.screen.blit(self.logo, logo_rect_positioned)
            
            subtitle_y = logo_y + self.logo_rect.height//2 + 60
            
        else:
            # Si le logo ne charge pas, afficher le texte de fallback
            title_text = "SHIMATORI"
            cartouche_width = 400
            cartouche_height = 160
            cartouche_y = 120
            
            # Fond du cartouche avec effet vieilli
            cart_surf = pygame.Surface((cartouche_width, cartouche_height), pygame.SRCALPHA)
            pygame.draw.rect(cart_surf, (*self.vermillion, 220), (0, 0, cartouche_width, cartouche_height))
            pygame.draw.rect(cart_surf, self.gold_leaf, (0, 0, cartouche_width, cartouche_height), 4)
            
            cart_rect = cart_surf.get_rect(center=(center_x, cartouche_y))
            self.screen.blit(cart_surf, cart_rect)
            
            # Titre principal
            title_surf = self.title_font.render(title_text, True, self.washi_color)
            title_rect = title_surf.get_rect(center=(center_x, cartouche_y))
            self.screen.blit(title_surf, title_rect)
            
            subtitle_y = cartouche_y + 100
        
        # Sous-titre avec effet calligraphie (sans sceau)
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, self.sumi_black)
        subtitle_rect = subtitle_surf.get_rect(center=(center_x, subtitle_y))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Lignes verticales décoratives style kakejiku
        line_x1 = center_x - 250
        line_x2 = center_x + 250
        line_top = subtitle_y - 180
        line_bottom = subtitle_y + 30
        pygame.draw.line(self.screen, self.sumi_gray, (line_x1, line_top), 
                        (line_x1, line_bottom), 2)
        pygame.draw.line(self.screen, self.sumi_gray, (line_x2, line_top), 
                        (line_x2, line_bottom), 2)
    
    def draw_buttons(self):
        """Dessine les boutons du menu style calligraphie"""
        center_y = self.height // 2 + 180
        mouse_pos = pygame.mouse.get_pos()
        
        for i, button in enumerate(self.buttons):
            y_pos = center_y + button["y_offset"]
            is_selected = (i == self.selected_button)
            
            # Position et animation
            if is_selected:
                pulse = math.sin(self.time * 4) * 3
                x_offset = pulse
                scale = 1.0
            else:
                x_offset = 0
                scale = 0.95
            
            center_x = self.width // 2 + x_offset
            
            # Fond du bouton - cartouche style kakejiku
            button_width = 320
            button_height = 60
            
            # Créer le rectangle de collision pour la souris
            button_rect = pygame.Rect(center_x - button_width//2, y_pos - button_height//2, 
                                     button_width, button_height)
            button["rect"] = button_rect
            
            # Vérifier si la souris survole ce bouton
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered and not is_selected:
                self.selected_button = i
                is_selected = True
            
            if is_selected:
                # Rectangle de fond beige clair
                bg_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (*self.washi_color, 240), (0, 0, button_width, button_height))
                
                # Bordure vermillon épaisse
                pygame.draw.rect(bg_surf, self.vermillion, (0, 0, button_width, button_height), 4)
                
                # Coins dorés
                corner_size = 12
                for corner in [(0, 0), (button_width-corner_size, 0), 
                              (0, button_height-corner_size), 
                              (button_width-corner_size, button_height-corner_size)]:
                    pygame.draw.rect(bg_surf, self.gold_leaf, 
                                   (corner[0], corner[1], corner_size, corner_size))
                
                bg_rect = bg_surf.get_rect(center=(center_x, y_pos))
                self.screen.blit(bg_surf, bg_rect)
            
            # Texte du bouton
            font_size = int(44 * scale)
            button_font = pygame.font.SysFont('cinzel, trajan, georgia, times new roman', font_size, bold=False)
            
            # Ombre du texte
            if is_selected:
                shadow_surf = button_font.render(button["text"], True, self.sumi_black)
                shadow_rect = shadow_surf.get_rect(center=(center_x + 2, y_pos + 2))
                shadow_surf.set_alpha(100)
                self.screen.blit(shadow_surf, shadow_rect)
            
            # Texte principal
            color = self.sumi_black if is_selected else self.sumi_gray
            text_surf = button_font.render(button["text"], True, color)
            text_rect = text_surf.get_rect(center=(center_x, y_pos))
            self.screen.blit(text_surf, text_rect)
            
            # Marqueurs de sélection - triangles style flèche
            if is_selected:
                marker_offset = int(12 + math.sin(self.time * 5) * 4)
                # Triangle gauche
                left_points = [
                    (text_rect.left - 40 - marker_offset, y_pos),
                    (text_rect.left - 50 - marker_offset, y_pos - 8),
                    (text_rect.left - 50 - marker_offset, y_pos + 8)
                ]
                pygame.draw.polygon(self.screen, self.vermillion, left_points)
                pygame.draw.polygon(self.screen, self.gold_leaf, left_points, 2)
                
                # Triangle droit
                right_points = [
                    (text_rect.right + 40 + marker_offset, y_pos),
                    (text_rect.right + 50 + marker_offset, y_pos - 8),
                    (text_rect.right + 50 + marker_offset, y_pos + 8)
                ]
                pygame.draw.polygon(self.screen, self.vermillion, right_points)
                pygame.draw.polygon(self.screen, self.gold_leaf, right_points, 2)
    
    def draw_fullscreen_button(self):
        """Dessine le bouton plein écran en bas à droite"""
        # Vérifier si la souris survole le bouton
        mouse_pos = pygame.mouse.get_pos()
        self.fullscreen_hover = self.fullscreen_button_rect.collidepoint(mouse_pos)
        
        # Animation hover
        if self.fullscreen_hover:
            scale = 1.1 + math.sin(self.time * 5) * 0.05
            color = self.vermillion
            border_color = self.gold_leaf
        else:
            scale = 1.0
            color = self.indigo
            border_color = self.sumi_gray
        
        # Centre du bouton
        center_x = self.fullscreen_button_rect.centerx
        center_y = self.fullscreen_button_rect.centery
        
        # Fond du bouton
        button_size = int(50 * scale)
        button_surf = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, (*self.washi_color, 240), (0, 0, button_size, button_size), border_radius=5)
        pygame.draw.rect(button_surf, color, (0, 0, button_size, button_size), 3, border_radius=5)
        
        # Icône plein écran (deux rectangles - un petit et un grand)
        if self.is_fullscreen:
            # Icône pour quitter le plein écran (deux rectangles qui se chevauchent)
            icon_size = int(18 * scale)
            offset = 3
            # Petit rectangle (avant-plan)
            pygame.draw.rect(button_surf, color, 
                           (button_size//2 - icon_size//2 + offset, button_size//2 - icon_size//2 + offset, 
                            icon_size - offset*2, icon_size - offset*2), 2)
            # Grand rectangle (arrière-plan)
            pygame.draw.rect(button_surf, border_color, 
                           (button_size//2 - icon_size//2 - offset, button_size//2 - icon_size//2 - offset, 
                            icon_size - offset*2, icon_size - offset*2), 2)
        else:
            # Icône pour passer en plein écran (rectangle avec flèches aux coins)
            icon_size = int(20 * scale)
            # Rectangle central
            pygame.draw.rect(button_surf, color, 
                           (button_size//2 - icon_size//2, button_size//2 - icon_size//2, 
                            icon_size, icon_size), 2)
            # Flèches aux coins
            arrow_size = 5
            # Coin haut-gauche
            pygame.draw.line(button_surf, border_color,
                           (button_size//2 - icon_size//2, button_size//2 - icon_size//2 + arrow_size),
                           (button_size//2 - icon_size//2, button_size//2 - icon_size//2), 2)
            pygame.draw.line(button_surf, border_color,
                           (button_size//2 - icon_size//2, button_size//2 - icon_size//2),
                           (button_size//2 - icon_size//2 + arrow_size, button_size//2 - icon_size//2), 2)
            # Coin bas-droit
            pygame.draw.line(button_surf, border_color,
                           (button_size//2 + icon_size//2, button_size//2 + icon_size//2 - arrow_size),
                           (button_size//2 + icon_size//2, button_size//2 + icon_size//2), 2)
            pygame.draw.line(button_surf, border_color,
                           (button_size//2 + icon_size//2 - arrow_size, button_size//2 + icon_size//2),
                           (button_size//2 + icon_size//2, button_size//2 + icon_size//2), 2)
        
        # Afficher le bouton
        button_rect = button_surf.get_rect(center=(center_x, center_y))
        self.screen.blit(button_surf, button_rect)
        
        # Texte d'aide au survol
        if self.fullscreen_hover:
            help_text = "Plein écran" if not self.is_fullscreen else "Fenêtré"
            help_font = pygame.font.SysFont('arial', 16)
            help_surf = help_font.render(help_text, True, self.sumi_black)
            help_rect = help_surf.get_rect(midright=(center_x - 35, center_y))
            
            # Fond pour le texte
            padding = 5
            bg_rect = pygame.Rect(help_rect.x - padding, help_rect.y - padding//2,
                                 help_rect.width + padding*2, help_rect.height + padding)
            pygame.draw.rect(self.screen, (*self.washi_color, 220), bg_rect, border_radius=3)
            pygame.draw.rect(self.screen, self.sumi_gray, bg_rect, 1, border_radius=3)
            
            self.screen.blit(help_surf, help_rect)
    
    def toggle_fullscreen(self):
        """Bascule entre mode fenêtré et plein écran"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720))
        
        # Mettre à jour les dimensions
        self.width, self.height = self.screen.get_size()
        
        # Repositionner le bouton plein écran
        self.fullscreen_button_rect = pygame.Rect(self.width - 70, self.height - 70, 50, 50)
    
    def handle_events(self):
        """Gère les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.buttons[self.selected_button]["action"]
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key == pygame.K_F11:
                    # F11 pour basculer en plein écran
                    self.toggle_fullscreen()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # Vérifier si on clique sur le bouton plein écran
                    if self.fullscreen_button_rect.collidepoint(event.pos):
                        self.toggle_fullscreen()
                    else:
                        # Vérifier si on clique sur un bouton du menu
                        for button in self.buttons:
                            if "rect" in button and button["rect"].collidepoint(event.pos):
                                return button["action"]
        
        return None
    
    def run(self):
        """Boucle principale du menu"""
        while self.running:
            self.time += 0.016  # ~60 FPS
            
            # Gérer les événements
            action = self.handle_events()
            
            if action == "quit":
                return "quit"
            elif action == "new_game":
                return "new_game"
            elif action == "collection":
                return "collection"
            elif action == "options":
                return "options"
            
            # Mise à jour
            self.update_particles()
            
            # Rendu
            self.draw_background()
            self.draw_particles()
            self.draw_title()
            self.draw_buttons()
            self.draw_fullscreen_button()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "quit"


def main():
    """Point d'entrée principal du jeu"""
    pygame.init()
    
    # Charger et définir l'icône de la fenêtre
    try:
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'raw.png')
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Impossible de charger l'icône: {e}")
    
    # Configuration de la fenêtre
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Shimatori TCG")
    
    # Boucle principale du jeu
    while True:
        # Lancer le menu principal
        menu = Menu(screen)
        result = menu.run()
        
        if result == "quit":
            break
        elif result == "options":
            # Lancer le menu options
            options_menu = OptionsMenu(screen)
            options_result = options_menu.run()
            if options_result == "quit":
                break
        elif result == "new_game":
            print("Lancement d'une nouvelle partie...")
            # TODO: Implémenter le gameplay
        elif result == "collection":
            print("Ouverture de la collection...")
            # TODO: Implémenter la collection
    
    # Quitter proprement
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
