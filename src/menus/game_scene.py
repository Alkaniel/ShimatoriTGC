import pygame
import random # Nécessaire pour le choix de cible de l'IA
import constants.colors as colors
from utils.game_state import GameState
from models.player import Player
from models.card_types import UnitCard

class GameScene(GameState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # On charge les polices une seule fois ici
        try:
            self.font_mini_name = pygame.font.SysFont('cinzel, trajan, georgia', 12, bold=True)
            self.font_mini_stat = pygame.font.SysFont('arial, sans-serif', 16, bold=True)
            self.font_hero_hp = pygame.font.SysFont('arial, sans-serif', 30, bold=True)
            self.font_button = pygame.font.SysFont('cinzel, trajan, georgia', 20, bold=True)
            self.font_game_over = pygame.font.SysFont('cinzel, trajan, georgia', 80, bold=True)
        except:
            self.font_mini_name = pygame.font.Font(None, 14)
            self.font_mini_stat = pygame.font.Font(None, 18)
            self.font_hero_hp = pygame.font.Font(None, 40)
            self.font_button = pygame.font.Font(None, 24)
            self.font_game_over = pygame.font.Font(None, 100)
            
        # Variables d'affichage
        self.hand_y = 0
        self.board_y = 0
        self.opp_hand_y = 0
        self.opp_board_y = 0
        self.card_visual_width = 120
        self.card_visual_height = 160
        self.end_turn_btn = pygame.Rect(0, 0, 140, 50)
        
        # --- LANCEMENT DE LA PARTIE ---
        self.reset_game()
        
        # Premier calcul de taille
        self.on_resize(self.width, self.height)

    def reset_game(self):
        """Réinitialise totalement la partie"""
        all_cards = self.game.card_manager.get_all_cards()
        
        self.player = Player("Joueur", all_cards, is_ai=False)
        self.opponent = Player("Adversaire", all_cards, is_ai=True)
        
        self.player.draw_card(3)
        self.opponent.draw_card(3)
        
        self.player.max_mana = 1
        self.player.mana = 1
        self.is_player_turn = True
        
        self.game_over = False
        self.winner_message = ""
        self.win_color = colors.SUMI_BLACK
        
        self.player_face_rect = None
        self.opponent_face_rect = None
        
        self.dragging_card = None
        self.dragging_index = -1
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.attacking_unit = None
        print("Nouvelle partie démarrée !")

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.opp_hand_y = -50
        self.opp_board_y = int(height * 0.25)
        self.board_y = int(height * 0.55)
        self.hand_y = int(height * 0.82)
        self.end_turn_btn.x = width - 160
        self.end_turn_btn.y = height // 2 - 25

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            # GESTION FIN DE PARTIE : Clic pour reset et revenir au menu
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.reset_game() # <--- ON RESET ICI
                    self.game.change_state("menu")
                continue

            # --- JEU NORMAL ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.reset_game() # On reset aussi si on quitte en cours
                    self.game.change_state("menu")
                if event.key == pygame.K_SPACE:
                    self.next_turn()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.end_turn_btn.collidepoint(mouse_pos) and self.is_player_turn:
                        self.next_turn()
                        return

                    if self.is_player_turn:
                        # Drag Main
                        for i in range(len(self.player.hand) - 1, -1, -1):
                            card = self.player.hand[i]
                            if card.rect and card.rect.collidepoint(mouse_pos):
                                self.dragging_card = card
                                self.dragging_index = i
                                self.drag_offset_x = mouse_pos[0] - card.rect.x
                                self.drag_offset_y = mouse_pos[1] - card.rect.y
                                return 

                        # Attaque Plateau
                        for unit in self.player.board:
                            if unit.rect and unit.rect.collidepoint(mouse_pos):
                                if unit.can_attack:
                                    self.attacking_unit = unit
                                return

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.dragging_card:
                        if mouse_pos[1] < self.hand_y - 50:
                            self.player.play_unit(self.dragging_index)
                        self.dragging_card = None
                        self.dragging_index = -1
                    
                    elif self.attacking_unit:
                        self.handle_attack_release(mouse_pos)
                        self.attacking_unit = None

    def handle_attack_release(self, mouse_pos):
        target_found = False
        for enemy in self.opponent.board:
            if enemy.rect and enemy.rect.collidepoint(mouse_pos):
                self.resolve_combat(self.attacking_unit, enemy)
                target_found = True
                break
        
        if not target_found and self.opponent_face_rect and self.opponent_face_rect.collidepoint(mouse_pos):
            self.resolve_combat(self.attacking_unit, self.opponent)
            target_found = True

    def resolve_combat(self, attacker, target):
        if isinstance(target, UnitCard):
            d_target = attacker.current_attack
            d_attacker = target.current_attack
            target.take_damage(d_target)
            attacker.take_damage(d_attacker)
            
        elif isinstance(target, Player):
            target.health -= attacker.current_attack
            print(f"{target.name} prend {attacker.current_attack} dégâts (PV: {target.health})")
            
        attacker.can_attack = False
        
        self.clean_dead_units(self.player)
        self.clean_dead_units(self.opponent)
        
        if self.opponent.health <= 0:
            self.trigger_game_over(victory=True)
        elif self.player.health <= 0:
            self.trigger_game_over(victory=False)

    def trigger_game_over(self, victory):
        self.game_over = True
        if victory:
            self.winner_message = "VICTOIRE !"
            self.win_color = colors.BAMBOO_GREEN
        else:
            self.winner_message = "DÉFAITE..."
            self.win_color = colors.VERMILLION

    def clean_dead_units(self, player):
        alive = []
        for unit in player.board:
            if not unit.is_dead:
                alive.append(unit)
            else:
                player.graveyard.append(unit)
        player.board = alive

    def next_turn(self):
        if self.is_player_turn and not self.game_over:
            self.is_player_turn = False
            self.opponent.start_turn()
            
            # --- IA : Jouer des cartes ---
            for i in range(len(self.opponent.hand) - 1, -1, -1):
                self.opponent.play_unit(i)
            
            # --- IA : Attaquer INTELLIGEMMENT ---
            for unit in self.opponent.board:
                if unit.can_attack and not self.game_over:
                    # LOGIQUE IA :
                    # 1. Si le joueur a des unités, on en attaque une au hasard (Contrôle de plateau)
                    if len(self.player.board) > 0:
                        target = random.choice(self.player.board)
                        print(f"IA attaque l'unité {target.name}")
                        self.resolve_combat(unit, target)
                    # 2. Sinon, on attaque le joueur (Face)
                    else:
                        print("IA attaque le Joueur")
                        self.resolve_combat(unit, self.player)
            
            if not self.game_over:
                self.is_player_turn = True
                self.player.start_turn()

    def update(self):
        pass

    def draw(self):
        self.screen.fill(colors.WASHI_COLOR)
        self.draw_tatami_pattern()
        pygame.draw.line(self.screen, colors.SUMI_GRAY, (0, self.height//2), (self.width, self.height//2), 2)
        
        # Jeu Normal
        self.draw_hand(self.opponent, self.opp_hand_y, hidden=True)
        self.draw_board(self.opponent, self.opp_board_y)
        self.draw_hero_stats(self.opponent, 60, 60, is_opponent=True)
        
        self.draw_board(self.player, self.board_y)
        self.draw_hand(self.player, self.hand_y, hidden=False, skip_index=self.dragging_index)
        self.draw_hero_stats(self.player, 60, self.height - 100, is_opponent=False)
        self.draw_mana_bar(self.player, self.width - 260, self.height - 60)
        self.draw_end_turn_button()

        if self.dragging_card:
            mx, my = pygame.mouse.get_pos()
            self.draw_card_front(self.dragging_card, mx - self.drag_offset_x, my - self.drag_offset_y)
        
        if self.attacking_unit:
            self.draw_attack_arrow()
            
        if self.game_over:
            self.draw_game_over_screen()

    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.font_game_over.render(self.winner_message, True, self.win_color)
        rect = text.get_rect(center=(self.width//2, self.height//2 - 50))
        
        shadow = self.font_game_over.render(self.winner_message, True, (0,0,0))
        self.screen.blit(shadow, (rect.x + 4, rect.y + 4))
        self.screen.blit(text, rect)
        
        sub = self.fonts['subtitle'].render("Cliquez pour retourner au menu", True, colors.WASHI_COLOR)
        self.screen.blit(sub, sub.get_rect(center=(self.width//2, self.height//2 + 50)))

    def draw_attack_arrow(self):
        if not self.attacking_unit or not self.attacking_unit.rect: return
        start = self.attacking_unit.rect.center
        end = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, colors.VERMILLION, start, end, 5)
        pygame.draw.circle(self.screen, colors.VERMILLION, end, 10)

    def draw_end_turn_button(self):
        if self.is_player_turn:
            bg_color = colors.VERMILLION
            text_color = colors.WASHI_COLOR
            text = "Fin de Tour"
        else:
            bg_color = colors.SUMI_GRAY
            text_color = (200, 200, 200)
            text = "Tour Adverse"
            
        r = self.end_turn_btn
        pygame.draw.rect(self.screen, (50, 50, 50, 100), (r.x+4, r.y+4, r.w, r.h))
        pygame.draw.rect(self.screen, bg_color, r)
        pygame.draw.rect(self.screen, colors.SUMI_BLACK, r, 2)
        
        t = self.font_button.render(text, True, text_color)
        self.screen.blit(t, t.get_rect(center=r.center))

    def draw_tatami_pattern(self):
        color = (230, 225, 210)
        line_spacing = 100
        for x in range(0, self.width, line_spacing):
            pygame.draw.line(self.screen, color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, line_spacing):
            pygame.draw.line(self.screen, color, (0, y), (self.width, y), 1)

    def draw_stat_bubble(self, x, y, value, color):
        radius = 16
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x, y), radius, 2)
        val_surf = self.font_mini_stat.render(str(value), True, colors.WASHI_COLOR)
        val_rect = val_surf.get_rect(center=(x, y)) 
        val_rect.y += 1 
        self.screen.blit(val_surf, val_rect)

    def draw_card_front(self, card, x, y, can_attack=False):
        rect = pygame.Rect(x, y, self.card_visual_width, self.card_visual_height)
        card.rect = rect
        
        if can_attack:
             glow_rect = rect.inflate(8, 8)
             pygame.draw.rect(self.screen, colors.BAMBOO_GREEN, glow_rect, 3, border_radius=4)
        
        pygame.draw.rect(self.screen, colors.WASHI_COLOR, rect)
        pygame.draw.rect(self.screen, colors.INDIGO, rect, 2)
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, colors.GOLD_LEAF, inner_rect, 1)

        mana_radius = 12
        mana_x, mana_y = x + 18, y + 20
        pygame.draw.circle(self.screen, colors.INDIGO, (mana_x, mana_y), mana_radius)
        pygame.draw.circle(self.screen, colors.GOLD_LEAF, (mana_x, mana_y), mana_radius, 1)
        mana = self.font_mini_stat.render(str(card.mana_cost), True, colors.WASHI_COLOR)
        self.screen.blit(mana, mana.get_rect(center=(mana_x, mana_y + 1)))

        text_start = x + 35
        text_w = (x + self.card_visual_width - 5) - text_start
        name = self.font_mini_name.render(card.name, True, colors.SUMI_BLACK)
        if name.get_width() > text_w:
            name = pygame.transform.smoothscale(name, (int(text_w), int(name.get_height() * text_w/name.get_width())))
        self.screen.blit(name, name.get_rect(center=(text_start + text_w//2, mana_y)))

        img_rect = pygame.Rect(x+10, y+40, self.card_visual_width-20, 80)
        pygame.draw.rect(self.screen, (*colors.INDIGO, 50), img_rect)
        pygame.draw.rect(self.screen, colors.SUMI_GRAY, img_rect, 1)

        if isinstance(card, UnitCard):
            stat_y = y + self.card_visual_height - 20
            self.draw_stat_bubble(x + 20, stat_y, card.current_attack, colors.VERMILLION)
            self.draw_stat_bubble(x + self.card_visual_width - 20, stat_y, card.current_health, colors.BAMBOO_GREEN)

    def draw_hand(self, player, y_pos, hidden=False, skip_index=-1):
        num_cards = len(player.hand)
        if num_cards == 0: return
        spacing = 10
        total_width = num_cards * (self.card_visual_width + spacing)
        start_x = (self.width - total_width) // 2
        for i, card in enumerate(player.hand):
            if i == skip_index: continue
            x = start_x + i * (self.card_visual_width + spacing)
            rect = pygame.Rect(x, y_pos, self.card_visual_width, self.card_visual_height)
            card.rect = rect 
            if hidden:
                pygame.draw.rect(self.screen, colors.INDIGO, rect)
                pygame.draw.rect(self.screen, colors.GOLD_LEAF, rect, 2)
                pygame.draw.circle(self.screen, colors.GOLD_LEAF, rect.center, 20, 1)
                pygame.draw.circle(self.screen, colors.INDIGO, rect.center, 15)
            else:
                self.draw_card_front(card, x, y_pos)

    def draw_board(self, player, y_pos):
        num_units = len(player.board)
        if num_units == 0: return
        spacing = 10
        total_width = num_units * (self.card_visual_width + spacing)
        start_x = (self.width - total_width) // 2
        for i, unit in enumerate(player.board):
            x = start_x + i * (self.card_visual_width + spacing)
            can_act = unit.can_attack and self.is_player_turn and player == self.player and not self.game_over
            self.draw_card_front(unit, x, y_pos, can_attack=can_act)

    def draw_hero_stats(self, player, x, y, is_opponent=False):
        radius = 35
        color = colors.VERMILLION if not player.is_ai else colors.INDIGO
        rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        if is_opponent: self.opponent_face_rect = rect
        else: self.player_face_rect = rect
        
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x, y), radius, 3)
        
        hp_surf = self.font_hero_hp.render(str(player.health), True, colors.WASHI_COLOR)
        if player.health > 99: hp_surf = pygame.transform.scale(hp_surf, (40, 30))
        self.screen.blit(hp_surf, hp_surf.get_rect(center=(x, y)))
        
        name_surf = self.fonts['subtitle'].render(player.name, True, colors.SUMI_BLACK)
        self.screen.blit(name_surf, (x + radius + 15, y - 15))

    def draw_mana_bar(self, player, x, y):
        crystal_size = 18
        spacing = 5
        txt = f"Mana: {player.mana}/{player.max_mana}"
        surf = self.fonts['small'].render(txt, True, colors.INDIGO)
        self.screen.blit(surf, (x, y - 40))
        for i in range(10): 
            cx = x + i * (crystal_size + spacing)
            pygame.draw.circle(self.screen, colors.SUMI_GRAY, (cx, y), crystal_size//2, 1)
            if i < player.mana:
                pygame.draw.circle(self.screen, colors.INDIGO, (cx, y), crystal_size//2 - 2)
            elif i < player.max_mana:
                pygame.draw.circle(self.screen, (150, 150, 200), (cx, y), crystal_size//2 - 4)