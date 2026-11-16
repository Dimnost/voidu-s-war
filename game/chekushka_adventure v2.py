# -*- coding: utf-8 -*-
"""
ЧЕКУШКА 2D — платформер
Картинка игрока: player.png (положи рядом с этим файлом)
"""

import tkinter as tk
from tkinter import messagebox
import math
import random
import time
import json
import os
import sys

# ==================== НАСТРОЙКИ ====================

W, H = 1100, 650
GRAVITY = 1850
MAX_SPEED = 430
JUMP_FORCE = -780
PLAYER_W = 54
PLAYER_H = 54

APP_VERSION = "3.0.0"
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chekushka_save.json")
PLAYER_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player.png")

# ==================== УРОВНИ ====================

LEVELS = [
    {
        "name": "Зелёные холмы",
        "subtitle": "Разомнись",
        "sky": "#7ec8ff",
        "far": "#a8d4a0",
        "hill": "#6bb87a",
        "ground": "#8b5a3c",
        "grass": "#5dcf66",
        "end": 2800,
        "terrain": [(0,520),(400,520),(650,470),(950,470),(1200,520),(1550,520),(1800,460),(2150,460),(2400,510),(2800,510)],
        "platforms": [(750,400,170),(1350,410,160),(1900,370,180),(2450,390,160)],
        "crates": [1050,1600,2200],
        "coins": [350,700,1100,1450,1750,2050,2350,2600],
        "spikes": [(1250,),(2100,)],
        "enemies": [1500,2300]
    },
    {
        "name": "Пустынный забег",
        "subtitle": "Жарко и опасно",
        "sky": "#ffc48a",
        "far": "#e8c090",
        "hill": "#d4a06a",
        "ground": "#a86b3c",
        "grass": "#e8b86a",
        "end": 3100,
        "terrain": [(0,510),(500,510),(750,455),(1050,455),(1350,520),(1700,520),(1950,460),(2300,460),(2600,515),(3100,515)],
        "platforms": [(600,370,160),(1150,365,180),(1750,370,170),(2350,355,190),(2800,350,150)],
        "crates": [950,1500,2100,2650],
        "coins": [300,650,900,1250,1600,1900,2200,2500,2850],
        "spikes": [(1300,),(2050,),(2750,)],
        "enemies": [1100,1850,2550]
    },
    {
        "name": "Ледяные пещеры",
        "subtitle": "Скользко",
        "sky": "#9ad0f0",
        "far": "#b8e0f0",
        "hill": "#7ab8d0",
        "ground": "#5a8090",
        "grass": "#c0f0ff",
        "end": 3300,
        "terrain": [(0,515),(450,515),(700,460),(1000,460),(1300,520),(1650,520),(1900,455),(2250,455),(2550,515),(2900,515),(3300,470)],
        "platforms": [(750,370,170),(1250,385,170),(1800,355,180),(2400,365,170),(2950,340,180)],
        "crates": [1050,1600,2150,2700],
        "coins": [280,600,950,1200,1500,1750,2050,2350,2650,3000],
        "spikes": [(1200,),(2300,),(2850,)],
        "enemies": [950,1950,2600]
    },
    {
        "name": "Ночная долина",
        "subtitle": "Темнеет",
        "sky": "#1e2a50",
        "far": "#2e3e68",
        "hill": "#24355a",
        "ground": "#4a3c55",
        "grass": "#60b070",
        "end": 3500,
        "terrain": [(0,515),(480,515),(720,465),(1050,465),(1350,520),(1700,520),(1950,455),(2300,455),(2600,520),(2950,520),(3200,460),(3500,460)],
        "platforms": [(580,375,180),(1150,360,180),(1750,350,190),(2350,355,180),(2900,340,190),(3250,330,150)],
        "crates": [950,1550,2150,2700,3150],
        "coins": [260,600,850,1200,1550,1850,2150,2500,2800,3050,3350],
        "spikes": [(1280,),(2450,),(3000,)],
        "enemies": [1050,1900,2650,3200]
    },
    {
        "name": "Вулканические земли",
        "subtitle": "Горячо!",
        "sky": "#3a1e1e",
        "far": "#5a3030",
        "hill": "#4a2828",
        "ground": "#6b3a2a",
        "grass": "#c06030",
        "end": 3600,
        "terrain": [(0,520),(420,520),(680,470),(1000,470),(1300,525),(1650,525),(1900,465),(2250,465),(2550,520),(2900,520),(3200,470),(3600,470)],
        "platforms": [(550,380,170),(1100,370,180),(1700,360,180),(2300,355,190),(2850,345,170),(3300,335,160)],
        "crates": [900,1500,2050,2600,3100],
        "coins": [250,580,820,1150,1480,1800,2100,2450,2750,3050,3400],
        "spikes": [(1250,),(2400,),(2950,)],
        "enemies": [1000,1850,2550,3250]
    },
    {
        "name": "Небесные острова",
        "subtitle": "Высоко и красиво",
        "sky": "#a0d8ff",
        "far": "#c0e8ff",
        "hill": "#90c8e0",
        "ground": "#7a9ab0",
        "grass": "#b0e0a0",
        "end": 3800,
        "terrain": [(0,530),(500,530),(800,480),(1200,480),(1500,535),(1900,535),(2200,475),(2600,475),(2900,530),(3300,530),(3600,480),(3800,480)],
        "platforms": [(650,390,180),(1300,380,190),(2000,370,200),(2700,360,190),(3400,350,180)],
        "crates": [1000,1650,2300,3000,3550],
        "coins": [300,700,1100,1450,1800,2150,2500,2850,3200,3550],
        "spikes": [(1400,),(2500,),(3200,)],
        "enemies": [1150,2050,2800,3500]
    },
    {
        "name": "Финал",
        "subtitle": "Последний рывок",
        "sky": "#2a1a40",
        "far": "#3a2a55",
        "hill": "#2e2248",
        "ground": "#4a3555",
        "grass": "#80c070",
        "end": 4000,
        "terrain": [(0,520),(450,520),(700,465),(1050,465),(1400,525),(1750,525),(2000,460),(2400,460),(2750,520),(3100,520),(3400,465),(3700,465),(4000,510)],
        "platforms": [(600,380,180),(1200,370,190),(1850,355,200),(2500,350,190),(3050,340,180),(3600,330,170)],
        "crates": [950,1600,2200,2800,3300,3750],
        "coins": [280,650,950,1300,1650,1950,2300,2650,2950,3250,3550,3850],
        "spikes": [(1350,),(2450,),(3150,),(3700,)],
        "enemies": [1100,1950,2700,3400,3850]
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
    return 520

# ==================== ИГРА ====================

class Game:
    def __init__(self, root):
        self.root = root
        root.title("ЧЕКУШКА 2D")
        root.resizable(False, False)
        root.configure(bg="#0d1520")

        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#0d1520")
        self.c.pack()

        self.keys = set()
        self.screen = "menu"
        self.last = time.perf_counter()
        self.level_index = 0
        self.total_coins = 0
        self.unlocked = 1
        self.particles = []
        self.buttons = []
        self.anim_t = 0.0
        self.player_img = None
        self.player_photo = None

        self.load_player_image()
        self.load_save()

        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)
        root.bind("<Escape>", lambda e: self.toggle_pause())
        root.bind("<Return>", lambda e: self.on_enter())
        root.bind("<space>", lambda e: self.jump())
        root.bind("p", lambda e: self.toggle_pause())
        root.bind("P", lambda e: self.toggle_pause())
        root.bind("r", lambda e: self.start_level(self.level_index) if self.screen == "play" else None)

        self.loop()

    def load_player_image(self):
        try:
            from PIL import Image, ImageTk
            # Если есть Pillow — лучше качество
            img = Image.open(PLAYER_IMAGE).convert("RGBA")
            img = img.resize((PLAYER_W, PLAYER_H), Image.LANCZOS)
            self.player_photo = ImageTk.PhotoImage(img)
            self.player_img = self.player_photo
        except Exception:
            try:
                # Обычный PhotoImage (работает без Pillow)
                self.player_photo = tk.PhotoImage(file=PLAYER_IMAGE)
                # Простое уменьшение если слишком большое
                w = self.player_photo.width()
                h = self.player_photo.height()
                if w > PLAYER_W * 2 or h > PLAYER_H * 2:
                    factor = max(w // PLAYER_W, h // PLAYER_H, 1)
                    self.player_photo = self.player_photo.subsample(factor, factor)
                self.player_img = self.player_photo
            except Exception:
                self.player_img = None
                print("Не найден player.png — будет использоваться запасной персонаж")

    def load_save(self):
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self.total_coins = int(data.get("coins", 0))
            self.unlocked = clamp(int(data.get("unlocked", 1)), 1, len(LEVELS))
        except Exception:
            pass

    def save(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "coins": self.total_coins,
                    "unlocked": self.unlocked
                }, f)
        except Exception:
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
            self.burst(self.x, self.y + PLAYER_H // 2, "#d0f0ff", 9)

    def start_level(self, idx):
        self.level_index = clamp(idx, 0, len(LEVELS) - 1)
        self.level = LEVELS[self.level_index]
        self.x = 100.0
        self.y = terrain_y(self.level, self.x) - PLAYER_H
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.camera = 0.0
        self.got_coins = set()
        self.dead_enemies = set()
        self.particles = []
        self.screen = "play"

    def burst(self, x, y, color, n=10):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(80, 260)
            self.particles.append([
                x, y,
                math.cos(a) * s,
                math.sin(a) * s,
                0.55,
                color,
                random.uniform(2.8, 5.5)
            ])

    # ==================== ФИЗИКА ====================

    def update(self, dt):
        self.anim_t += dt
        if self.screen != "play":
            return

        l = self.level
        left = "a" in self.keys or "left" in self.keys
        right = "d" in self.keys or "right" in self.keys
        direction = int(right) - int(left)

        if direction:
            self.vx += direction * 1900 * dt
        else:
            self.vx *= max(0.0, 1.0 - 7.0 * dt)

        self.vx = clamp(self.vx, -MAX_SPEED, MAX_SPEED)

        old_y = self.y
        self.x = clamp(self.x + self.vx * dt, PLAYER_W // 2, l["end"] - PLAYER_W // 2)
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        self.on_ground = False

        # Земля
        ground = terrain_y(l, self.x) - PLAYER_H
        if self.y >= ground and self.vy >= 0:
            self.y = ground
            self.vy = 0
            self.on_ground = True

        # Платформы
        for px, py, pw in l["platforms"]:
            if (px - PLAYER_W // 2 < self.x < px + pw + PLAYER_W // 2 and
                old_y + PLAYER_H <= py + 12 and
                self.y + PLAYER_H >= py and
                self.vy >= 0):
                self.y = py - PLAYER_H
                self.vy = 0
                self.on_ground = True

        # Коробки (исправленная физика)
        for cx in l["crates"]:
            crate_w = 50
            crate_h = 50
            crate_center = cx + crate_w / 2
            base = terrain_y(l, cx + 25)
            top = base - crate_h

            if abs(self.x - crate_center) < PLAYER_W // 2 + crate_w / 2 + 3:
                # Стоим сверху
                if (old_y + PLAYER_H <= top + 16 and
                    self.y + PLAYER_H >= top and
                    self.vy >= 0):
                    self.y = top - PLAYER_H
                    self.vy = 0
                    self.on_ground = True
                # Упираемся сбоку
                elif self.y + PLAYER_H > top + 10 and self.y < base:
                    if self.x < crate_center:
                        self.x = crate_center - (crate_w / 2 + PLAYER_W // 2)
                        if self.vx > 0:
                            self.vx = 0
                    else:
                        self.x = crate_center + (crate_w / 2 + PLAYER_W // 2)
                        if self.vx < 0:
                            self.vx = 0

        # Шипы
        for sx, in l["spikes"]:
            sy = terrain_y(l, sx)
            if abs(self.x - (sx + 30)) < PLAYER_W // 2 + 26 and self.y + PLAYER_H > sy - 30:
                self.screen = "dead"

        # Враги
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemies:
                continue
            ey = terrain_y(l, ex) - 20
            if abs(self.x - ex) < PLAYER_W // 2 + 20 and abs(self.y + PLAYER_H // 2 - ey) < PLAYER_H // 2 + 20:
                if self.vy > 100 and old_y + PLAYER_H < ey + 10:
                    self.dead_enemies.add(i)
                    self.vy = -500
                    self.burst(ex, ey, "#b0f0a0", 14)
                else:
                    self.screen = "dead"

        # Монеты
        for i, cx in enumerate(l["coins"]):
            cy = terrain_y(l, cx) - 85 - (10 if i % 2 else 0)
            if i not in self.got_coins and math.hypot(self.x - cx, self.y + PLAYER_H // 2 - cy) < 42:
                self.got_coins.add(i)
                self.total_coins += 1
                self.burst(cx, cy, "#ffd040", 12)
                self.save()

        if self.y > H + 200:
            self.screen = "dead"

        if self.x > l["end"] - 100:
            self.screen = "win"
            self.unlocked = max(self.unlocked, min(len(LEVELS), self.level_index + 2))
            self.save()

        self.camera = clamp(self.x - W * 0.38, 0, l["end"] - W)

        # Частицы
        for p in self.particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 500 * dt
            p[4] -= dt
            if p[4] <= 0:
                self.particles.remove(p)

    # ==================== ОТРИСОВКА ====================

    def draw_rect(self, x1, y1, x2, y2, fill, outline="", width=1):
        self.c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

    def draw_text(self, x, y, text, size, color, bold=True, **kwargs):
        self.c.create_text(x, y, text=text, fill=color,
                           font=("Segoe UI", size, "bold" if bold else "normal"), **kwargs)

    def button(self, x, y, w, h, label, command, sub=None, disabled=False):
        fill = "#1a2e42" if disabled else "#254a68"
        outline = "#4a6a82" if disabled else "#7ec8e0"
        self.draw_rect(x - w/2, y - h/2, x + w/2, y + h/2, fill, outline, 2)
        if not disabled:
            self.draw_rect(x - w/2 + 2, y - h/2 + 2, x + w/2 - 2, y - h/2 + 7, "#3a6a88")
        self.draw_text(x, y - 3 if sub else y, label, 15, "#8aa8bc" if disabled else "#ffffff")
        if sub:
            self.draw_text(x, y + 15, sub, 10, "#a8c8d8", False)
        self.buttons.append((x - w/2, y - h/2, x + w/2, y + h/2, command, disabled))

    def on_click(self, e):
        for x1, y1, x2, y2, cmd, disabled in reversed(self.buttons):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2 and not disabled:
                cmd()
                return

    def draw_sky(self):
        l = self.level
        self.c.configure(bg=l["sky"])

        # Облака
        for x, y, s in [(120, 90, 1.0), (480, 140, 0.9), (850, 85, 1.1),
                        (1250, 125, 0.95), (1900, 80, 1.05), (2550, 130, 0.9), (3200, 95, 1.0)]:
            sx = (x - self.camera * 0.15) % (W + 220) - 110
            size = 65 * s
            self.c.create_oval(sx, y, sx + size, y + size * 0.42, fill="#f5fcff", outline="")
            self.c.create_oval(sx + size * 0.3, y - size * 0.22, sx + size * 1.1, y + size * 0.42, fill="#f5fcff", outline="")
            self.c.create_oval(sx + size * 0.7, y, sx + size * 1.5, y + size * 0.42, fill="#f5fcff", outline="")

        # Холмы
        for i in range(-1, 10):
            x = i * 290 - (self.camera * 0.32) % 290
            self.c.create_oval(x, 310, x + 400, 590, fill=l["far"], outline="")
            self.c.create_oval(x + 110, 350, x + 480, 600, fill=l["hill"], outline="")

    def draw_world(self):
        l = self.level
        cam = self.camera

        # Земля
        pts = []
        for x in range(max(0, int(cam) - 40), min(l["end"], int(cam) + W + 50), 10):
            pts.extend((x - cam, terrain_y(l, x)))
        pts.extend((W + 50, H + 60, -50, H + 60))
        self.c.create_polygon(*pts, fill=l["ground"], outline="")

        # Трава
        edge = []
        for x in range(max(0, int(cam) - 40), min(l["end"], int(cam) + W + 50), 10):
            edge.extend((x - cam, terrain_y(l, x)))
        self.c.create_line(*edge, fill=l["grass"], width=13, smooth=True)
        self.c.create_line(*edge, fill="#c8f090", width=4, smooth=True)

        # Платформы
        for px, py, pw in l["platforms"]:
            sx = px - cam
            self.draw_rect(sx, py, sx + pw, py + 20, "#8b5e3c", "#5a3a28", 2)
            self.draw_rect(sx, py, sx + pw, py + 6, "#d4a06a")

        # Коробки
        for cx in l["crates"]:
            sx = cx - cam
            gy = terrain_y(l, cx + 25)
            self.c.create_oval(sx + 5, gy - 3, sx + 55, gy + 7, fill="#2a1f18", outline="")
            self.draw_rect(sx, gy - 50, sx + 50, gy, "#c48a4a", "#6b452f", 3)
            self.c.create_line(sx + 5, gy - 45, sx + 45, gy - 5, fill="#e8c08a", width=3)
            self.c.create_line(sx + 45, gy - 45, sx + 5, gy - 5, fill="#e8c08a", width=3)

        # Шипы
        for sx, in l["spikes"]:
            x = sx - cam
            y = terrain_y(l, sx)
            self.c.create_polygon(x, y, x + 30, y - 32, x + 60, y, fill="#dce6ed", outline="#5a6e80", width=2)

        # Враги
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemies:
                continue
            x = ex - cam
            y = terrain_y(l, ex) - 18
            bounce = math.sin(self.anim_t * 5.5 + i) * 2.5
            self.c.create_oval(x - 20, y - 18 + bounce, x + 20, y + 20 + bounce, fill="#5b8f45", outline="#2d4a28", width=3)
            self.c.create_oval(x - 11, y - 8 + bounce, x - 3, y + 2 + bounce, fill="white", outline="")
            self.c.create_oval(x + 3, y - 8 + bounce, x + 11, y + 2 + bounce, fill="white", outline="")
            self.c.create_oval(x - 8, y - 5 + bounce, x - 4, y, fill="#1a2a18", outline="")
            self.c.create_oval(x + 5, y - 5 + bounce, x + 9, y, fill="#1a2a18", outline="")

        # Монеты
        for i, cx in enumerate(l["coins"]):
            if i in self.got_coins:
                continue
            x = cx - cam
            y = terrain_y(l, cx) - 85 - (10 if i % 2 else 0)
            pulse = 1.0 + math.sin(self.anim_t * 5 + i) * 0.1
            r = 12 * pulse
            self.c.create_oval(x - r, y - r, x + r, y + r, fill="#d99416", outline="#fff1a0", width=2)
            self.c.create_oval(x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55, fill="#ffdf4a", outline="")

        # Флаг
        fx = l["end"] - 80 - cam
        fy = terrain_y(l, l["end"] - 80)
        self.draw_rect(fx - 3, fy - 130, fx + 3, fy, "#4a3a2a")
        wave = math.sin(self.anim_t * 4) * 5
        self.c.create_polygon(fx, fy - 130, fx + 70 + wave, fy - 110, fx, fy - 88, fill="#ffdc58", outline="#fff3b0", width=2)

    def draw_player(self):
        x = self.x - self.camera
        y = self.y

        # Тень
        gy = terrain_y(self.level, self.x)
        self.c.create_oval(x - 20, gy - 4, x + 20, gy + 6, fill="#2a3a30", outline="")

        if self.player_img:
            self.c.create_image(x, y + PLAYER_H // 2, image=self.player_img, anchor="center")
        else:
            # Запасной персонаж
            self.c.create_oval(x - 24, y, x + 24, y + 48, fill="#ef5148", outline="#a92e35", width=3)
            self.c.create_oval(x - 12, y + 10, x - 2, y + 22, fill="white", outline="")
            self.c.create_oval(x + 2, y + 10, x + 12, y + 22, fill="white", outline="")

    def draw_hud(self):
        self.draw_rect(14, 12, 340, 78, "#0f2438", "#7ec8d8", 2)
        self.draw_text(28, 30, "ЧЕКУШКА 2D", 14, "#ffe27a", anchor="w")
        self.draw_text(28, 55, f"Монеты: {len(self.got_coins)}/{len(self.level['coins'])}", 12, "#e8f4f8", anchor="w")

        self.draw_rect(400, 20, 720, 36, "#1a3a50")
        progress = self.x / self.level["end"]
        self.draw_rect(400, 20, 400 + 320 * progress, 36, "#ffdc58")
        self.draw_text(560, 50, self.level["name"].upper(), 10, "#ffffff")

        self.draw_rect(860, 14, 1082, 56, "#0f2438", "#7ec8d8", 2)
        self.draw_text(970, 35, f"★  {self.total_coins}", 15, "#ffe27a")

    def draw_particles(self):
        for x, y, vx, vy, life, col, size in self.particles:
            sx = x - self.camera
            if -30 < sx < W + 30:
                r = max(1.5, size * life / 0.55)
                self.c.create_oval(sx - r, y - r, sx + r, y + r, fill=col, outline="")

    def draw_panel(self, title, subtitle):
        self.draw_rect(0, 0, W, H, "#0c1624")
        for x, y, r in [(80, 70, 100), (1020, 560, 170), (940, 60, 45)]:
            self.c.create_oval(x - r, y - r, x + r, y + r, fill="#152a40", outline="")
        self.draw_text(W / 2, 110, title, 38, "#ffe27a")
        self.draw_text(W / 2, 160, subtitle, 14, "#c0dce8", False)

    def draw_menu(self):
        self.draw_panel("ЧЕКУШКА 2D", "Платформер с котом")
        self.buttons = []
        self.button(W / 2, 280, 300, 54, "ИГРАТЬ", lambda: setattr(self, "screen", "levels"))
        self.button(W / 2, 360, 300, 48, "ВЫХОД", self.root.destroy)
        self.draw_text(W / 2, 480, "A / D  или  ← / →  — бег     SPACE — прыжок", 13, "#a8c8d8", False)
        self.draw_text(W / 2, 510, "P или ESC — пауза", 12, "#80a0b0", False)
        self.draw_text(W / 2, 560, f"Версия {APP_VERSION}", 11, "#5a7a90", False)

    def draw_levels(self):
        self.draw_panel("ВЫБОР УРОВНЯ", "Пройди уровень, чтобы открыть следующий")
        self.buttons = []
        for i, lvl in enumerate(LEVELS):
            col = i % 2
            row = i // 2
            x = W / 2 + (col - 0.5) * 340
            y = 250 + row * 85
            locked = i + 1 > self.unlocked
            self.button(x, y, 300, 62,
                        ("🔒  " if locked else f"{i+1:02d}  ") + lvl["name"],
                        lambda j=i: self.start_level(j),
                        "Закрыт" if locked else lvl["subtitle"],
                        locked)
        self.button(W / 2, 580, 200, 44, "НАЗАД", lambda: setattr(self, "screen", "menu"))

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
            self.draw_menu()
        elif self.screen == "levels":
            self.draw_levels()
        elif self.screen == "pause":
            self.draw_rect(0, 0, W, H, "#0c1624")
            self.draw_text(W / 2, 220, "ПАУЗА", 40, "#ffe27a")
            self.draw_text(W / 2, 280, "Нажми P или ESC, чтобы продолжить", 14, "#d0e8f0", False)
            self.buttons = []
            self.button(W / 2, 370, 230, 50, "В МЕНЮ", lambda: setattr(self, "screen", "menu"))
        elif self.screen == "dead":
            self.draw_rect(0, 0, W, H, "#0c1624")
            self.draw_text(W / 2, 220, "ОЙ!", 40, "#ff8a78")
            self.draw_text(W / 2, 280, "Попробуй ещё раз", 15, "#d0e8f0", False)
            self.buttons = []
            self.button(W / 2, 370, 240, 52, "ПОВТОРИТЬ", lambda: self.start_level(self.level_index))
            self.button(W / 2, 440, 240, 46, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))
        elif self.screen == "win":
            self.draw_rect(0, 0, W, H, "#0c1624")
            self.draw_text(W / 2, 190, "УРОВЕНЬ ПРОЙДЕН!", 36, "#ffe27a")
            self.draw_text(W / 2, 250, f"Монеты: {len(self.got_coins)}/{len(self.level['coins'])}", 16, "#ffffff", False)
            self.buttons = []
            if self.level_index < len(LEVELS) - 1:
                self.button(W / 2, 350, 280, 52, "СЛЕДУЮЩИЙ УРОВЕНЬ",
                            lambda: self.start_level(self.level_index + 1))
            self.button(W / 2, 420, 280, 46, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))

        self.c.bind("<Button-1>", self.on_click)

    def loop(self):
        now = time.perf_counter()
        dt = min(now - self.last, 0.033)
        self.last = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.loop)

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
