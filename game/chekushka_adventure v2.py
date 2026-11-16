# -*- coding: utf-8 -*-
"""ЧЕКУШКА 2D — платформер на Tkinter. Никаких pip-зависимостей."""
import tkinter as tk
from tkinter import messagebox
import math, random, time, json, os, urllib.request, urllib.error, subprocess, sys

APP_VERSION = "2.1.1"
REPO_OWNER = "Dimnost"
REPO_NAME = "voidu-s-war"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = RAW_BASE + "/version.json"
GAME_URL = RAW_BASE + "/game/chekushka_adventure%20v2.py"

W, H = 1100, 650
R = 25
GRAVITY = 1750
MAX_SPEED = 410
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chekushka_save.json")

SKINS = [
    {"name":"Классика", "body":"#ef5148", "dark":"#a92e35", "shine":"#ff9b83", "price":0},
    {"name":"Золотой", "body":"#f5bd35", "dark":"#ad7415", "shine":"#fff0a0", "price":12},
    {"name":"Космос", "body":"#7659d9", "dark":"#392a83", "shine":"#c5aaff", "price":25},
    {"name":"Мята", "body":"#40cda4", "dark":"#16785f", "shine":"#b4ffe7", "price":40},
    {"name":"Огонёк", "body":"#ff7a28", "dark":"#a83c18", "shine":"#ffd08b", "price":55},
    {"name":"Лёд", "body":"#6bc9f5", "dark":"#2878ad", "shine":"#e0f8ff", "price":70},
]

