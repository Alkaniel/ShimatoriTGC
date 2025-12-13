import pygame
import json
import os
import math
import constants.colors as colors
from utils.game_state import GameState

class OptionsMenu(GameState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        self.settings = self.load_settings()
        
        # Appliquer les paramètres au lancement (volume uniquement)
        self.apply_settings(init_phase=True)
        
        self.options = [
            {"name": "Volume Musique", "type": "slider", "key": "music_volume", "min": 0, "max": 100, "step": 5},
            {"name": "Volume Effets", "type": "slider", "key": "sfx_volume", "min": 0, "max": 100, "step": 5},
            # Retour au simple Toggle ON/OFF
            {"name": "Plein Écran", "type": "toggle", "key": "fullscreen"},
            {"name": "Résolution", "type": "choice", "key": "resolution", "choices": ["1280x720", "1600x900", "1920x1080"]},
            {"name": "Langue", "type": "choice", "key": "language", "choices": ["Français", "English", "日本語"]},
            {"name": "Vsync", "type": "toggle", "key": "vsync"}
        ]
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_options = 6
        self.save_message_timer = 0
        
        self.btn_save_rect = None
        self.btn_back_rect = None

    def load_settings(self):
        default = {
            "music_volume": 70, 
            "sfx_volume": 80, 
            "fullscreen": False, # Simple booléen
            "resolution": "1280x720", 
            "language": "Français", 
            "vsync": True
        }
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default, **json.load(f)}
        except Exception as e:
            print(f"Erreur config: {e}")
        return default

    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            self.apply_settings()
            self.save_message_timer = 120
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")

    def apply_settings(self, init_phase=False):
        # 1. Audio
        try:
            pygame.mixer.music.set_volume(self.settings["music_volume"] / 100)
        except:
            pass
        
        # 2. Vidéo
        if not init_phase:
            # Récupération de la résolution fenêtrée choisie
            try:
                res_w, res_h = map(int, self.settings["resolution"].split('x'))
            except:
                res_w, res_h = 1280, 720

            # Logique Plein Écran vs Fenêtré
            if self.settings["fullscreen"]:
                # En plein écran, on utilise la résolution NATIVE de l'écran pour la netteté
                info = pygame.display.Info()
                target_w = info.current_w
                target_h = info.current_h
                target_flags = pygame.FULLSCREEN
            else:
                # En fenêtré, on utilise la résolution choisie
                target_w = res_w
                target_h = res_h
                target_flags = 0

            # Vérification update
            current_w, current_h = self.game.screen.get_size()
            current_flags = self.game.screen.get_flags()
            
            flags_changed = (bool(current_flags & pygame.FULLSCREEN) != bool(target_flags & pygame.FULLSCREEN))
            need_update = (target_w != current_w) or (target_h != current_h) or flags_changed
            
            if need_update:
                # Recréation fenêtre
                new_screen = pygame.display.set_mode((target_w, target_h), target_flags)
                
                # Mise à jour références
                self.game.screen = new_screen
                self.game.width = target_w
                self.game.height = target_h
                
                # Déclenchement du RESPONSIVE sur tous les menus
                for state in self.game.states.values():
                    if state:
                        state.screen = new_screen
                        if hasattr(state, 'on_resize'):
                            state.on_resize(target_w, target_h)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
                    if self.selected_index >= self.scroll_offset + self.max_visible_options:
                        self.scroll_offset = self.selected_index - self.max_visible_options + 1
                elif event.key == pygame.K_LEFT:
                    self.adjust_option(-1)
                elif event.key == pygame.K_RIGHT:
                    self.adjust_option(1)
                elif event.key == pygame.K_RETURN:
                    opt = self.options[self.selected_index]
                    if opt["type"] == "toggle":
                        self.adjust_option(0)
                elif event.key == pygame.K_ESCAPE:
                    self.game.change_state("menu")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.btn_save_rect and self.btn_save_rect.collidepoint(mouse_pos):
                        self.save_settings()
                    elif self.btn_back_rect and self.btn_back_rect.collidepoint(mouse_pos):
                        self.game.change_state("menu")
                    
                    visible_end = min(len(self.options), self.scroll_offset + self.max_visible_options)
                    for i in range(self.scroll_offset, visible_end):
                        opt = self.options[i]
                        if opt["type"] == "slider" and "slider_rect" in opt:
                            if opt["slider_rect"].collidepoint(mouse_pos):
                                self.selected_index = i
                                relative_x = mouse_pos[0] - opt["slider_rect"].x
                                ratio = relative_x / opt["slider_rect"].width
                                val = int(ratio * opt["max"])
                                val = round(val / opt["step"]) * opt["step"]
                                self.settings[opt["key"]] = max(opt["min"], min(opt["max"], val))
                        elif "rect" in opt and opt["rect"].collidepoint(mouse_pos):
                            self.selected_index = i
                            direction = 1 if opt["type"] == "choice" else 0
                            self.adjust_option(direction)

    def adjust_option(self, direction):
        opt = self.options[self.selected_index]
        key = opt["key"]
        if opt["type"] == "slider":
            new_val = self.settings[key] + (direction * opt["step"])
            self.settings[key] = max(opt["min"], min(opt["max"], new_val))
        elif opt["type"] == "toggle":
            self.settings[key] = not self.settings[key]
        elif opt["type"] == "choice":
            choices = opt["choices"]
            try:
                curr_idx = choices.index(self.settings[key])
                new_idx = (curr_idx + direction) % len(choices)
                self.settings[key] = choices[new_idx]
            except:
                self.settings[key] = choices[0]

    def update(self):
        if self.save_message_timer > 0:
            self.save_message_timer -= 1

    def draw(self):
        super().draw()
        title = self.fonts['title'].render("OPTIONS", True, colors.SUMI_BLACK)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 80)))

        start_y = 200
        visible_end = min(self.scroll_offset + self.max_visible_options, len(self.options))
        
        for i in range(self.scroll_offset, visible_end):
            opt = self.options[i]
            y_pos = start_y + (i - self.scroll_offset) * 70
            is_selected = (i == self.selected_index)
            
            opt_rect = pygame.Rect(self.width//2 - 350, y_pos - 25, 700, 50)
            opt["rect"] = opt_rect
            
            if is_selected:
                s = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                s.fill((*colors.VERMILLION, 50))
                self.screen.blit(s, opt_rect)
                pygame.draw.rect(self.screen, colors.VERMILLION, opt_rect, 2, border_radius=5)
            
            name_surf = self.fonts['subtitle'].render(opt["name"], True, colors.SUMI_BLACK)
            self.screen.blit(name_surf, (opt_rect.x + 20, y_pos - 15))
            
            right_x = opt_rect.right - 20
            
            if opt["type"] == "slider":
                slider_w = 200
                slider_h = 10
                slider_rect = pygame.Rect(right_x - slider_w - 50, y_pos - 5, slider_w, slider_h)
                opt["slider_rect"] = slider_rect
                pygame.draw.rect(self.screen, colors.SUMI_GRAY, slider_rect, border_radius=5)
                pct = self.settings[opt["key"]] / opt["max"]
                fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, slider_rect.width * pct, slider_rect.height)
                pygame.draw.rect(self.screen, colors.VERMILLION, fill_rect, border_radius=5)
                val_surf = self.fonts['small'].render(f"{self.settings[opt['key']]}%", True, colors.SUMI_GRAY)
                self.screen.blit(val_surf, (right_x - 40, y_pos - 10))
                
            elif opt["type"] == "toggle":
                val = self.settings[opt["key"]]
                text = "ON" if val else "OFF"
                col = colors.VERMILLION if val else colors.SUMI_GRAY
                val_surf = self.fonts['subtitle'].render(text, True, col)
                self.screen.blit(val_surf, val_surf.get_rect(midright=(right_x, y_pos)))
                
            elif opt["type"] == "choice":
                val = str(self.settings[opt["key"]])
                val_surf = self.fonts['small'].render(val, True, colors.SUMI_GRAY)
                val_rect = val_surf.get_rect(midright=(right_x - 20, y_pos))
                self.screen.blit(val_surf, val_rect)
                if is_selected:
                    arrow_l = self.fonts['small'].render("<", True, colors.VERMILLION)
                    self.screen.blit(arrow_l, (val_rect.left - 20, val_rect.top))
                    arrow_r = self.fonts['small'].render(">", True, colors.VERMILLION)
                    self.screen.blit(arrow_r, (val_rect.right + 10, val_rect.top))

        btn_y = self.height - 80
        save_surf = self.fonts['button'].render("Sauvegarder", True, colors.SUMI_BLACK)
        self.btn_save_rect = save_surf.get_rect(center=(self.width//2 - 150, btn_y))
        pygame.draw.rect(self.screen, colors.WASHI_COLOR, self.btn_save_rect.inflate(20, 10))
        pygame.draw.rect(self.screen, colors.VERMILLION, self.btn_save_rect.inflate(20, 10), 2)
        self.screen.blit(save_surf, self.btn_save_rect)
        
        back_surf = self.fonts['button'].render("Retour", True, colors.SUMI_BLACK)
        self.btn_back_rect = back_surf.get_rect(center=(self.width//2 + 150, btn_y))
        self.screen.blit(back_surf, self.btn_back_rect)
        
        if self.save_message_timer > 0:
            msg = self.fonts['small'].render("Paramètres appliqués !", True, colors.VERMILLION)
            self.screen.blit(msg, msg.get_rect(center=(self.width//2, btn_y - 50)))