import pygame
import random
import constants.colors as colors
from utils.game_state import GameState
from models.player import Player
from models.card_types import UnitCard, SpellCard
from constants.enums import Keyword

# --- CLASSE POUR LES EFFETS FLOTTANTS ---
class FloatingText:
    def __init__(self, x, y, text, color, size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 60 # Durée de vie (1 seconde à 60 FPS)
        self.opacity = 255
        
        try:
            self.font = pygame.font.SysFont('arial, sans-serif', size, bold=True)
        except:
            self.font = pygame.font.Font(None, size)

    def update(self):
        self.y -= 1.5 # Monte doucement
        self.timer -= 1
        if self.timer < 20: # Fade out sur la fin
            self.opacity -= 12
            if self.opacity < 0: self.opacity = 0

    def draw(self, screen):
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(self.opacity)
        # Contour noir pour lisibilité
        outline = self.font.render(self.text, True, colors.SUMI_BLACK)
        outline.set_alpha(self.opacity)
        
        rect = surf.get_rect(center=(self.x, self.y))
        screen.blit(outline, (rect.x+2, rect.y+2))
        screen.blit(surf, rect)


class GameScene(GameState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        try:
            self.font_mini_name = pygame.font.SysFont('cinzel, trajan, georgia', 12, bold=True)
            self.font_mini_stat = pygame.font.SysFont('arial, sans-serif', 16, bold=True)
            self.font_hero_hp = pygame.font.SysFont('arial, sans-serif', 30, bold=True)
            self.font_button = pygame.font.SysFont('cinzel, trajan, georgia', 20, bold=True)
            self.font_game_over = pygame.font.SysFont('cinzel, trajan, georgia', 80, bold=True)
            self.font_zoom_name = pygame.font.SysFont('cinzel, trajan, georgia', 20, bold=True)
            self.font_zoom_desc = pygame.font.SysFont('arial, sans-serif', 15, bold=False)
            self.font_zoom_stat = pygame.font.SysFont('arial, sans-serif', 22, bold=True)
            self.font_zoom_kw = pygame.font.SysFont('arial, sans-serif', 15, bold=True)
            self.font_deck = pygame.font.SysFont('arial, sans-serif', 24, bold=True)
        except:
            self.font_mini_name = pygame.font.Font(None, 14)
            self.font_mini_stat = pygame.font.Font(None, 18)
            self.font_hero_hp = pygame.font.Font(None, 40)
            self.font_button = pygame.font.Font(None, 24)
            self.font_game_over = pygame.font.Font(None, 100)
            self.font_zoom_name = pygame.font.Font(None, 24)
            self.font_zoom_desc = pygame.font.Font(None, 18)
            self.font_zoom_stat = pygame.font.Font(None, 26)
            self.font_zoom_kw = pygame.font.Font(None, 18)
            self.font_deck = pygame.font.Font(None, 30)
            
        self.hand_y = 0
        self.board_y = 0
        self.opp_hand_y = 0
        self.opp_board_y = 0
        self.card_visual_width = 120
        self.card_visual_height = 160
        self.end_turn_btn = pygame.Rect(0, 0, 140, 50)
        
        # LISTE DES EFFETS VISUELS
        self.visual_effects = []
        
        self.reset_game()
        self.on_resize(self.width, self.height)

    def reset_game(self):
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
        self.visual_effects = []

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
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.reset_game()
                    self.game.change_state("menu")
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.reset_game()
                    self.game.change_state("menu")
                if event.key == pygame.K_SPACE:
                    self.next_turn()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.end_turn_btn.collidepoint(mouse_pos) and self.is_player_turn:
                        self.next_turn()
                        return

                    if self.is_player_turn:
                        for i in range(len(self.player.hand) - 1, -1, -1):
                            card = self.player.hand[i]
                            if card.rect and card.rect.collidepoint(mouse_pos):
                                self.dragging_card = card
                                self.dragging_index = i
                                self.drag_offset_x = mouse_pos[0] - card.rect.x
                                self.drag_offset_y = mouse_pos[1] - card.rect.y
                                return 

                        for unit in self.player.board:
                            if unit.rect and unit.rect.collidepoint(mouse_pos):
                                if unit.can_attack:
                                    self.attacking_unit = unit
                                return

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.dragging_card:
                        self.handle_card_drop(mouse_pos)
                        self.dragging_card = None
                        self.dragging_index = -1
                    elif self.attacking_unit:
                        self.handle_attack_release(mouse_pos)
                        self.attacking_unit = None

    def handle_card_drop(self, mouse_pos):
        card = self.dragging_card
        
        if isinstance(card, UnitCard):
            if mouse_pos[1] < self.hand_y - 50:
                self.player.play_unit(self.dragging_index)
                
        elif isinstance(card, SpellCard):
            target = None
            for enemy in self.opponent.board:
                if enemy.rect and enemy.rect.collidepoint(mouse_pos): target = enemy; break
            
            if not target:
                for ally in self.player.board:
                    if ally.rect and ally.rect.collidepoint(mouse_pos): target = ally; break
            
            if not target and self.opponent_face_rect and self.opponent_face_rect.collidepoint(mouse_pos):
                target = self.opponent
            
            if not target and self.player_face_rect and self.player_face_rect.collidepoint(mouse_pos):
                target = self.player

            if target:
                if self.player.play_ritual(self.dragging_index, target):
                    # Effet visuel si c'est un buff sur soi-même ou ses unités
                    if card.effect_type == "buff_target" or target == self.player:
                         self.spawn_floating_text(target.rect.centerx if hasattr(target, 'rect') else self.player_face_rect.centerx, 
                                                  target.rect.centery if hasattr(target, 'rect') else self.player_face_rect.centery, 
                                                  "Buff!", colors.BAMBOO_GREEN)
                    # Effet visuel si c'est des dégâts
                    elif card.effect_type == "damage_target":
                         self.spawn_floating_text(target.rect.centerx if hasattr(target, 'rect') else self.opponent_face_rect.centerx, 
                                                  target.rect.centery if hasattr(target, 'rect') else self.opponent_face_rect.centery, 
                                                  f"-{card.effect_value}", colors.VERMILLION)

                self.clean_dead_units(self.player)
                self.clean_dead_units(self.opponent)
                self.check_game_over()

    def handle_attack_release(self, mouse_pos):
        target = None
        for enemy in self.opponent.board:
            if enemy.rect and enemy.rect.collidepoint(mouse_pos): target = enemy; break
        
        if not target and self.opponent_face_rect and self.opponent_face_rect.collidepoint(mouse_pos):
            target = self.opponent

        if not target: return

        if isinstance(target, UnitCard) and Keyword.STEALTH in target.keywords:
            self.spawn_floating_text(target.rect.centerx, target.rect.centery, "Furtif!", colors.SUMI_GRAY)
            return

        taunt_units = [u for u in self.opponent.board if Keyword.TAUNT in u.keywords and not u.is_dead and Keyword.STEALTH not in u.keywords]
        
        if taunt_units:
            if target in taunt_units:
                self.resolve_combat(self.attacking_unit, target)
            else:
                self.spawn_floating_text(mouse_pos[0], mouse_pos[1], "Provocation!", colors.VERMILLION)
        else:
            self.resolve_combat(self.attacking_unit, target)

    def resolve_combat(self, attacker, target):
        damage_to_target = attacker.current_attack
        damage_to_attacker = 0
        
        if isinstance(target, UnitCard):
            damage_to_attacker = target.current_attack
            
            if Keyword.POISONOUS in attacker.keywords: damage_to_target = 999 
            if Keyword.POISONOUS in target.keywords: damage_to_attacker = 999

            if Keyword.DIVINE_SHIELD in target.keywords:
                damage_to_target = 0
                target.keywords.remove(Keyword.DIVINE_SHIELD)
                self.spawn_floating_text(target.rect.centerx, target.rect.centery, "Bloqué!", (255, 215, 0))
            
            target.take_damage(damage_to_target)
            if damage_to_target > 0:
                self.spawn_floating_text(target.rect.centerx, target.rect.centery, f"-{damage_to_target}", colors.VERMILLION)
            
            if Keyword.DIVINE_SHIELD in attacker.keywords:
                damage_to_attacker = 0
                attacker.keywords.remove(Keyword.DIVINE_SHIELD)
                self.spawn_floating_text(attacker.rect.centerx, attacker.rect.centery, "Bloqué!", (255, 215, 0))
                
            attacker.take_damage(damage_to_attacker)
            if damage_to_attacker > 0:
                self.spawn_floating_text(attacker.rect.centerx, attacker.rect.centery, f"-{damage_to_attacker}", colors.VERMILLION)
            
            if Keyword.STEALTH in attacker.keywords: attacker.keywords.remove(Keyword.STEALTH)

        elif isinstance(target, Player):
            target.health -= damage_to_target
            # Position du texte pour le héros
            tx = self.opponent_face_rect.centerx if target == self.opponent else self.player_face_rect.centerx
            ty = self.opponent_face_rect.centery if target == self.opponent else self.player_face_rect.centery
            self.spawn_floating_text(tx, ty, f"-{damage_to_target}", colors.VERMILLION)
            
            if Keyword.STEALTH in attacker.keywords: attacker.keywords.remove(Keyword.STEALTH)
            
        attacker.can_attack = False
        self.clean_dead_units(self.player)
        self.clean_dead_units(self.opponent)
        self.check_game_over()

    def spawn_floating_text(self, x, y, text, color):
        self.visual_effects.append(FloatingText(x, y, text, color))

    def check_game_over(self):
        if self.opponent.health <= 0: self.trigger_game_over(True)
        elif self.player.health <= 0: self.trigger_game_over(False)

    def trigger_game_over(self, victory):
        self.game_over = True
        self.winner_message = "VICTOIRE !" if victory else "DÉFAITE..."
        self.win_color = colors.BAMBOO_GREEN if victory else colors.VERMILLION

    def clean_dead_units(self, player):
        alive = []
        for unit in player.board:
            if not unit.is_dead: alive.append(unit)
            else: player.graveyard.append(unit)
        player.board = alive

    def next_turn(self):
        if self.is_player_turn and not self.game_over:
            self.is_player_turn = False
            self.opponent.start_turn()
            
            for i in range(len(self.opponent.hand) - 1, -1, -1):
                card = self.opponent.hand[i]
                if isinstance(card, UnitCard):
                    self.opponent.play_unit(i)
                elif isinstance(card, SpellCard) and card.effect_type == "damage_target":
                    self.opponent.play_ritual(i, self.player)
                    cx, cy = self.player_face_rect.centerx, self.player_face_rect.centery
                    self.spawn_floating_text(cx, cy, f"-{card.effect_value}", colors.VERMILLION)
                
            taunt_targets = [u for u in self.player.board if Keyword.TAUNT in u.keywords]
            other_targets = [u for u in self.player.board if Keyword.TAUNT not in u.keywords and Keyword.STEALTH not in u.keywords]
            
            for unit in self.opponent.board:
                if unit.can_attack and not self.game_over:
                    target = None
                    if taunt_targets: target = random.choice(taunt_targets)
                    elif other_targets:
                        target = self.player if random.random() < 0.5 else random.choice(other_targets)
                    else: target = self.player 
                    if target:
                        self.resolve_combat(unit, target)
                        taunt_targets = [u for u in self.player.board if Keyword.TAUNT in u.keywords]
                        other_targets = [u for u in self.player.board if Keyword.TAUNT not in u.keywords and Keyword.STEALTH not in u.keywords]

            if not self.game_over:
                self.is_player_turn = True
                self.player.start_turn()

    def update(self):
        for effect in self.visual_effects[:]:
            effect.update()
            if effect.timer <= 0:
                self.visual_effects.remove(effect)

    def draw(self):
        self.screen.fill(colors.WASHI_COLOR)
        self.draw_tatami_pattern()
        pygame.draw.line(self.screen, colors.SUMI_GRAY, (0, self.height//2), (self.width, self.height//2), 2)
        
        self.draw_deck_pile(self.opponent, 50, self.height//2 - 140)
        self.draw_deck_pile(self.player, self.width - 110, self.height//2 + 50)
        
        self.draw_hand(self.opponent, self.opp_hand_y, hidden=True)
        self.draw_board(self.opponent, self.opp_board_y)
        self.draw_hero_stats(self.opponent, 60, 60, is_opponent=True)
        
        self.draw_board(self.player, self.board_y)
        self.draw_hand(self.player, self.hand_y, hidden=False, skip_index=self.dragging_index)
        self.draw_hero_stats(self.player, 60, self.height - 100, is_opponent=False)
        self.draw_mana_bar(self.player, self.width - 260, self.height - 60)
        self.draw_end_turn_button()

        if self.dragging_card:
            if isinstance(self.dragging_card, UnitCard):
                mx, my = pygame.mouse.get_pos()
                self.draw_card_front(self.dragging_card, mx - self.drag_offset_x, my - self.drag_offset_y)
            elif isinstance(self.dragging_card, SpellCard):
                card_origin_x = self.dragging_card.rect.x
                card_origin_y = self.dragging_card.rect.y
                self.draw_card_front(self.dragging_card, card_origin_x, card_origin_y)
                start_pos = self.dragging_card.rect.center
                end_pos = pygame.mouse.get_pos()
                pygame.draw.line(self.screen, colors.INDIGO, start_pos, end_pos, 4)
                pygame.draw.circle(self.screen, colors.INDIGO, end_pos, 8)

        if self.attacking_unit:
            self.draw_attack_arrow()
        
        for effect in self.visual_effects:
            effect.draw(self.screen)

        if self.game_over:
            self.draw_game_over_screen()
        
        if not self.dragging_card and not self.game_over:
            self.check_hover_and_draw_zoom()

    def draw_tatami_pattern(self):
        color = (230, 225, 210)
        for x in range(0, self.width, 100): pygame.draw.line(self.screen, color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 100): pygame.draw.line(self.screen, color, (0, y), (self.width, y), 1)

    def draw_stat_bubble(self, x, y, value, color):
        pygame.draw.circle(self.screen, color, (x, y), 16)
        pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x, y), 16, 2)
        val_surf = self.font_mini_stat.render(str(value), True, colors.WASHI_COLOR)
        val_rect = val_surf.get_rect(center=(x, y)); val_rect.y+=1
        self.screen.blit(val_surf, val_rect)

    def draw_deck_pile(self, player, x, y):
        deck_count = len(player.deck)
        if deck_count == 0:
            rect = pygame.Rect(x, y, 60, 80); pygame.draw.rect(self.screen, (0,0,0,50), rect, 1)
            return
        offset = min(deck_count, 3) * 2
        for i in range(min(deck_count, 3)):
            r = pygame.Rect(x - i*2, y - i*2, 60, 80)
            pygame.draw.rect(self.screen, colors.INDIGO, r)
            pygame.draw.rect(self.screen, colors.WASHI_COLOR, r, 1)
        top_rect = pygame.Rect(x - offset, y - offset, 60, 80)
        pygame.draw.rect(self.screen, colors.INDIGO, top_rect)
        pygame.draw.rect(self.screen, colors.GOLD_LEAF, top_rect, 2)
        pygame.draw.circle(self.screen, colors.GOLD_LEAF, top_rect.center, 15, 1)
        txt_surf = self.font_deck.render(str(deck_count), True, colors.WASHI_COLOR)
        txt_bg = txt_surf.get_rect(center=top_rect.center)
        pygame.draw.rect(self.screen, colors.INDIGO, txt_bg.inflate(10, 5))
        self.screen.blit(txt_surf, txt_bg)

    def draw_keyword_icons(self, card, x, y):
        if not isinstance(card, UnitCard): return
        icon_y = y + 85; start_x = x + 10; spacing = 20
        if Keyword.CHARGE in card.keywords:
            cx, cy = start_x, icon_y
            pygame.draw.circle(self.screen, colors.GOLD_LEAF, (cx, cy), 8)
            pygame.draw.circle(self.screen, colors.SUMI_BLACK, (cx, cy), 8, 1)
            pygame.draw.line(self.screen, colors.SUMI_BLACK, (cx-3, cy-3), (cx+3, cy-3), 2)
            pygame.draw.line(self.screen, colors.SUMI_BLACK, (cx+3, cy-3), (cx-3, cy+3), 2)
            pygame.draw.line(self.screen, colors.SUMI_BLACK, (cx-3, cy+3), (cx+3, cy+3), 2)
            start_x += spacing
        if Keyword.STEALTH in card.keywords:
            cx, cy = start_x, icon_y
            pygame.draw.circle(self.screen, colors.SUMI_GRAY, (cx, cy), 8)
            pygame.draw.circle(self.screen, colors.SUMI_BLACK, (cx, cy), 8, 1)
            pygame.draw.line(self.screen, colors.WASHI_COLOR, (cx-4, cy), (cx+4, cy), 2)
            start_x += spacing
        if Keyword.POISONOUS in card.keywords:
            cx, cy = start_x, icon_y
            pygame.draw.circle(self.screen, (50, 200, 50), (cx, cy), 8)
            pygame.draw.circle(self.screen, colors.SUMI_BLACK, (cx, cy), 8, 1)
            pygame.draw.line(self.screen, colors.SUMI_BLACK, (cx-3, cy-3), (cx+3, cy-3), 2)
            pygame.draw.line(self.screen, colors.SUMI_BLACK, (cx+3, cy-3), (cx-3, cy+3), 2)
            start_x += spacing

    def check_hover_and_draw_zoom(self, *args):
        mouse_pos = pygame.mouse.get_pos()
        hovered_card = None
        all_zones = self.player.hand + self.player.board + self.opponent.board
        for card in all_zones:
            if card.rect and card.rect.collidepoint(mouse_pos):
                hovered_card = card; break
        if hovered_card: self.draw_zoomed_card(hovered_card, mouse_pos)

    def draw_zoomed_card(self, card, mouse_pos):
        zoom_w, zoom_h = 240, 340
        x, y = mouse_pos[0] + 20, mouse_pos[1] - 50
        if x + zoom_w > self.width: x = mouse_pos[0] - zoom_w - 20
        if y + zoom_h > self.height: y = self.height - zoom_h - 10
        if y < 10: y = 10
        rect = pygame.Rect(x, y, zoom_w, zoom_h)
        shadow_rect = rect.copy(); shadow_rect.x += 8; shadow_rect.y += 8
        pygame.draw.rect(self.screen, (0,0,0,90), shadow_rect, border_radius=12)
        pygame.draw.rect(self.screen, colors.WASHI_COLOR, rect, border_radius=12)
        pygame.draw.rect(self.screen, colors.INDIGO, rect, 3, border_radius=12)
        pygame.draw.rect(self.screen, colors.GOLD_LEAF, rect.inflate(-8, -8), 1, border_radius=12)
        mana_radius = 22; mana_cx, mana_cy = x + 30, y + 30
        pygame.draw.circle(self.screen, colors.INDIGO, (mana_cx, mana_cy), mana_radius)
        pygame.draw.circle(self.screen, colors.GOLD_LEAF, (mana_cx, mana_cy), mana_radius, 2)
        cost_surf = self.font_zoom_stat.render(str(card.mana_cost), True, colors.WASHI_COLOR)
        self.screen.blit(cost_surf, cost_surf.get_rect(center=(mana_cx, mana_cy)))
        text_start_x = x + 60; available_text_width = (x + zoom_w - 15) - text_start_x
        name_surf = self.font_zoom_name.render(card.name, True, colors.SUMI_BLACK)
        if name_surf.get_width() > available_text_width:
             ratio = available_text_width / name_surf.get_width()
             new_h = int(name_surf.get_height() * ratio)
             name_surf = pygame.transform.smoothscale(name_surf, (int(available_text_width), new_h))
        name_rect = name_surf.get_rect(midleft=(text_start_x, mana_cy))
        self.screen.blit(name_surf, name_rect)
        img_h = 140; img_rect = pygame.Rect(x + 15, y + 65, zoom_w - 30, img_h)
        bg_col = (*colors.INDIGO, 60)
        pygame.draw.rect(self.screen, bg_col, img_rect)
        pygame.draw.rect(self.screen, colors.SUMI_GRAY, img_rect, 1)
        desc_y = y + 65 + img_h + 15
        current_y = desc_y
        if isinstance(card, UnitCard) and card.keywords:
            kw_txt = ", ".join([k.value for k in card.keywords])
            kw_surf = self.font_zoom_kw.render(kw_txt, True, colors.VERMILLION)
            self.screen.blit(kw_surf, (x + 20, current_y)); current_y += 25
        words = card.description.split(' '); lines = []; curr_line = []
        for word in words:
            curr_line.append(word)
            if self.font_zoom_desc.size(' '.join(curr_line))[0] > zoom_w - 40:
                curr_line.pop(); lines.append(' '.join(curr_line)); curr_line = [word]
        lines.append(' '.join(curr_line))
        for line in lines:
            line_surf = self.font_zoom_desc.render(line, True, colors.SUMI_GRAY)
            self.screen.blit(line_surf, (x + 20, current_y)); current_y += 18
        if isinstance(card, UnitCard):
            stat_y = y + zoom_h - 35
            pygame.draw.circle(self.screen, colors.VERMILLION, (x + 35, stat_y), 20)
            pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x + 35, stat_y), 20, 2)
            atk_s = self.font_zoom_stat.render(str(card.current_attack), True, colors.WASHI_COLOR)
            self.screen.blit(atk_s, atk_s.get_rect(center=(x + 35, stat_y)))
            pygame.draw.circle(self.screen, colors.BAMBOO_GREEN, (x + zoom_w - 35, stat_y), 20)
            pygame.draw.circle(self.screen, colors.SUMI_BLACK, (x + zoom_w - 35, stat_y), 20, 2)
            hp_s = self.font_zoom_stat.render(str(card.current_health), True, colors.WASHI_COLOR)
            self.screen.blit(hp_s, hp_s.get_rect(center=(x + zoom_w - 35, stat_y)))

    def draw_card_front(self, card, x, y, can_attack=False):
        rect = pygame.Rect(x, y, self.card_visual_width, self.card_visual_height)
        card.rect = rect
        
        has_taunt = False; is_stealth = False
        if isinstance(card, UnitCard):
            if Keyword.TAUNT in card.keywords: has_taunt = True
            if Keyword.STEALTH in card.keywords: is_stealth = True

        if has_taunt:
            shield_rect = rect.inflate(6, 6)
            pygame.draw.rect(self.screen, (100, 100, 100), shield_rect, border_radius=5)
            pygame.draw.rect(self.screen, colors.SUMI_BLACK, shield_rect, 2, border_radius=5)
        
        if isinstance(card, UnitCard) and Keyword.DIVINE_SHIELD in card.keywords:
            ds_rect = rect.inflate(10, 10)
            pygame.draw.rect(self.screen, (255, 215, 0), ds_rect, 3, border_radius=6)

        if can_attack:
             glow_rect = rect.inflate(8, 8)
             pygame.draw.rect(self.screen, colors.BAMBOO_GREEN, glow_rect, 3, border_radius=4)
        
        bg_color = (200, 200, 200) if is_stealth else colors.WASHI_COLOR
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, colors.INDIGO, rect, 2)
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, colors.GOLD_LEAF, inner_rect, 1)

        mana_x, mana_y = x + 18, y + 20
        pygame.draw.circle(self.screen, colors.INDIGO, (mana_x, mana_y), 12)
        pygame.draw.circle(self.screen, colors.GOLD_LEAF, (mana_x, mana_y), 12, 1)
        mana = self.font_mini_stat.render(str(card.mana_cost), True, colors.WASHI_COLOR)
        self.screen.blit(mana, mana.get_rect(center=(mana_x, mana_y + 1)))

        text_start = x + 35; text_w = (x + self.card_visual_width - 5) - text_start
        name = self.font_mini_name.render(card.name, True, colors.SUMI_BLACK)
        if name.get_width() > text_w:
            name = pygame.transform.smoothscale(name, (int(text_w), int(name.get_height() * text_w/name.get_width())))
        self.screen.blit(name, name.get_rect(center=(text_start + text_w//2, mana_y)))

        img_rect = pygame.Rect(x+10, y+40, self.card_visual_width-20, 80)
        bg_col = (*colors.INDIGO, 80) if has_taunt else (*colors.INDIGO, 50)
        if is_stealth: bg_col = (50, 50, 50, 100)
        pygame.draw.rect(self.screen, bg_col, img_rect)
        pygame.draw.rect(self.screen, colors.SUMI_GRAY, img_rect, 1)
        
        self.draw_keyword_icons(card, x, y)

        if isinstance(card, UnitCard):
            stat_y = y + self.card_visual_height - 20
            self.draw_stat_bubble(x + 20, stat_y, card.current_attack, colors.VERMILLION)
            self.draw_stat_bubble(x + self.card_visual_width - 20, stat_y, card.current_health, colors.BAMBOO_GREEN)

    def draw_hand(self, player, y_pos, hidden=False, skip_index=-1):
        num_cards = len(player.hand)
        if num_cards == 0: return
        start_x = (self.width - (num_cards * (self.card_visual_width + 10))) // 2
        for i, card in enumerate(player.hand):
            if i == skip_index: continue
            x = start_x + i * (self.card_visual_width + 10)
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
        start_x = (self.width - (num_units * (self.card_visual_width + 10))) // 2
        for i, unit in enumerate(player.board):
            x = start_x + i * (self.card_visual_width + 10)
            can_act = unit.can_attack and self.is_player_turn and player == self.player and not self.game_over
            self.draw_card_front(unit, x, y_pos, can_attack=can_act)

    def draw_hero_stats(self, player, x, y, is_opponent=False):
        radius = 35; color = colors.VERMILLION if not player.is_ai else colors.INDIGO
        rect = pygame.Rect(x-radius, y-radius, radius*2, radius*2)
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
        txt = f"Mana: {player.mana}/{player.max_mana}"
        surf = self.fonts['small'].render(txt, True, colors.INDIGO)
        self.screen.blit(surf, (x, y - 40))
        for i in range(10): 
            cx = x + i * 23
            pygame.draw.circle(self.screen, colors.SUMI_GRAY, (cx, y), 9, 1)
            if i < player.mana: pygame.draw.circle(self.screen, colors.INDIGO, (cx, y), 7)
            elif i < player.max_mana: pygame.draw.circle(self.screen, (150, 150, 200), (cx, y), 5)
    
    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        text = self.font_game_over.render(self.winner_message, True, self.win_color)
        rect = text.get_rect(center=(self.width//2, self.height//2 - 50))
        shadow = self.font_game_over.render(self.winner_message, True, (0,0,0))
        self.screen.blit(shadow, (rect.x+4, rect.y+4))
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
            bg_color = colors.VERMILLION; text_color = colors.WASHI_COLOR; text = "Fin de Tour"
        else:
            bg_color = colors.SUMI_GRAY; text_color = (200, 200, 200); text = "Tour Adverse"
        r = self.end_turn_btn
        pygame.draw.rect(self.screen, (50, 50, 50, 100), (r.x+4, r.y+4, r.w, r.h))
        pygame.draw.rect(self.screen, bg_color, r)
        pygame.draw.rect(self.screen, colors.SUMI_BLACK, r, 2)
        t = self.font_button.render(text, True, text_color)
        self.screen.blit(t, t.get_rect(center=r.center))