LEVELS = [
    {"name":"Зелёные холмы", "subtitle":"Разомнись и собери добычу", "sky":"#76d5ff", "far":"#9bd9a3", "hill":"#58b97a", "ground":"#805536", "grass":"#54c65c",
     "end":2600, "terrain":[(0,510),(420,510),(620,465),(900,465),(1120,510),(1450,510),(1650,455),(1940,455),(2150,505),(2600,505)],
     "platforms":[(720,390,180),(1260,405,175),(1770,365,190),(2240,390,180)],
     "crates":[980,1510,2070], "bottles":[520,810,1320,1810,2320], "coins":[330,700,1080,1190,1580,1900,2200,2470],
     "spikes":[(1100,0),(1960,0)], "enemies":[1450,2150]},
    {"name":"Пустынный забег", "subtitle":"Жарко! Не наступай на шипы", "sky":"#ffbd83", "far":"#e8bb83", "hill":"#c78b54", "ground":"#9a6037", "grass":"#e4b35b",
     "end":3000, "terrain":[(0,500),(500,500),(720,450),(1000,450),(1250,515),(1580,515),(1800,460),(2120,460),(2370,510),(2700,510),(3000,470)],
     "platforms":[(580,365,170),(1080,365,190),(1660,370,180),(2220,360,200),(2670,345,170)],
     "crates":[900,1430,2040,2530], "bottles":[370,650,1140,1720,2280,2780], "coins":[260,600,800,1190,1530,1860,2160,2450,2850],
     "spikes":[(1240,0),(2110,0),(2700,0)], "enemies":[980,1830,2580]},
    {"name":"Ледяные пещеры", "subtitle":"Скользкие дорожки и холодные ловушки", "sky":"#8cc9ef", "far":"#b4dff0", "hill":"#73b6d0", "ground":"#547b91", "grass":"#b7f2ff",
     "end":3200, "terrain":[(0,510),(430,510),(650,455),(900,455),(1130,515),(1480,515),(1700,450),(2020,450),(2260,510),(2600,510),(2820,455),(3200,455)],
     "platforms":[(700,360,180),(1200,390,180),(1740,350,190),(2300,370,180),(2800,340,190)],
     "crates":[980,1540,2110,2650], "bottles":[340,770,1260,1800,2360,2880], "coins":[250,620,890,1150,1450,1690,2010,2250,2540,2950],
     "spikes":[(1120,0),(2220,0),(2740,0)], "enemies":[890,1910,2570]},
    {"name":"Ночная долина", "subtitle":"Последний рывок к финишу!", "sky":"#202d5c", "far":"#354878", "hill":"#283d68", "ground":"#51415c", "grass":"#68b77d",
     "end":3500, "terrain":[(0,510),(480,510),(700,460),(1000,460),(1240,510),(1600,510),(1810,450),(2150,450),(2390,515),(2750,515),(2970,455),(3500,455)],
     "platforms":[(560,365,190),(1070,360,190),(1650,355,200),(2220,360,190),(2820,345,200),(3200,330,170)],
     "crates":[900,1450,2070,2650,3100], "bottles":[350,640,1120,1710,2280,2880,3290], "coins":[250,590,830,1170,1530,1870,2180,2490,2790,3020,3370],
     "spikes":[(1220,0),(2380,0),(2940,0)], "enemies":[990,1830,2700,3190]},
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
    return 500

class Game:
    def __init__(self, root):
        self.root = root
        root.title("ЧЕКУШКА 2D — приключение")
        root.resizable(False, False)
        root.configure(bg="#101d32")
        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#101d32")
        self.c.pack()
        self.keys = set()
        self.screen = "menu"
        self.last = time.perf_counter()
        self.level_index = 0
        self.skin_index = 0
        self.total_coins = 0
        self.unlocked = 1
        self.load_save()
        self.owned_skins = getattr(self, "owned_skins", {0})
        self.particles = []
        self.buttons = []
        self.anim_t = 0.0

        root.bind("<KeyPress>", self.keydown)
        root.bind("<KeyRelease>", self.keyup)
        root.bind("<Escape>", lambda e: self.pause())
        root.bind("<Return>", lambda e: self.enter())
        root.bind("<space>", lambda e: self.jump())
        root.bind("p", lambda e: self.pause())
        root.bind("P", lambda e: self.pause())
        root.bind("r", lambda e: self.start_level(self.level_index))
        self.loop()

    def load_save(self):
        try:
            d = json.load(open(SAVE_FILE, encoding="utf-8"))
            self.total_coins = int(d.get("coins", 0))
            self.unlocked = clamp(int(d.get("unlocked", 1)), 1, len(LEVELS))
            self.skin_index = clamp(int(d.get("skin", 0)), 0, len(SKINS) - 1)
            self.owned_skins = set(d.get("owned_skins", [0]))
        except Exception:
            self.owned_skins = {0}

    def save(self):
        try:
            json.dump({
                "coins": self.total_coins,
                "unlocked": self.unlocked,
                "skin": self.skin_index,
                "owned_skins": sorted(getattr(self, "owned_skins", {0}))
            }, open(SAVE_FILE, "w", encoding="utf-8"))
        except Exception:
            pass

    def keydown(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        if k in ("space", "w", "up"):
            self.jump()
        if k == "escape":
            self.pause()

    def keyup(self, e):
        self.keys.discard(e.keysym.lower())

    def enter(self):
        if self.screen == "menu":
            self.screen = "levels"
        elif self.screen == "levels":
            self.start_level(self.level_index)
        elif self.screen == "skins":
            self.screen = "menu"
        elif self.screen in ("win", "dead"):
            self.start_level(self.level_index)
        elif self.screen == "pause":
            self.screen = "play"

    def jump(self):
        if self.screen == "play" and self.on_ground:
            self.vy = -720
            self.on_ground = False
            self.burst(self.x, self.y + R, "#e9ffff", 8)

    def pause(self):
        if self.screen == "play":
            self.screen = "pause"
        elif self.screen == "pause":
            self.screen = "play"

    def start_level(self, i):
        self.level_index = clamp(i, 0, len(LEVELS) - 1)
        self.level = LEVELS[self.level_index]
        self.x = 90.0
        self.y = terrain_y(self.level, self.x) - R
        self.vx = self.vy = 0.0
        self.on_ground = True
        self.camera = 0.0
        self.got_b = set()
        self.got_c = set()
        self.dead_enemy = set()
        self.particles = []
        self.screen = "play"

    def burst(self, x, y, color, n=10):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(70, 240)
            self.particles.append([x, y, math.cos(a) * s, math.sin(a) * s, 0.6, color, random.uniform(2.5, 5.5)])

    def update(self, dt):
        self.anim_t += dt
        if self.screen != "play":
            return

        l = self.level
        left = ("a" in self.keys or "left" in self.keys)
        right = ("d" in self.keys or "right" in self.keys)
        d = int(right) - int(left)

        if d:
            self.vx += d * 1750 * dt
        else:
            self.vx *= max(0.0, 1.0 - 6.0 * dt)

        self.vx = clamp(self.vx, -MAX_SPEED, MAX_SPEED)

        oldy = self.y
        self.x = clamp(self.x + self.vx * dt, R, l["end"] - R)
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        self.on_ground = False

        # Земля
        gy = terrain_y(l, self.x) - R
        if self.y >= gy and self.vy >= 0:
            self.y = gy
            self.vy = 0
            self.on_ground = True

        # Платформы
        for px, py, pw in l["platforms"]:
            if (px - R < self.x < px + pw + R and
                oldy + R <= py + 10 and
                self.y + R >= py and
                self.vy >= 0):
                self.y = py - R
                self.vy = 0
                self.on_ground = True

        # === ИСПРАВЛЕННЫЕ КОРОБКИ ===
        for cx in l["crates"]:
            crate_w = 48
            crate_h = 50
            crate_x = cx + crate_w / 2
            base = terrain_y(l, cx + 22)
            top = base - crate_h

            # Горизонтальное пересечение
            if abs(self.x - crate_x) < R + crate_w / 2 + 2:
                # Стоим сверху
                if (oldy + R <= top + 14 and
                    self.y + R >= top and
                    self.vy >= 0):
                    self.y = top - R
                    self.vy = 0
                    self.on_ground = True
                # Упираемся сбоку
                elif self.y + R > top + 8 and self.y < base:
                    if self.x < crate_x:
                        self.x = crate_x - (crate_w / 2 + R)
                        if self.vx > 0:
                            self.vx = 0
                    else:
                        self.x = crate_x + (crate_w / 2 + R)
                        if self.vx < 0:
                            self.vx = 0

        # Шипы
        for sx, _ in l["spikes"]:
            sy = terrain_y(l, sx)
            if abs(self.x - (sx + 30)) < R + 24 and self.y + R > sy - 28 and self.y < sy + 5:
                self.screen = "dead"

        # Враги
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemy:
                continue
            ey = terrain_y(l, ex) - 18
            if abs(self.x - ex) < R + 18 and abs(self.y - ey) < R + 18:
                if self.vy > 80 and oldy + R < ey + 8:
                    self.dead_enemy.add(i)
                    self.vy = -480
                    self.burst(ex, ey, "#b8f4a5", 14)
                else:
                    self.screen = "dead"

        # Бутылки
        for i, bx in enumerate(l["bottles"]):
            by = terrain_y(l, bx) - 56
            if i not in self.got_b and math.hypot(self.x - bx, self.y - by) < 48:
                self.got_b.add(i)
                self.burst(bx, by, "#ffdf8c", 16)

        # Монеты
        for i, cx in enumerate(l["coins"]):
            cy = terrain_y(l, cx) - 90 - (12 if i % 2 else 0)
            if i not in self.got_c and math.hypot(self.x - cx, self.y - cy) < 44:
                self.got_c.add(i)
                self.total_coins += 1
                self.burst(cx, cy, "#ffdf48", 14)
                self.save()

        if self.y > H + 160:
            self.screen = "dead"

        if self.x > l["end"] - 90:
            self.screen = "win"
            self.unlocked = max(self.unlocked, min(len(LEVELS), self.level_index + 2))
            self.save()

        self.camera = clamp(self.x - W * 0.36, 0, l["end"] - W)

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

    def txt(self, x, y, s, size, color, bold=True, **kw):
        self.c.create_text(x, y, text=s, fill=color,
                           font=("Segoe UI", size, "bold" if bold else "normal"), **kw)

    def button(self, x, y, w, h, label, cmd, sub=None, disabled=False):
        fill = "#1e334d" if disabled else "#2a5570"
        outline = "#5a7a94" if disabled else "#8bd8e8"
        self.c.create_rectangle(x - w/2, y - h/2, x + w/2, y + h/2,
                                fill=fill, outline=outline, width=2)
        # Лёгкий блик сверху
        if not disabled:
            self.c.create_rectangle(x - w/2 + 2, y - h/2 + 2, x + w/2 - 2, y - h/2 + 8,
                                    fill="#3a6a88", outline="")
        self.txt(x, y - 4 if sub else y, label, 16, "#8aa0b4" if disabled else "#ffffff")
        if sub:
            self.txt(x, y + 16, sub, 10, "#b8d0dc", False)
        self.buttons.append((x - w/2, y - h/2, x + w/2, y + h/2, cmd, disabled))

    def click(self, e):
        for x1, y1, x2, y2, cmd, dis in reversed(self.buttons):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2 and not dis:
                cmd()
                return

    def sky(self):
        l = self.level if hasattr(self, "level") else LEVELS[0]
        self.c.configure(bg=l["sky"])

        # Облака
        for x, y, scale in [(140, 95, 1.0), (490, 150, 0.85), (880, 90, 1.1),
                            (1200, 130, 0.9), (1850, 85, 1.0), (2500, 130, 0.95), (3200, 90, 1.05)]:
            sx = (x - self.camera * 0.18) % (W + 200) - 100
            s = 70 * scale
            self.c.create_oval(sx, y, sx + s, y + s * 0.45, fill="#f7fdff", outline="")
            self.c.create_oval(sx + s*0.35, y - s*0.25, sx + s*1.15, y + s*0.45, fill="#f7fdff", outline="")
            self.c.create_oval(sx + s*0.75, y, sx + s*1.55, y + s*0.45, fill="#f7fdff", outline="")

        # Дальние холмы
        for i in range(-1, 9):
            x = i * 280 - (self.camera * 0.35) % 280
            self.c.create_oval(x, 320, x + 380, 580, fill=l["far"], outline="")
            self.c.create_oval(x + 100, 360, x + 460, 590, fill=l["hill"], outline="")

        # Солнце / луна
        if "Ночная" in l["name"]:
            self.c.create_oval(840, 55, 915, 130, fill="#e8f0ff", outline="")
            self.c.create_oval(855, 70, 900, 115, fill="#d0e0f8", outline="")
        else:
            self.c.create_oval(840, 55, 915, 130, fill="#fff0a0", outline="")
            self.c.create_oval(855, 70, 900, 115, fill="#ffe070", outline="")

    def world(self):
        l = self.level
        cam = self.camera

        # Земля
        points = []
        for x in range(max(0, int(cam) - 30), min(l["end"], int(cam) + W + 40), 8):
            points.extend((x - cam, terrain_y(l, x)))
        points.extend((W + 40, H + 50, -40, H + 50))
        self.c.create_polygon(*points, fill=l["ground"], outline="")

        # Трава
        edge = []
        for x in range(max(0, int(cam) - 30), min(l["end"], int(cam) + W + 40), 8):
            edge.extend((x - cam, terrain_y(l, x)))
        self.c.create_line(*edge, fill=l["grass"], width=14, smooth=True)
        self.c.create_line(*edge, fill="#c4f28b", width=4, smooth=True)

        # Платформы
        for px, py, pw in l["platforms"]:
            sx = px - cam
            self.rect(sx, py, sx + pw, py + 22, "#8b5e3c", "#5a3a28", 2)
            self.rect(sx, py, sx + pw, py + 7, "#d4a06a")
            for xx in range(int(sx + 14), int(sx + pw - 10), 28):
                self.rect(xx, py + 9, xx + 16, py + 17, "#a87045")

        # Коробки (красивее)
        for cx in l["crates"]:
            sx = cx - cam
            gy = terrain_y(l, cx + 22)
            # Тень
            self.c.create_oval(sx + 4, gy - 4, sx + 52, gy + 6, fill="#2a1f18", outline="")
            # Корпус
            self.rect(sx, gy - 50, sx + 48, gy, "#c48a4a", "#6b452f", 3)
            # Доски
            self.c.create_line(sx + 4, gy - 45, sx + 44, gy - 5, fill="#e8c08a", width=3)
            self.c.create_line(sx + 44, gy - 45, sx + 4, gy - 5, fill="#e8c08a", width=3)
            # Блик
            self.rect(sx + 3, gy - 47, sx + 12, gy - 40, "#f0d0a0")

        # Шипы
        for sx, _ in l["spikes"]:
            x = sx - cam
            y = terrain_y(l, sx)
            self.c.create_polygon(x, y, x + 30, y - 34, x + 60, y,
                                  fill="#dce6ed", outline="#5a6e80", width=2)
            self.c.create_line(x + 30, y - 28, x + 30, y - 4, fill="#ffffff", width=3)

        # Враги
        for i, ex in enumerate(l["enemies"]):
            if i in self.dead_enemy:
                continue
            x = ex - cam
            y = terrain_y(l, ex) - 17
            bounce = math.sin(self.anim_t * 6 + i) * 2
            self.c.create_oval(x - 19, y - 18 + bounce, x + 19, y + 19 + bounce,
                               fill="#5b8f45", outline="#2d4a28", width=3)
            self.c.create_oval(x - 11, y - 8 + bounce, x - 3, y + 2 + bounce, fill="white", outline="")
            self.c.create_oval(x + 3, y - 8 + bounce, x + 11, y + 2 + bounce, fill="white", outline="")
            self.c.create_oval(x - 8, y - 5 + bounce, x - 4, y + 1 + bounce, fill="#1a2a18", outline="")
            self.c.create_oval(x + 5, y - 5 + bounce, x + 9, y + 1 + bounce, fill="#1a2a18", outline="")

        # Бутылки
        for i, bx in enumerate(l["bottles"]):
            if i in self.got_b:
                continue
            x = bx - cam
            y = terrain_y(l, bx) - 58
            self.c.create_oval(x - 15, y + 46, x + 15, y + 54, fill="#2a4a3a", outline="")
            self.rect(x - 10, y + 12, x + 10, y + 48, "#d0f0ea", "#ffffff", 2)
            self.rect(x - 6, y + 2, x + 6, y + 16, "#b8e0e0", "#ffffff")
            self.rect(x - 6, y - 3, x + 6, y + 4, "#d04555")
            self.rect(x - 7, y + 24, x + 7, y + 36, "#e85a5a")
            self.c.create_line(x - 5, y + 16, x - 5, y + 44, fill="#ffffff", width=2)

        # Монеты
        for i, cx in enumerate(l["coins"]):
            if i in self.got_c:
                continue
            x = cx - cam
            y = terrain_y(l, cx) - 90 - (12 if i % 2 else 0)
            pulse = 1.0 + math.sin(self.anim_t * 5 + i) * 0.08
            r = 13 * pulse
            self.c.create_oval(x - r, y - r, x + r, y + r, fill="#d99416", outline="#fff1a0", width=2)
            self.c.create_oval(x - r*0.6, y - r*0.6, x + r*0.6, y + r*0.6, fill="#ffdf4a", outline="")

        # Флаг финиша
        fx = l["end"] - 75 - cam
        fy = terrain_y(l, l["end"] - 75)
        self.rect(fx - 3, fy - 130, fx + 3, fy, "#4a3a2a")
        wave = math.sin(self.anim_t * 4) * 4
        self.c.create_polygon(fx, fy - 130, fx + 68 + wave, fy - 112, fx, fy - 90,
                              fill="#ffdc58", outline="#fff3b0", width=2)

    def player(self):
        x = self.x - self.camera
        y = self.y
        s = SKINS[self.skin_index]

        # Тень под персонажем
        shadow_y = terrain_y(self.level, self.x)
        self.c.create_oval(x - 22, shadow_y - 5, x + 22, shadow_y + 6, fill="#2a3a30", outline="")

        # Тело
        self.c.create_oval(x - R + 3, y - R + 6, x + R + 3, y + R + 6, fill=s["dark"], outline="")
        self.c.create_oval(x - R, y - R, x + R, y + R, fill=s["body"], outline=s["dark"], width=3)

        # Блик
        self.c.create_oval(x - 15, y - 17, x - 2, y - 7, fill=s["shine"], outline="")

        # Глаза
        self.c.create_oval(x - 13, y - 9, x - 3, y + 4, fill="white", outline="")
        self.c.create_oval(x + 3, y - 9, x + 13, y + 4, fill="white", outline="")
        self.c.create_oval(x - 9, y - 4, x - 5, y + 2, fill="#222333", outline="")
        self.c.create_oval(x + 7, y - 4, x + 11, y + 2, fill="#222333", outline="")

        # Улыбка
        self.c.create_arc(x - 9, y + 2, x + 10, y + 16, start=200, extent=140,
                          style=tk.ARC, outline=s["dark"], width=2)

    def hud(self):
        # Фон
        self.rect(14, 12, 370, 88, "#0f2438", "#7ec8d8", 2)
        self.txt(30, 32, "ЧЕКУШКА 2D", 15, "#ffe27a", anchor="w")
        self.txt(30, 62, f"Бутылки {len(self.got_b)}/{len(self.level['bottles'])}   ·   Монеты {len(self.got_c)}/{len(self.level['coins'])}",
                 12, "#e8f4f8", anchor="w")

        # Прогресс
        self.rect(410, 22, 700, 38, "#1a3a50")
        progress = self.x / self.level["end"]
        self.rect(410, 22, 410 + 290 * progress, 38, "#ffdc58")
        self.txt(555, 52, self.level["name"].upper(), 10, "#ffffff")

        # Монеты
        self.rect(860, 14, 1082, 58, "#0f2438", "#7ec8d8", 2)
        self.txt(970, 36, f"★  {self.total_coins}", 16, "#ffe27a")

    def particles_draw(self):
        for x, y, vx, vy, life, col, size in self.particles:
            sx = x - self.camera
            if -20 < sx < W + 20:
                rr = max(1.5, size * life / 0.6)
                self.c.create_oval(sx - rr, y - rr, sx + rr, y + rr, fill=col, outline="")

    def panel(self, title, sub):
        self.rect(0, 0, W, H, "#0d1a2c")
        # Декоративные круги
        for x, y, r, col in [(90, 80, 110, "#152a42"), (1020, 560, 180, "#152a42"),
                             (950, 70, 50, "#1a3550")]:
            self.c.create_oval(x - r, y - r, x + r, y + r, fill=col, outline="")
        self.txt(W/2, 115, title, 40, "#ffe27a")
        self.txt(W/2, 168, sub, 14, "#c8e0ec", False)

    def check_updates(self):
        try:
            req = urllib.request.Request(VERSION_URL, headers={"User-Agent": "ChekushkaAdventure"})
            with urllib.request.urlopen(req, timeout=12) as response:
                remote = json.loads(response.read().decode("utf-8"))
            latest = str(remote.get("version", ""))
            if not latest:
                raise ValueError("В version.json не указана версия")
            if latest == APP_VERSION:
                messagebox.showinfo("Обновления", f"У тебя последняя версия: {APP_VERSION}")
                return
            if not messagebox.askyesno("Доступно обновление",
                                       f"Установлена версия {APP_VERSION}.\nНовая версия: {latest}.\nСкачать и установить?"):
                return
            self.download_update()
        except Exception as e:
            messagebox.showerror("Ошибка обновления",
                                 "Не удалось проверить обновления.\nПроверь интернет и GitHub.\n\n" + str(e))

    def download_update(self):
        try:
            req = urllib.request.Request(GAME_URL, headers={"User-Agent": "ChekushkaAdventure"})
            with urllib.request.urlopen(req, timeout=30) as response:
                new_code = response.read()
            if len(new_code) < 1000:
                raise ValueError("Файл обновления пустой или повреждён")
            folder = os.path.dirname(os.path.abspath(__file__))
            temp_file = os.path.join(folder, "chekushka_adventure.new.py")
            with open(temp_file, "wb") as f:
                f.write(new_code)

            current = os.path.basename(__file__)
            bat_file = os.path.join(folder, "apply_update.bat")
            with open(bat_file, "w", encoding="utf-8") as f:
                f.write("@echo off\r\n")
                f.write("chcp 65001 >nul\r\n")
                f.write("timeout /t 2 /nobreak >nul\r\n")
                f.write(f'copy /Y "chekushka_adventure.new.py" "{current}" >nul\r\n')
                f.write(f'"{sys.executable}" "{current}"\r\n')
                f.write('del "%~f0"\r\n')

            messagebox.showinfo("Обновление", "Обновление скачано. Игра перезапустится.")
            subprocess.Popen(["cmd", "/c", bat_file], cwd=folder,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", "Не удалось установить обновление.\n\n" + str(e))

    def draw_menu(self):
        self.panel("ЧЕКУШКА 2D", "Маленький герой. Большое приключение.")
        self.buttons = []
        self.button(W/2, 275, 310, 56, "ИГРАТЬ", lambda: setattr(self, "screen", "levels"))
        self.button(W/2, 350, 310, 56, "ВЫБРАТЬ СКИН",
                    lambda: setattr(self, "screen", "skins"),
                    f"Монет: {self.total_coins}")
        self.button(W/2, 425, 310, 48, "ПРОВЕРИТЬ ОБНОВЛЕНИЯ", self.check_updates)
        self.txt(W/2, 510, "A / D  или  ← / →  — движение     SPACE — прыжок", 13, "#b8d0dc", False)
        self.txt(W/2, 535, "Собирай монеты, обходи шипы и побеждай слизней!", 12, "#8aa8b8", False)
        self.txt(W/2, 570, f"Версия {APP_VERSION}", 11, "#5a7a90", False)

    def draw_levels(self):
        self.panel("ВЫБОР УРОВНЯ", "Пройди уровень, чтобы открыть следующий")
        self.buttons = []
        for i, l in enumerate(LEVELS):
            col = i % 2
            row = i // 2
            x = W/2 + (col - 0.5) * 320
            y = 260 + row * 100
            locked = i + 1 > self.unlocked
            self.button(x, y, 280, 70,
                        ("🔒  " if locked else f"{i+1:02d}  ") + l["name"],
                        lambda j=i: self.start_level(j),
                        "Закрыт" if locked else l["subtitle"],
                        locked)
        self.button(W/2, 545, 220, 46, "НАЗАД", lambda: setattr(self, "screen", "menu"))

    def draw_skins(self):
        self.panel("ВЫБОР СКИНА", f"Твои монеты: {self.total_coins}")
        self.buttons = []
        if not hasattr(self, "owned_skins"):
            self.owned_skins = {0}

        for i, s in enumerate(SKINS):
            col = i % 3
            row = i // 3
            x = 250 + col * 300
            y = 270 + row * 140

            # Превью скина
            self.c.create_oval(x - 32, y - 38, x + 32, y + 26, fill=s["body"], outline=s["shine"], width=3)
            self.c.create_oval(x - 15, y - 18, x - 5, y - 5, fill="white", outline="")
            self.c.create_oval(x + 5, y - 18, x + 15, y - 5, fill="white", outline="")

            owned = (i in self.owned_skins) or (s["price"] == 0)
            if i in self.owned_skins:
                owned = True

            if i == self.skin_index:
                label = "ВЫБРАН"
            elif owned:
                label = "ВЫБРАТЬ"
            else:
                label = f"КУПИТЬ • {s['price']} ★"

            def choose(j=i):
                ss = SKINS[j]
                if j not in self.owned_skins:
                    if self.total_coins < ss["price"]:
                        return
                    self.total_coins -= ss["price"]
                    self.owned_skins.add(j)
                    self.save()
                self.skin_index = j
                self.save()

            can_buy = owned or self.total_coins >= s["price"]
            self.button(x, y + 50, 190, 40, label, choose, s["name"], not can_buy)

        self.button(W/2, 545, 220, 46, "НАЗАД", lambda: setattr(self, "screen", "menu"))

    def draw(self):
        self.c.delete("all")
        self.buttons = []

        if self.screen in ("play", "pause", "win", "dead"):
            self.sky()
            self.world()
            self.particles_draw()
            self.player()
            self.hud()

        if self.screen == "menu":
            self.draw_menu()
        elif self.screen == "levels":
            self.draw_levels()
        elif self.screen == "skins":
            self.draw_skins()
        elif self.screen == "pause":
            self.rect(0, 0, W, H, "#0d1a2c")
            self.txt(W/2, 220, "ПАУЗА", 42, "#ffe27a")
            self.txt(W/2, 285, "Нажми P или ESC, чтобы продолжить", 15, "#d0e8f0", False)
            self.buttons = []
            self.button(W/2, 370, 240, 52, "В МЕНЮ", lambda: setattr(self, "screen", "menu"))
        elif self.screen == "dead":
            self.rect(0, 0, W, H, "#0d1a2c")
            self.txt(W/2, 220, "ОЙ! ПОПАЛСЯ!", 40, "#ff8a78")
            self.txt(W/2, 285, "Попробуй ещё раз — у тебя получится", 15, "#d0e8f0", False)
            self.buttons = []
            self.button(W/2, 370, 250, 54, "ПОВТОРИТЬ", lambda: self.start_level(self.level_index))
            self.button(W/2, 445, 250, 48, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))
        elif self.screen == "win":
            self.rect(0, 0, W, H, "#0d1a2c")
            self.txt(W/2, 195, "УРОВЕНЬ ПРОЙДЕН!", 40, "#ffe27a")
            self.txt(W/2, 265,
                     f"Бутылки: {len(self.got_b)}/{len(self.level['bottles'])}    Монеты: {len(self.got_c)}/{len(self.level['coins'])}",
                     16, "#ffffff", False)
            self.buttons = []
            if self.level_index < len(LEVELS) - 1:
                self.button(W/2, 360, 280, 54, "СЛЕДУЮЩИЙ УРОВЕНЬ",
                            lambda: self.start_level(self.level_index + 1))
            self.button(W/2, 435, 280, 48, "К УРОВНЯМ", lambda: setattr(self, "screen", "levels"))

        self.c.bind("<Button-1>", self.click)

    def loop(self):
        now = time.perf_counter()
        dt = min(now - self.last, 0.035)
        self.last = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
