import pygame
import math
import constants.colors as colors
from utils.game_state import GameState

class CollectionMenu(GameState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        self.cards = self.game.card_manager.get_all_cards()
        
        # --- Paramètres Visuels ---
        self.card_width = 200
        self.card_height = 300
        self.spacing = 25
        
        # --- Polices Spécifiques ---
        try:
            self.font_card_name = pygame.font.SysFont('cinzel, trajan, georgia', 22, bold=True)
            self.font_card_class = pygame.font.SysFont('cinzel, trajan, georgia', 18, bold=False)
            self.font_card_stat = pygame.font.SysFont('arial, sans-serif', 18, bold=True) # Réduit à 18 pour rentrer dans les bulles
            self.font_card_label = pygame.font.SysFont('arial, sans-serif', 10, bold=True)
            
            # Police spécifique pour le TITRE de la vue détail (plus petit que le main menu)
            self.font_detail_title = pygame.font.SysFont('cinzel, trajan, georgia', 60, bold=True)
        except:
            self.font_card_name = pygame.font.Font(None, 24)
            self.font_card_class = pygame.font.Font(None, 20)
            self.font_card_stat = pygame.font.Font(None, 20)
            self.font_card_label = pygame.font.Font(None, 12)
            self.font_detail_title = pygame.font.Font(None, 60)
        
        # Scroll & Nav
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.max_scroll = 0
        self.selected_index = 0
        self.detail_view = False
        
        # Layout
        self.cols = 4
        self.start_x = 0
        self.start_y = 120
        
        self.on_resize(self.width, self.height)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        available_width = width - 100
        self.cols = max(1, available_width // (self.card_width + self.spacing))
        grid_width = self.cols * self.card_width + (self.cols - 1) * self.spacing
        self.start_x = (width - grid_width) // 2
        
        if self.cards:
            rows = math.ceil(len(self.cards) / self.cols)
            total_content_height = rows * (self.card_height + self.spacing)
            visible_height = height - self.start_y - 20
            self.max_scroll = max(0, total_content_height - visible_height)
        else:
            self.max_scroll = 0
        self.target_scroll_y = min(self.target_scroll_y, self.max_scroll)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.change_state("quit")
            
            if event.type == pygame.KEYDOWN:
                if self.detail_view:
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE]:
                        self.detail_view = False
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = (self.selected_index - 1) % len(self.cards)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = (self.selected_index + 1) % len(self.cards)
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.game.change_state("menu")
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = min(len(self.cards)-1, self.selected_index + 1)
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.cards)-1, self.selected_index + self.cols)
                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - self.cols)
                    elif event.key == pygame.K_RETURN:
                        self.detail_view = True
                    self.ensure_visible(self.selected_index)

            if event.type == pygame.MOUSEWHEEL:
                self.target_scroll_y = max(0, min(self.max_scroll, self.target_scroll_y - event.y * 60))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.detail_view:
                        self.detail_view = False
                    else:
                        mouse_pos = pygame.mouse.get_pos()
                        adj_y = mouse_pos[1] - self.start_y + self.scroll_y
                        col = (mouse_pos[0] - self.start_x) // (self.card_width + self.spacing)
                        row = adj_y // (self.card_height + self.spacing)
                        index = int(row * self.cols + col)
                        
                        if 0 <= col < self.cols and 0 <= index < len(self.cards):
                            card_x = self.start_x + col * (self.card_width + self.spacing)
                            card_y = self.start_y + row * (self.card_height + self.spacing) - self.scroll_y
                            if pygame.Rect(card_x, card_y, self.card_width, self.card_height).collidepoint(mouse_pos):
                                self.selected_index = index
                                self.detail_view = True

    def ensure_visible(self, index):
        row = index // self.cols
        card_top = row * (self.card_height + self.spacing)
        card_bottom = card_top + self.card_height
        view_height = self.height - self.start_y - 20
        if card_top < self.target_scroll_y:
            self.target_scroll_y = card_top
        elif card_bottom > self.target_scroll_y + view_height:
            self.target_scroll_y = card_bottom - view_height

    def update(self):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 0.2

    def draw(self):
        super().draw()
        
        # Titre Principal
        title_font = pygame.font.SysFont('cinzel, trajan, georgia', 70, bold=True)
        title = title_font.render("COLLECTION", True, colors.SUMI_BLACK)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
        
        count_text = f"{len(self.cards)} Cartes"
        count = self.fonts['small'].render(count_text, True, colors.SUMI_GRAY)
        self.screen.blit(count, count.get_rect(center=(self.width // 2, 100)))

        clip_rect = pygame.Rect(0, self.start_y, self.width, self.height - self.start_y)
        self.screen.set_clip(clip_rect)
        
        if self.cards:
            start_row = int(self.scroll_y // (self.card_height + self.spacing))
            end_row = start_row + int(self.height // (self.card_height + self.spacing)) + 2
            start_idx = start_row * self.cols
            end_idx = min(len(self.cards), end_row * self.cols)
            
            for i in range(start_idx, end_idx):
                self.draw_mini_card(i)
        
        self.screen.set_clip(None)

        if self.detail_view:
            self.draw_detail_view()

    def draw_stat_bubble(self, x, y, value, color, label=""):
        """Dessine une bulle de stat"""
        radius = 16 # Légèrement plus petit
        
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x, y), radius, 1)
        
        val_surf = self.font_card_stat.render(str(value), True, colors.WASHI_COLOR)
        val_rect = val_surf.get_rect(center=(x, y))
        self.screen.blit(val_surf, val_rect)
        
        if label:
            lbl_surf = self.font_card_label.render(label, True, color)
            self.screen.blit(lbl_surf, lbl_surf.get_rect(center=(x, y + radius + 8)))

    def draw_mini_card(self, index):
        card = self.cards[index]
        row = index // self.cols
        col = index % self.cols
        
        x = self.start_x + col * (self.card_width + self.spacing)
        y = self.start_y + row * (self.card_height + self.spacing) - self.scroll_y
        rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        pygame.draw.rect(self.screen, colors.WASHI_COLOR, rect)
        
        is_selected = (index == self.selected_index)
        if is_selected:
            pygame.draw.rect(self.screen, colors.VERMILLION, rect, 3)
            shadow = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
            shadow.fill((255, 255, 255, 20))
            self.screen.blit(shadow, (x, y))
        else:
            pygame.draw.rect(self.screen, colors.SUMI_GRAY, rect, 1)
        
        center_x = x + self.card_width // 2
        
        name = self.font_card_name.render(card.get("nom", "Inconnu"), True, colors.SUMI_BLACK)
        if name.get_width() > self.card_width - 14:
            name = pygame.transform.smoothscale(name, (self.card_width - 14, int(name.get_height() * (self.card_width-14)/name.get_width())))
        self.screen.blit(name, name.get_rect(center=(center_x, y + 25)))
        
        classe = self.font_card_class.render(card.get("classe", ""), True, colors.INDIGO)
        if classe.get_width() > self.card_width - 14:
            classe = pygame.transform.scale(classe, (self.card_width - 14, classe.get_height()))
        self.screen.blit(classe, classe.get_rect(center=(center_x, y + 50)))
        
        img_rect = pygame.Rect(x + 10, y + 65, self.card_width - 20, 120)
        pygame.draw.rect(self.screen, (*colors.INDIGO, 50), img_rect)
        pygame.draw.rect(self.screen, colors.SUMI_GRAY, img_rect, 1)
        
        stats_y = y + 225
        self.draw_stat_bubble(x + 35, stats_y, card.get('puissance', 0), colors.VERMILLION, "ATK")
        self.draw_stat_bubble(x + self.card_width - 35, stats_y, card.get('vitalite', 0), colors.BAMBOO_GREEN, "PV")
        
        rarete = card.get("rarete", 1)
        star_start_x = center_x - (rarete * 12) // 2
        for i in range(rarete):
            pygame.draw.circle(self.screen, colors.GOLD_LEAF, (star_start_x + i * 12 + 6, y + self.card_height - 25), 4)

    def draw_detail_view(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        card = self.cards[self.selected_index]
        w, h = 900, 600
        if w > self.width - 40: w = self.width - 40
        if h > self.height - 40: h = self.height - 40
        x, y = (self.width - w) // 2, (self.height - h) // 2
        
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, colors.WASHI_COLOR, rect)
        pygame.draw.rect(self.screen, colors.GOLD_LEAF, rect, 4)
        
        col_left_x = x + 30
        
        # --- CORRECTION DU CHEVAUCHEMENT ---
        
        # 1. Nom : On utilise la police spécifique DETAIL (60px) au lieu du titre géant
        # Position Y : y + 30
        name = self.font_detail_title.render(card.get("nom", "???"), True, colors.SUMI_BLACK)
        # Scale si trop grand
        if name.get_width() > 400:
             name = pygame.transform.smoothscale(name, (400, int(name.get_height() * 400/name.get_width())))
        self.screen.blit(name, (col_left_x, y + 30))
        
        # 2. Sous-titre : On le descend à y + 100 pour laisser respirer le titre
        subtitle = f"{card.get('classe', 'Inconnu')} - {card.get('edition', 'Base')}"
        sub_surf = self.fonts['subtitle'].render(subtitle, True, colors.INDIGO)
        self.screen.blit(sub_surf, (col_left_x, y + 100))
        
        # 3. Image : On la descend aussi
        img_y = y + 150
        img_h = 250
        pygame.draw.rect(self.screen, (*colors.INDIGO, 30), (col_left_x, img_y, 300, img_h))
        pygame.draw.rect(self.screen, colors.SUMI_BLACK, (col_left_x, img_y, 300, img_h), 2)
        
        # 4. Stats Détail
        stats_y = img_y + img_h + 40
        self.draw_stat_bubble(col_left_x + 60, stats_y, card.get('puissance', 0), colors.VERMILLION, "Attaque")
        self.draw_stat_bubble(col_left_x + 180, stats_y, card.get('vitalite', 0), colors.BAMBOO_GREEN, "Santé")
        
        # --- COLONNE DROITE ---
        col_right_x = x + 360
        text_w = w - 390
        # On aligne le texte avec le haut de l'image
        curr_y = img_y
        
        self.draw_text_wrapped("Description:", self.fonts['subtitle'], colors.SUMI_BLACK, col_right_x, curr_y, text_w)
        curr_y += 40
        curr_y = self.draw_text_wrapped(f"\"{card.get('description', '')}\"", self.fonts['small'], colors.SUMI_GRAY, col_right_x, curr_y, text_w)
        curr_y += 30
        
        comps = card.get('competences', [])
        if comps:
            self.draw_text_wrapped("Compétences:", self.fonts['subtitle'], colors.SUMI_BLACK, col_right_x, curr_y, text_w)
            curr_y += 35
            for comp in comps:
                curr_y = self.draw_text_wrapped(f"• {comp}", self.fonts['small'], colors.INDIGO, col_right_x, curr_y, text_w)
            curr_y += 20
            
        forces = card.get('forces', [])
        if forces:
            txt = "Fort contre: " + ", ".join(forces)
            curr_y = self.draw_text_wrapped(txt, self.fonts['small'], colors.BAMBOO_GREEN, col_right_x, curr_y, text_w)
            
        faiblesses = card.get('faiblesses', [])
        if faiblesses:
            txt = "Faible contre: " + ", ".join(faiblesses)
            curr_y = self.draw_text_wrapped(txt, self.fonts['small'], colors.VERMILLION, col_right_x, curr_y, text_w)

        hint = self.fonts['small'].render("[ECHAP] Retour", True, colors.SUMI_GRAY)
        self.screen.blit(hint, hint.get_rect(bottomright=(x + w - 20, y + h - 20)))

    def draw_text_wrapped(self, text, font, color, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            w, _ = font.size(' '.join(current_line))
            if w > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            surf = font.render(line, True, color)
            self.screen.blit(surf, (x, y + i * line_height))
        return y + len(lines) * line_height