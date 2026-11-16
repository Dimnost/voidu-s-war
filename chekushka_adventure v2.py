# -*- coding: utf-8 -*-
"""
СНЕЖОК — зимний мультяшный платформер
С физикой льда
"""

import tkinter as tk
import math
import random
import time
import json
import os

W, H = 1100, 650
GRAVITY = 1900
MAX_SPEED = 420
JUMP_FORCE = -820
PLAYER_R = 26

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snezhok_save.json")

# ==================== УРОВНИ ====================

LEVELS = [
    {
        "name": "Снежные холмы",
        "sky": "#b8e0ff",
        "far": "#d0f0ff",
        "hill": "#e8f8ff",
        "ground": "#f0f8ff",
        "ice": False,
        "end": 2700,
        "terrain": [(0,530),(400,530),(650,480),(950,480),(1250,535),(1600,535),(1850,475),(2200,475),(2500,530),(2700,530)],
        "platforms": [(750,400,160),(1400,410,150),(1950,380,170)],
        "ice_platforms": [],
        "crates": [1100,1700],
        "coins": [300,700,1000,1350,1650,2000,2350],
        "spikes": [(1300,),(2100,)],
        "enemies": [1500,2300],
        "boss": None
    },
    {
        "name": "Ледяная тропа",
        "sky": "#a0d0f0",
        "far": "#c0e8f8",
        "hill": "#d8f0ff",
        "ground": "#e8f4ff",
        "ice": True,          # весь уровень скользкий
        "end": 3000,
        "terrain": [(0,520),(500,520),(800,470),(1100,470),(1400,525),(1750,525),(2000,465),(2350,465),(2700,520),(3000,520)],
        "platforms": [(600,390,150),(1200,380,160),(1800,370,170),(2500,360,150)],
        "ice_platforms": [(900,350,180),(2100,340,160)],
        "crates": [1000,1600,2400],
        "coins": [250,650,950,1300,1650,1950,2300,2700],
        "spikes": [(1350,),(2200,)],
        "enemies": [1100,1900,2600],
        "boss": None
    },
    {
        "name": "Морозная долина",
        "sky": "#90c8e8",
        "far": "#b0e0f0",
        "hill": "#d0f0ff",
        "ground": "#e0f0ff",
        "ice": False,
        "end": 3200,
        "terrain": [(0,525),(450,525),(700,475),(1050,475),(1400,530),(1750,530),(2000,470),(2400,470),(2750,525),(3200,525)],
        "platforms": [(550,400,160),(1150,390,170),(1850,375,180),(2550,365,160)],
        "ice_platforms": [(800,360,140),(2200,350,150)],
        "crates": [950,1550,2300],
        "coins": [280,600,900,1250,1600,1900,2250,2600,2950],
        "spikes": [(1300,),(2450,)],
        "enemies": [1050,1800,2700],
        "boss": None
    },
    {
        "name": "Ледяные пещеры",
        "sky": "#70b0d0",
        "far": "#90c8e0",
        "hill": "#b0e0f0",
        "ground": "#d0e8f8",
        "ice": True,
        "end": 3400,
        "terrain": [(0,530),(400,530),(700,480),(1000,480),(1350,535),(1700,535),(2000,475),(2350,475),(2700,530),(3100,530),(3400,490)],
        "platforms": [(600,400,150),(1200,390,160),(1850,375,170),(2500,365,160),(3000,355,140)],
        "ice_platforms": [(900,360,170),(2100,350,160),(2800,340,150)],
        "crates": [1050,1650,2450],
        "coins": [250,550,850,1150,1500,1800,2150,2500,2850,3200],
        "spikes": [(1400,),(2300,),(2900,)],
        "enemies": [950,1750,2550,3100],
        "boss": None
    },
    {
        "name": "Царство снега",
        "sky": "#60a0c8",
        "far": "#80b8d8",
        "hill": "#a0d0e8",
        "ground": "#c8e4f4",
        "ice": False,
        "end": 3600,
        "terrain": [(0,525),(480,525),(750,470),(1100,470),(1450,530),(1800,530),(2100,470),(2500,470),(2850,525),(3200,525),(3600,490)],
        "platforms": [(600,395,160),(1250,380,170),(1950,370,180),(2650,360,170),(3300,350,150)],
        "ice_platforms": [(900,355,150),(2300,345,160)],
        "crates": [1000,1600,2400,3000],
        "coins": [300,650,950,1300,1650,2000,2350,2700,3050,3400],
        "spikes": [(1350,),(2500,),(3100,)],
        "enemies": [1100,1850,2600,3300],
        "boss": None
    },
    {
        "name": "Лорд Мороз",
        "sky": "#4080a8",
        "far": "#6098c0",
        "hill": "#80b0d0",
        "ground": "#a0c8e0",
        "ice": True,
        "end": 2200,
        "terrain": [(0,530),(500,530),(800,480),(1200,480),(1600,530),(2000,530),(2200,500)],
        "platforms": [(600,400,140),(1000,380,150),(1400,370,160)],
        "ice_platforms": [(800,350,180)],
        "crates": [900],
        "coins": [300,700,1100,1500,1900],
        "spikes": [(1300,)],
        "enemies": [1100],
        "boss": {"x": 1900, "hp": 5, "name": "Лорд Мороз"}
    },
]

