import pygame
import sys
import math
import json
import os


class CollectionMenu:
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
        
        # Charger les cartes
        self.cards_file = os.path.join(os.path.dirname(__file__), '..', 'cards.json')
        self.cards = self.load_cards()
        
        # Navigation
        self.selected_card = 0
        self.scroll_offset = 0
        self.cards_per_row = 4
        self.card_width = 180
        self.card_height = 260
        self.card_spacing = 20
        self.detail_view = False  # Vue détaillée d'une carte
        
        # Polices
        try:
            self.title_font = pygame.font.SysFont('cinzel, trajan, georgia', 60, bold=True)
            self.card_name_font = pygame.font.SysFont('cinzel, trajan, georgia', 22, bold=True)
            self.card_info_font = pygame.font.SysFont('cinzel, trajan, georgia', 18)
            self.detail_font = pygame.font.SysFont('cinzel, trajan, georgia', 24)
            self.detail_label_font = pygame.font.SysFont('cinzel, trajan, georgia', 20, bold=True)
            self.detail_text_font = pygame.font.SysFont('cinzel, trajan, georgia', 18)
        except:
            self.title_font = pygame.font.Font(None, 60)
            self.card_name_font = pygame.font.Font(None, 22)
            self.card_info_font = pygame.font.Font(None, 18)
            self.detail_font = pygame.font.Font(None, 24)
            self.detail_label_font = pygame.font.Font(None, 20)
            self.detail_text_font = pygame.font.Font(None, 18)
    
    def load_cards(self):
        """Charge les données des cartes depuis le fichier JSON"""
        try:
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('cards', [])
        except Exception as e:
            print(f"Erreur lors du chargement des cartes: {e}")
            return []
    
    def draw_background(self):
        """Dessine le fond style washi avec motifs"""
        self.screen.fill(self.washi_color)
        
        # Bordure indigo
        pygame.draw.rect(self.screen, self.indigo, (0, 0, self.width, self.height), 8)
        
        # Motif de vagues seigaiha subtil
        wave_color = (*self.indigo, 30)
        for y in range(0, self.height, 40):
            for x in range(0, self.width, 80):
                surf = pygame.Surface((80, 40), pygame.SRCALPHA)
                for i in range(3):
                    radius = 15 + i * 8
                    pygame.draw.arc(surf, wave_color, 
                                  (40 - radius, 20 - radius, radius * 2, radius * 2),
                                  0, math.pi, 2)
                self.screen.blit(surf, (x, y))
    
    def draw_title(self):
        """Dessine le titre de la collection"""
        # Cartouche décoratif
        cartouche_width = 500
        cartouche_height = 80
        cartouche_x = self.width // 2 - cartouche_width // 2
        cartouche_y = 30
        
        # Fond du cartouche
        pygame.draw.rect(self.screen, self.indigo, 
                        (cartouche_x, cartouche_y, cartouche_width, cartouche_height))
        pygame.draw.rect(self.screen, self.gold_leaf, 
                        (cartouche_x, cartouche_y, cartouche_width, cartouche_height), 3)
        
        # Titre
        title_surf = self.title_font.render("Collection", True, self.washi_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, cartouche_y + cartouche_height // 2))
        self.screen.blit(title_surf, title_rect)
        
        # Compteur de cartes
        count_text = f"{len(self.cards)} cartes"
        count_surf = self.card_info_font.render(count_text, True, self.sumi_gray)
        count_rect = count_surf.get_rect(center=(self.width // 2, cartouche_y + cartouche_height + 15))
        self.screen.blit(count_surf, count_rect)
    
    def draw_rarity_stars(self, surface, x, y, rarity):
        """Dessine les étoiles de rareté"""
        star_size = 12
        star_spacing = 15
        total_width = rarity * star_spacing
        start_x = x - total_width // 2
        
        for i in range(rarity):
            star_x = start_x + i * star_spacing
            # Étoile simple (pentagone)
            points = []
            for angle in range(0, 360, 72):
                rad = math.radians(angle - 90)
                px = star_x + math.cos(rad) * star_size
                py = y + math.sin(rad) * star_size
                points.append((px, py))
            pygame.draw.polygon(surface, self.gold_leaf, points)
    
    def draw_card_mini(self, card, x, y, is_selected):
        """Dessine une carte en mode miniature (vue grille)"""
        # Surface de la carte
        card_surf = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        
        # Fond de carte avec texture
        pygame.draw.rect(card_surf, (230, 220, 200), (0, 0, self.card_width, self.card_height))
        
        # Bordure selon rareté
        border_colors = {
            1: self.sumi_gray,
            2: (100, 150, 100),  # Vert
            3: (70, 130, 180),   # Bleu
            4: (147, 112, 219),  # Violet
            5: self.gold_leaf    # Or
        }
        border_color = border_colors.get(card.get('rarete', 1), self.sumi_gray)
        border_width = 4 if is_selected else 3
        pygame.draw.rect(card_surf, border_color, (0, 0, self.card_width, self.card_height), border_width)
        
        # Zone image (placeholder)
        image_height = 140
        pygame.draw.rect(card_surf, self.indigo, (10, 10, self.card_width - 20, image_height))
        
        # Texte placeholder pour l'image
        img_text = card.get('nom', 'Carte')[:2].upper()
        img_surf = self.detail_font.render(img_text, True, self.washi_color)
        img_rect = img_surf.get_rect(center=(self.card_width // 2, 10 + image_height // 2))
        card_surf.blit(img_surf, img_rect)
        
        # Nom de la carte
        name_surf = self.card_name_font.render(card.get('nom', 'Inconnu'), True, self.sumi_black)
        name_rect = name_surf.get_rect(center=(self.card_width // 2, image_height + 25))
        card_surf.blit(name_surf, name_rect)
        
        # Classe
        classe_surf = self.card_info_font.render(card.get('classe', ''), True, self.vermillion)
        classe_rect = classe_surf.get_rect(center=(self.card_width // 2, image_height + 48))
        card_surf.blit(classe_surf, classe_rect)
        
        # Stats
        stats_y = image_height + 70
        # Puissance
        power_text = f"⚔ {card.get('puissance', 0)}"
        power_surf = self.card_info_font.render(power_text, True, self.sumi_black)
        card_surf.blit(power_surf, (15, stats_y))
        
        # Vitalité
        hp_text = f"❤ {card.get('vitalite', 0)}"
        hp_surf = self.card_info_font.render(hp_text, True, self.sumi_black)
        hp_rect = hp_surf.get_rect(right=self.card_width - 15, top=stats_y)
        card_surf.blit(hp_surf, hp_rect)
        
        # Rareté (étoiles)
        self.draw_rarity_stars(card_surf, self.card_width // 2, stats_y + 30, card.get('rarete', 1))
        
        # Édition
        edition_surf = self.card_info_font.render(card.get('edition', ''), True, self.sumi_gray)
        edition_rect = edition_surf.get_rect(center=(self.card_width // 2, self.card_height - 15))
        card_surf.blit(edition_surf, edition_rect)
        
        # Si sélectionné, effet lumineux
        if is_selected:
            highlight = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (*self.vermillion, 40), (0, 0, self.card_width, self.card_height))
            card_surf.blit(highlight, (0, 0))
        
        self.screen.blit(card_surf, (x, y))
        
        return pygame.Rect(x, y, self.card_width, self.card_height)
    
    def draw_card_detail(self, card):
        """Dessine la vue détaillée d'une carte"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, self.width, self.height))
        self.screen.blit(overlay, (0, 0))
        
        # Panneau de détails
        panel_width = 700
        panel_height = 600
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Fond du panneau
        pygame.draw.rect(self.screen, self.washi_color, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.gold_leaf, 
                        (panel_x, panel_y, panel_width, panel_height), 4)
        
        # Contenu
        content_x = panel_x + 40
        content_y = panel_y + 40
        line_height = 35
        
        # Nom
        name_surf = self.title_font.render(card.get('nom', 'Inconnu'), True, self.vermillion)
        self.screen.blit(name_surf, (content_x, content_y))
        content_y += 60
        
        # Classe et Rareté
        classe_text = f"Classe: {card.get('classe', 'Inconnue')}"
        classe_surf = self.detail_text_font.render(classe_text, True, self.sumi_black)
        self.screen.blit(classe_surf, (content_x, content_y))
        
        self.draw_rarity_stars(self.screen, panel_x + panel_width - 100, content_y + 10, 
                              card.get('rarete', 1))
        content_y += line_height
        
        # Description
        desc_label = self.detail_label_font.render("Description:", True, self.indigo)
        self.screen.blit(desc_label, (content_x, content_y))
        content_y += 30
        
        # Découper la description en lignes
        description = card.get('description', '')
        words = description.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.detail_text_font.size(test_line)[0] > panel_width - 80:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines[:3]:  # Max 3 lignes
            line_surf = self.detail_text_font.render(line, True, self.sumi_gray)
            self.screen.blit(line_surf, (content_x, content_y))
            content_y += 25
        
        content_y += 15
        
        # Stats
        stats_label = self.detail_label_font.render("Statistiques:", True, self.indigo)
        self.screen.blit(stats_label, (content_x, content_y))
        content_y += 30
        
        stats_text = f"⚔ Puissance: {card.get('puissance', 0)}/7     ❤ Vitalité: {card.get('vitalite', 0)} HP"
        stats_surf = self.detail_text_font.render(stats_text, True, self.sumi_black)
        self.screen.blit(stats_surf, (content_x, content_y))
        content_y += line_height
        
        # Compétences
        comp_label = self.detail_label_font.render("Compétences:", True, self.indigo)
        self.screen.blit(comp_label, (content_x, content_y))
        content_y += 30
        
        competences = card.get('competences', [])
        for comp in competences:
            comp_surf = self.detail_text_font.render(f"• {comp}", True, self.sumi_black)
            self.screen.blit(comp_surf, (content_x + 20, content_y))
            content_y += 25
        
        content_y += 10
        
        # Forces et Faiblesses
        forces_label = self.detail_label_font.render("Forces:", True, self.indigo)
        self.screen.blit(forces_label, (content_x, content_y))
        content_y += 25
        
        forces = ', '.join(card.get('forces', []))
        forces_surf = self.detail_text_font.render(forces, True, (46, 125, 50))
        self.screen.blit(forces_surf, (content_x + 20, content_y))
        content_y += 30
        
        faiblesses_label = self.detail_label_font.render("Faiblesses:", True, self.indigo)
        self.screen.blit(faiblesses_label, (content_x, content_y))
        content_y += 25
        
        faiblesses = ', '.join(card.get('faiblesses', []))
        faiblesses_surf = self.detail_text_font.render(faiblesses, True, (198, 40, 40))
        self.screen.blit(faiblesses_surf, (content_x + 20, content_y))
        content_y += 35
        
        # Édition
        edition_text = f"Édition: {card.get('edition', 'Standard')}"
        edition_surf = self.detail_text_font.render(edition_text, True, self.sumi_gray)
        self.screen.blit(edition_surf, (content_x, content_y))
        
        # Instruction
        instruction = "[ÉCHAP] Fermer   [←→] Carte suivante/précédente"
        instruction_surf = self.card_info_font.render(instruction, True, self.sumi_gray)
        instruction_rect = instruction_surf.get_rect(center=(self.width // 2, panel_y + panel_height - 20))
        self.screen.blit(instruction_surf, instruction_rect)
    
    def draw_cards_grid(self):
        """Dessine la grille de cartes"""
        start_x = 60
        start_y = 150
        
        for i, card in enumerate(self.cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            x = start_x + col * (self.card_width + self.card_spacing)
            y = start_y + row * (self.card_height + self.card_spacing) - self.scroll_offset
            
            # Ne dessiner que les cartes visibles
            if y + self.card_height > 120 and y < self.height - 20:
                is_selected = (i == self.selected_card)
                card_rect = self.draw_card_mini(card, x, y, is_selected)
                card['rect'] = card_rect
    
    def draw_instructions(self):
        """Dessine les instructions de navigation"""
        instructions = "[←↑↓→] Navigation   [ENTRÉE] Détails   [ÉCHAP] Retour"
        instr_surf = self.card_info_font.render(instructions, True, self.sumi_gray)
        instr_rect = instr_surf.get_rect(center=(self.width // 2, self.height - 30))
        self.screen.blit(instr_surf, instr_rect)
    
    def handle_events(self):
        """Gère les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if self.detail_view:
                    # Navigation en mode détail
                    if event.key == pygame.K_ESCAPE:
                        self.detail_view = False
                    elif event.key == pygame.K_LEFT:
                        self.selected_card = (self.selected_card - 1) % len(self.cards)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_card = (self.selected_card + 1) % len(self.cards)
                else:
                    # Navigation en mode grille
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                    
                    elif event.key == pygame.K_LEFT:
                        if self.selected_card % self.cards_per_row > 0:
                            self.selected_card -= 1
                    
                    elif event.key == pygame.K_RIGHT:
                        if self.selected_card % self.cards_per_row < self.cards_per_row - 1 and \
                           self.selected_card < len(self.cards) - 1:
                            self.selected_card += 1
                    
                    elif event.key == pygame.K_UP:
                        if self.selected_card >= self.cards_per_row:
                            self.selected_card -= self.cards_per_row
                            self.scroll_offset = max(0, self.scroll_offset - self.card_height - self.card_spacing)
                    
                    elif event.key == pygame.K_DOWN:
                        if self.selected_card + self.cards_per_row < len(self.cards):
                            self.selected_card += self.cards_per_row
                            self.scroll_offset += self.card_height + self.card_spacing
                    
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.detail_view = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    mouse_pos = event.pos
                    if self.detail_view:
                        self.detail_view = False
                    else:
                        # Vérifier si on clique sur une carte
                        for i, card in enumerate(self.cards):
                            if 'rect' in card and card['rect'].collidepoint(mouse_pos):
                                self.selected_card = i
                                self.detail_view = True
                                break
                
                elif event.button == 4:  # Molette haut
                    self.scroll_offset = max(0, self.scroll_offset - 30)
                
                elif event.button == 5:  # Molette bas
                    max_scroll = max(0, ((len(self.cards) + self.cards_per_row - 1) // self.cards_per_row) * 
                                   (self.card_height + self.card_spacing) - (self.height - 200))
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 30)
            
            if event.type == pygame.MOUSEMOTION and not self.detail_view:
                # Hover sur les cartes
                mouse_pos = event.pos
                for i, card in enumerate(self.cards):
                    if 'rect' in card and card['rect'].collidepoint(mouse_pos):
                        self.selected_card = i
                        break
        
        return None
    
    def run(self):
        """Boucle principale du menu collection"""
        while self.running:
            self.time += 1
            
            action = self.handle_events()
            if action:
                return action
            
            # Dessin
            self.draw_background()
            self.draw_title()
            
            if not self.detail_view:
                self.draw_cards_grid()
                self.draw_instructions()
            else:
                self.draw_cards_grid()  # Garder la grille en arrière-plan
                if self.selected_card < len(self.cards):
                    self.draw_card_detail(self.cards[self.selected_card])
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "back"