def clamp(v, a, b):
    return max(a, min(b, v))

def terrain_y(level, x):
    arr = level["terrain"]
    x = clamp(x, 0, level["end"])
    for (x1, y1), (x2, y2) in zip(arr, arr[1:]):
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1)
            t = t * t * (3 - 2 * t)
            return y1 + (y2 - y1) * t
    return 530

class Game:
    def __init__(self, root):
        self.root = root
        root.title("СНЕЖОК — Зимнее приключение")
        root.resizable(False, False)
        root.configure(bg="#0a1520")

        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#0a1520")
        self.c.pack()

        self.keys = set()
        self.screen = "menu"
        self.last = time.perf_counter()
        self.level_index = 0
        self.total_coins = 0
        self.unlocked = 1
        self.particles = []
        self.snow = []
        self.buttons = []
        self.anim_t = 0.0
        self.on_ice = False

        # Создаём снег
        for _ in range(70):
            self.snow.append([
                random.uniform(0, W),
                random.uniform(0, H),
                random.uniform(0.4, 1.3),
                random.uniform(1.0, 2.8)
            ])

        self.load_save()

        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)
        root.bind("<Escape>", lambda e: self.toggle_pause())
        root.bind("<Return>", lambda e: self.on_enter())
        root.bind("<space>", lambda e: self.jump())
        root.bind("p", lambda e: self.toggle_pause())
        root.bind("P", lambda e: self.toggle_pause())

        self.loop()

    def load_save(self):
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self.total_coins = int(data.get("coins", 0))
            self.unlocked = clamp(int(data.get("unlocked", 1)), 1, len(LEVELS))
        except:
            pass

    def save(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"coins": self.total_coins, "unlocked": self.unlocked}, f)
        except:
            pass

    def on_key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        if k in ("space", "w", "up"):
            self.jump()
        if k == "escape":
            self.toggle_pause()

    def on_key_up(self, e):
        self.keys.discard(e.keysym.lower())

    def on_enter(self):
        if self.screen == "menu":
            self.screen = "levels"
        elif self.screen == "levels":
            self.start_level(self.level_index)
        elif self.screen in ("win", "dead"):
            self.start_level(self.level_index)
        elif self.screen == "pause":
            self.screen = "play"

    def toggle_pause(self):
        if self.screen == "play":
            self.screen = "pause"
        elif self.screen == "pause":
            self.screen = "play"

    def jump(self):
        if self.screen == "play" and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.burst(self.x, self.y + PLAYER_R, "#e0f8ff", 10)

    def start_level(self, idx):
        self.level_index = clamp(idx, 0, len(LEVELS) - 1)
        self.level = LEVELS[self.level_index]
        self.x = 100.0
        self.y = terrain_y(self.level, self.x) - PLAYER_R
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.on_ice = False
        self.camera = 0.0
        self.got_coins = set()
        self.dead_enemies = set()
        self.particles = []
        self.boss_hp = self.level["boss"]["hp"] if self.level["boss"] else 0
        self.boss_alive = self.level["boss"] is not None
        self.screen = "play"

    def burst(self, x, y, color, n=8):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(60, 220)
            self.particles.append([x, y, math.cos(a)*s, math.sin(a)*s, 0.5, color, random.uniform(2.5, 5)])

    # ==================== ФИЗИКА ====================

    def update(self, dt):
        self.anim_t += dt

        # Снег всегда падает
        for s in self.snow:
            s[1] += s[3] * 40 * dt
            s[0] += math.sin(self.anim_t + s[2]) * 12 * dt
            if s[1] > H + 10:
                s[1] = -10
                s[0] = random.uniform(0, W)

        if self.screen != "play":
            return

        l = self.level
        left = "a" in self.keys or "left" in self.keys
        right = "d" in self.keys or "right" in self.keys
        direction = int(right) - int(left)

        # === ФИЗИКА ЛЬДА ===
        friction = 2.8 if self.on_ice else 7.5
        accel = 1400 if self.on_ice else 2000

        if direction:
            self.vx += direction * accel * dt
        else:
            self.vx *= max(0.0, 1.0 - friction * dt)

        self.vx = clamp(self.vx, -MAX_SPEED, MAX_SPEED)

        old_y = self.y
        self.x = clamp(self.x + self.vx * dt, PLAYER_R, l["end"] - PLAYER_R)
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        self.on_ground = False
        self.on_ice = False

        # Земля
        ground = terrain_y(l, self.x) - PLAYER_R
        if self.y >= ground and self.vy >= 0:
            self.y = ground
            self.vy = 0
            self.on_ground = True
            if l["ice"]:
                self.on_ice = True

        # Обычные платформы
        for px, py, pw in l["platforms"]:
            if (px - PLAYER_R < self.x < px + pw + PLAYER_R and
                old_y + PLAYER_R <= py + 14 and
                self.y + PLAYER_R >= py and self.vy >= 0):
                self.y = py - PLAYER_R
                self.vy = 0
                self.on_ground = True

        # Ледяные платформы
        for px, py, pw in l["ice_platforms"]:
            if (px - PLAYER_R < self.x < px + pw + PLAYER_R and
                old_y + PLAYER_R <= py + 14 and
                self.y + PLAYER_R >= py and self.vy >= 0):
                self.y = py - PLAYER_R
                self.vy = 0
                self.on_ground = True
                self.on_ice = True

        # Коробки
        for cx in l["crates"]:
            base = terrain_y(l, cx + 25)
            top = base - 48
            if abs(self.x - (cx + 25)) < PLAYER_R + 28:
                if old_y + PLAYER_R <= top + 16 and self.y + PLAYER_R >= top and self.vy >= 0:
                    self.y = top - PLAYER_R
                    self.vy = 0
                    self.on_ground = True
                elif self.y + PLAYER_R > top + 8 and self.y < base:
                    if self.x < cx + 25:
                        self.x = cx - PLAYER_R
                        self.vx = min(self.vx, 0)
                    else:
                        self.x = cx + 50 + PLAYER_R
                        self.vx = max(self.vx, 0)

        # Шипы
        for sx, in l["spikes"]:
            sy = terrain_y(l, sx)
            if abs(self.x - (sx + 28)) < PLAYER_R + 24 and self.y + PLAYER_R > sy - 28:
                self.screen = "dead"

        # Враги
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemies:
                continue
            ey = terrain_y(l, ex) - 18
            if abs(self.x - ex) < PLAYER_R + 20 and abs(self.y - ey) < PLAYER_R + 20:
                if self.vy > 80 and old_y + PLAYER_R < ey + 10:
                    self.dead_enemies.add(i)
                    self.vy = -520
                    self.burst(ex, ey, "#b0f0ff", 12)
                else:
                    self.screen = "dead"

        # Босс
        if self.boss_alive and l["boss"]:
            bx = l["boss"]["x"]
            by = terrain_y(l, bx) - 40
            if abs(self.x - bx) < PLAYER_R + 45 and abs(self.y - by) < PLAYER_R + 45:
                if self.vy > 100 and old_y + PLAYER_R < by + 15:
                    self.boss_hp -= 1
                    self.vy = -600
                    self.burst(bx, by, "#a0e0ff", 18)
                    if self.boss_hp <= 0:
                        self.boss_alive = False
                        self.burst(bx, by, "#ffffff", 25)
                else:
                    self.screen = "dead"

        # Монеты
        for i, cx in enumerate(l["coins"]):
            cy = terrain_y(l, cx) - 80 - (8 if i % 2 else 0)
            if i not in self.got_coins and math.hypot(self.x - cx, self.y - cy) < 40:
                self.got_coins.add(i)
                self.total_coins += 1
                self.burst(cx, cy, "#ffe080", 10)
                self.save()

        if self.y > H + 180:
            self.screen = "dead"

        # Победа
        if self.x > l["end"] - 90:
            if l["boss"] is None or not self.boss_alive:
                self.screen = "win"
                self.unlocked = max(self.unlocked, min(len(LEVELS), self.level_index + 2))
                self.save()

        self.camera = clamp(self.x - W * 0.37, 0, l["end"] - W)

        # Частицы
        for p in self.particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 480 * dt
            p[4] -= dt
            if p[4] <= 0:
                self.particles.remove(p)

    # ==================== ОТРИСОВКА ====================

    def rect(self, x1, y1, x2, y2, fill, outline="", width=1):
        self.c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

    def txt(self, x, y, text, size, color, bold=True, **kw):
        self.c.create_text(x, y, text=text, fill=color,
                           font=("Segoe UI", size, "bold" if bold else "normal"), **kw)

    def button(self, x, y, w, h, label, cmd, sub=None, disabled=False):
        fill = "#1a3048" if disabled else "#2a5580"
        outline = "#4a7080" if disabled else "#80d0f0"
        self.rect(x-w/2, y-h/2, x+w/2, y+h/2, fill, outline, 2)
        if not disabled:
            self.rect(x-w/2+2, y-h/2+2, x+w/2-2, y-h/2+7, "#3a70a0")
        self.txt(x, y-3 if sub else y, label, 15, "#90b0c0" if disabled else "#ffffff")
        if sub:
            self.txt(x, y+15, sub, 10, "#a0c8d8", False)
        self.buttons.append((x-w/2, y-h/2, x+w/2, y+h/2, cmd, disabled))

    def on_click(self, e):
        for x1, y1, x2, y2, cmd, dis in reversed(self.buttons):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2 and not dis:
                cmd()
                return

    def draw_sky(self):
        l = self.level
        self.c.configure(bg=l["sky"])

        # Снежинки на фоне
        for s in self.snow:
            r = s[2] * 2.2
            self.c.create_oval(s[0]-r, s[1]-r, s[0]+r, s[1]+r, fill="#ffffff", outline="")

        # Дальние холмы
        for i in range(-1, 10):
            x = i * 300 - (self.camera * 0.25) % 300
            self.c.create_oval(x, 300, x+420, 600, fill=l["far"], outline="")
            self.c.create_oval(x+120, 340, x+500, 620, fill=l["hill"], outline="")

    def draw_world(self):
        l = self.level
        cam = self.camera

        # Земля
        pts = []
        for x in range(max(0, int(cam)-40), min(l["end"], int(cam)+W+50), 12):
            pts.extend((x-cam, terrain_y(l, x)))
        pts.extend((W+50, H+50, -50, H+50))
        self.c.create_polygon(*pts, fill=l["ground"], outline="")

        # Снежный край
        edge = []
        for x in range(max(0, int(cam)-40), min(l["end"], int(cam)+W+50), 12):
            edge.extend((x-cam, terrain_y(l, x)))
        self.c.create_line(*edge, fill="#ffffff", width=14, smooth=True)
        self.c.create_line(*edge, fill="#e0f4ff", width=5, smooth=True)

        # Обычные платформы
        for px, py, pw in l["platforms"]:
            sx = px - cam
            self.rect(sx, py, sx+pw, py+18, "#d0e8f8", "#80a0b8", 2)
            self.rect(sx, py, sx+pw, py+6, "#ffffff")

        # Ледяные платформы (более голубые и блестящие)
        for px, py, pw in l["ice_platforms"]:
            sx = px - cam
            self.rect(sx, py, sx+pw, py+16, "#a0e0ff", "#60b0d8", 2)
            self.rect(sx, py, sx+pw, py+5, "#e0f8ff")
            # Блики
            for i in range(3):
                self.rect(sx + 15 + i*40, py+2, sx + 30 + i*40, py+5, "#ffffff")

        # Коробки
        for cx in l["crates"]:
            sx = cx - cam
            gy = terrain_y(l, cx+25)
            self.rect(sx, gy-48, sx+50, gy, "#e8f0f8", "#80a0b0", 2)
            self.c.create_line(sx+5, gy-43, sx+45, gy-5, fill="#c0d8e8", width=2)
            self.c.create_line(sx+45, gy-43, sx+5, gy-5, fill="#c0d8e8", width=2)

        # Шипы (сосульки)
        for sx, in l["spikes"]:
            x = sx - cam
            y = terrain_y(l, sx)
            self.c.create_polygon(x, y, x+15, y-36, x+30, y, fill="#d0f0ff", outline="#80b0c8", width=2)
            self.c.create_polygon(x+20, y, x+35, y-30, x+50, y, fill="#c0e8ff", outline="#80b0c8", width=2)

        # Враги (снежные слаймы)
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemies:
                continue
            x = ex - cam
            y = terrain_y(l, ex) - 16
            bounce = math.sin(self.anim_t * 5 + i) * 2
            self.c.create_oval(x-18, y-16+bounce, x+18, y+18+bounce, fill="#e0f4ff", outline="#80b0c8", width=3)
            self.c.create_oval(x-9, y-6+bounce, x-2, y+3+bounce, fill="#406080", outline="")
            self.c.create_oval(x+2, y-6+bounce, x+9, y+3+bounce, fill="#406080", outline="")

        # Босс
        if self.boss_alive and l["boss"]:
            bx = l["boss"]["x"] - cam
            by = terrain_y(l, l["boss"]["x"]) - 50
            # Тело
            self.c.create_oval(bx-42, by-35, bx+42, by+45, fill="#c0e8ff", outline="#5090b0", width=4)
            # Глаза
            self.c.create_oval(bx-22, by-15, bx-6, by+5, fill="white", outline="")
            self.c.create_oval(bx+6, by-15, bx+22, by+5, fill="white", outline="")
            self.c.create_oval(bx-16, by-8, bx-9, by+1, fill="#203040", outline="")
            self.c.create_oval(bx+10, by-8, bx+17, by+1, fill="#203040", outline="")
            # Корона
            self.c.create_polygon(bx-20, by-35, bx-10, by-55, bx, by-35, bx+10, by-55, bx+20, by-35,
                                  fill="#ffe080", outline="#d0a020", width=2)
            # HP
            self.rect(bx-40, by-70, bx+40, by-60, "#305060")
            self.rect(bx-40, by-70, bx-40 + 80*(self.boss_hp/l["boss"]["hp"]), by-60, "#60d0ff")

        # Монеты
        for i, cx in enumerate(l["coins"]):
            if i in self.got_coins:
                continue
            x = cx - cam
            y = terrain_y(l, cx) - 80 - (8 if i % 2 else 0)
            pulse = 1 + math.sin(self.anim_t*5 + i)*0.1
            r = 11 * pulse
            self.c.create_oval(x-r, y-r, x+r, y+r, fill="#ffe040", outline="#fff0a0", width=2)

        # Флаг
        fx = l["end"] - 80 - cam
        fy = terrain_y(l, l["end"]-80)
        self.rect(fx-3, fy-120, fx+3, fy, "#6090a8")
        wave = math.sin(self.anim_t*3.5)*5
        self.c.create_polygon(fx, fy-120, fx+65+wave, fy-100, fx, fy-80, fill="#80e0ff", outline="#e0f8ff", width=2)

    def draw_player(self):
        x = self.x - self.camera
        y = self.y

        # Тень
        gy = terrain_y(self.level, self.x)
        self.c.create_oval(x-18, gy-3, x+18, gy+5, fill="#80a0b0", outline="")

        # Тело (мультяшный шарик)
        self.c.create_oval(x-PLAYER_R, y-PLAYER_R, x+PLAYER_R, y+PLAYER_R,
                           fill="#ff6b6b", outline="#c04040", width=3)
        # Блик
        self.c.create_oval(x-14, y-16, x-2, y-6, fill="#ffb0b0", outline="")

        # Глаза
        self.c.create_oval(x-13, y-8, x-3, y+5, fill="white", outline="")
        self.c.create_oval(x+3, y-8, x+13, y+5, fill="white", outline="")
        self.c.create_oval(x-9, y-3, x-5, y+3, fill="#203040", outline="")
        self.c.create_oval(x+7, y-3, x+11, y+3, fill="#203040", outline="")

        # Улыбка
        self.c.create_arc(x-10, y+2, x+10, y+16, start=200, extent=140, style=tk.ARC, outline="#c04040", width=2)

        # Шапка
        self.c.create_polygon(x-22, y-PLAYER_R+4, x, y-PLAYER_R-18, x+22, y-PLAYER_R+4,
                              fill="#4080c0", outline="#2060a0", width=2)
        self.c.create_oval(x-6, y-PLAYER_R-22, x+6, y-PLAYER_R-10, fill="#ffffff", outline="")

        # Если на льду — индикатор
        if self.on_ice:
            self.txt(x, y - PLAYER_R - 28, "❄", 14, "#80e0ff")

    def draw_hud(self):
        self.rect(12, 10, 300, 70, "#0a2030", "#60c0e0", 2)
        self.txt(24, 28, "СНЕЖОК", 14, "#a0e0ff", anchor="w")
        self.txt(24, 50, f"Монеты: {len(self.got_coins)}/{len(self.level['coins'])}", 11, "#e0f4ff", anchor="w")

        self.rect(400, 18, 720, 34, "#1a3850")
        prog = self.x / self.level["end"]
        self.rect(400, 18, 400 + 320*prog, 34, "#60d0ff")
        self.txt(560, 48, self.level["name"], 10, "#ffffff")

        self.rect(860, 12, 1080, 52, "#0a2030", "#60c0e0", 2)
        self.txt(970, 32, f"★ {self.total_coins}", 14, "#ffe080")

        if self.on_ice:
            self.txt(W/2, 30, "❄ СКОЛЬЗКО ❄", 12, "#80e0ff")

    def draw_particles(self):
        for x, y, vx, vy, life, col, size in self.particles:
            sx = x - self.camera
            if -20 < sx < W+20:
                r = max(1.5, size * life / 0.5)
                self.c.create_oval(sx-r, y-r, sx+r, y+r, fill=col, outline="")

    def draw_panel(self, title, sub):
        self.rect(0, 0, W, H, "#0a1525")
        for x, y, r in [(70, 60, 90), (1030, 570, 160)]:
            self.c.create_oval(x-r, y-r, x+r, y+r, fill="#102535", outline="")
        self.txt(W/2, 105, title, 36, "#a0e0ff")
        self.txt(W/2, 155, sub, 14, "#c0e0f0", False)

    def draw(self):
        self.c.delete("all")
        self.buttons = []

        if self.screen in ("play", "pause", "win", "dead"):
            self.draw_sky()
            self.draw_world()
            self.draw_particles()
            self.draw_player()
            self.draw_hud()

        if self.screen == "menu":
            self.draw_panel("СНЕЖОК", "Зимнее мультяшное приключение")
            self.buttons = []
            self.button(W/2, 280, 300, 54, "ИГРАТЬ", lambda: setattr(self, "screen", "levels"))
            self.button(W/2, 355, 300, 46, "ВЫХОД", self.root.destroy)
            self.txt(W/2, 470, "A / D — бег     SPACE — прыжок     P — пауза", 13, "#90c0d8", False)
            self.txt(W/2, 510, "На льду персонаж сильно скользит!", 12, "#70b0d0", False)

        elif self.screen == "levels":
            self.draw_panel("ВЫБОР УРОВНЯ", "Пройди уровень, чтобы открыть следующий")
            self.buttons = []
            for i, lvl in enumerate(LEVELS):
                col = i % 2
                row = i // 2
                x = W/2 + (col-0.5)*340
                y = 245 + row*80
                locked = i+1 > self.unlocked
                self.button(x, y, 300, 58,
                            ("🔒 " if locked else f"{i+1}. ") + lvl["name"],
                            lambda j=i: self.start_level(j),
                            "Босс!" if lvl["boss"] else ("Лёд" if lvl["ice"] else ""),
                            locked)
            self.button(W/2, 580, 200, 42, "НАЗАД", lambda: setattr(self, "screen", "menu"))

        elif self.screen == "pause":
            self.rect(0, 0, W, H, "#0a1525")
            self.txt(W/2, 220, "ПАУЗА", 38, "#a0e0ff")
            self.buttons = []
            self.button(W/2, 340, 230, 50, "В МЕНЮ", lambda: setattr(self, "screen", "menu"))

        elif self.screen == "dead":
            self.rect(0, 0, W, H, "#0a1525")
            self.txt(W/2, 210, "ОЙ!", 40, "#ff8090")
            self.txt(W/2, 270, "Попробуй ещё раз", 15, "#c0e0f0", False)
            self.buttons = []
            self.button(W/2, 360, 240, 50, "ПОВТОРИТЬ", lambda: self.start_level(self.level_index))
            self.button(W/2, 430, 240, 44, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))

        elif self.screen == "win":
            self.rect(0, 0, W, H, "#0a1525")
            self.txt(W/2, 190, "УРОВЕНЬ ПРОЙДЕН!", 34, "#a0e0ff")
            self.txt(W/2, 250, f"Монеты: {len(self.got_coins)}/{len(self.level['coins'])}", 15, "#ffffff", False)
            self.buttons = []
            if self.level_index < len(LEVELS)-1:
                self.button(W/2, 340, 280, 50, "СЛЕДУЮЩИЙ", lambda: self.start_level(self.level_index+1))
            self.button(W/2, 410, 280, 44, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))

        self.c.bind("<Button-1>", self.on_click)

    def loop(self):
        now = time.perf_counter()
        dt = min(now - self.last, 0.033)
        self.last = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
