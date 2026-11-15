# -*- coding: utf-8 -*-
"""ЧЕКУШКА 2D — платформер на Tkinter. Никаких pip-зависимостей."""
import tkinter as tk
from tkinter import messagebox
import math, random, time, json, os, urllib.request, urllib.error, subprocess, tempfile, sys

APP_VERSION = "2.1.0"
REPO_OWNER = "YOUR_GITHUB_USERNAME"
REPO_NAME = "YOUR_REPO"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = RAW_BASE + "/version.json"
GAME_URL = RAW_BASE + "/game/chekushka_adventure.py"


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

def clamp(v,a,b): return max(a,min(b,v))
def terrain_y(level,x):
    arr=level["terrain"]; x=clamp(x,0,level["end"])
    for (x1,y1),(x2,y2) in zip(arr,arr[1:]):
        if x1<=x<=x2:
            t=(x-x1)/(x2-x1); t=t*t*(3-2*t)
            return y1+(y2-y1)*t
    return 500

class Game:
    def __init__(self,root):
        self.root=root; root.title("ЧЕКУШКА 2D — приключение"); root.resizable(False,False)
        root.configure(bg="#101d32")
        self.c=tk.Canvas(root,width=W,height=H,highlightthickness=0); self.c.pack()
        self.keys=set(); self.screen="menu"; self.last=time.perf_counter()
        self.level_index=0; self.skin_index=0; self.total_coins=0; self.unlocked=1
        self.load_save(); self.owned_skins=getattr(self,"owned_skins",{0}); self.particles=[]; self.buttons=[]
        root.bind("<KeyPress>",self.keydown); root.bind("<KeyRelease>",self.keyup)
        root.bind("<Escape>",lambda e:self.pause())
        root.bind("<Return>",lambda e:self.enter())
        root.bind("<space>",lambda e:self.jump())
        root.bind("p",lambda e:self.pause()); root.bind("P",lambda e:self.pause())
        root.bind("r",lambda e:self.start_level(self.level_index))
        self.loop()

    def load_save(self):
        try:
            d=json.load(open(SAVE_FILE,encoding="utf-8"))
            self.total_coins=int(d.get("coins",0)); self.unlocked=clamp(int(d.get("unlocked",1)),1,len(LEVELS))
            self.skin_index=clamp(int(d.get("skin",0)),0,len(SKINS)-1)
            self.owned_skins=set(d.get("owned_skins",[0]))
        except Exception:
            self.owned_skins={0}
    def save(self):
        try:
            json.dump({"coins":self.total_coins,"unlocked":self.unlocked,"skin":self.skin_index,
                       "owned_skins":sorted(getattr(self,"owned_skins",{0}))},open(SAVE_FILE,"w",encoding="utf-8"))
        except Exception: pass
    def keydown(self,e):
        k=e.keysym.lower(); self.keys.add(k)
        if k in ("space","w","up"): self.jump()
        if k=="escape": self.pause()
    def keyup(self,e): self.keys.discard(e.keysym.lower())
    def enter(self):
        if self.screen=="menu": self.screen="levels"
        elif self.screen=="levels": self.start_level(self.level_index)
        elif self.screen=="skins": self.screen="menu"
        elif self.screen in ("win","dead"): self.start_level(self.level_index)
        elif self.screen=="pause": self.screen="play"
    def jump(self):
        if self.screen=="play" and self.on_ground:
            self.vy=-720; self.on_ground=False; self.burst(self.x,self.y+R,"#e9ffff",7)
    def pause(self):
        if self.screen=="play": self.screen="pause"
        elif self.screen=="pause": self.screen="play"
    def start_level(self,i):
        self.level_index=clamp(i,0,len(LEVELS)-1); self.level=LEVELS[self.level_index]
        self.x=90.; self.y=terrain_y(self.level,self.x)-R; self.vx=self.vy=0; self.on_ground=True
        self.camera=0; self.got_b=set(); self.got_c=set(); self.dead_enemy=set()
        self.particles=[]; self.screen="play"
    def burst(self,x,y,color,n=10):
        for _ in range(n):
            a=random.random()*math.tau; s=random.uniform(60,220)
            self.particles.append([x,y,math.cos(a)*s,math.sin(a)*s,.55,color])
    def update(self,dt):
        if self.screen!="play": return
        l=self.level; left=("a" in self.keys or "left" in self.keys); right=("d" in self.keys or "right" in self.keys)
        d=int(right)-int(left)
        if d: self.vx+=d*1700*dt
        else: self.vx*=max(0,1-5.5*dt)
        self.vx=clamp(self.vx,-MAX_SPEED,MAX_SPEED)
        oldy=self.y; self.x=clamp(self.x+self.vx*dt,R,l["end"]-R); self.vy+=GRAVITY*dt; self.y+=self.vy*dt
        self.on_ground=False
        gy=terrain_y(l,self.x)-R
        if self.y>=gy and self.vy>=0: self.y=gy; self.vy=0; self.on_ground=True
        for px,py,pw in l["platforms"]:
            if px-R<self.x<px+pw+R and oldy+R<=py+12 and self.y+R>=py and self.vy>=0:
                self.y=py-R; self.vy=0; self.on_ground=True
        for cx in l["crates"]:
            base=terrain_y(l,cx+22); top=base-50
            if abs(self.x-(cx+24))<R+22 and self.y+R>top+3 and self.y<base:
                if oldy+R<=top+12 and self.vy>=0: self.y=top-R; self.vy=0; self.on_ground=True
                elif self.x<cx+24: self.x=cx-R; self.vx=0
                else: self.x=cx+48+R; self.vx=0
        # Шипы
        for sx,_ in l["spikes"]:
            sy=terrain_y(l,sx)
            if abs(self.x-(sx+30))<R+25 and self.y+R>sy-28 and self.y<sy+5: self.screen="dead"
        # Враги-патрульные
        for i,ex in enumerate(l["enemies"]):
            if i in self.dead_enemy: continue
            ey=terrain_y(l,ex)-18
            if abs(self.x-ex)<R+18 and abs(self.y-ey)<R+18:
                if self.vy>100 and oldy+R<ey+5:
                    self.dead_enemy.add(i); self.vy=-450; self.burst(ex,ey,"#b8f4a5",12)
                else: self.screen="dead"
        for i,bx in enumerate(l["bottles"]):
            by=terrain_y(l,bx)-56
            if i not in self.got_b and math.hypot(self.x-bx,self.y-by)<47:
                self.got_b.add(i); self.burst(bx,by,"#ffdf8c",14)
        for i,cx in enumerate(l["coins"]):
            cy=terrain_y(l,cx)-90-(12 if i%2 else 0)
            if i not in self.got_c and math.hypot(self.x-cx,self.y-cy)<43:
                self.got_c.add(i); self.total_coins+=1; self.burst(cx,cy,"#ffdf48",12); self.save()
        if self.y>H+150: self.screen="dead"
        if self.x>l["end"]-90:
            self.screen="win"; self.unlocked=max(self.unlocked,min(len(LEVELS),self.level_index+2)); self.save()
        self.camera=clamp(self.x-W*.36,0,l["end"]-W)
        for p in self.particles[:]:
            p[0]+=p[2]*dt; p[1]+=p[3]*dt; p[3]+=430*dt; p[4]-=dt
            if p[4]<=0: self.particles.remove(p)

    def rect(self,x1,y1,x2,y2,fill,outline="",width=1):
        self.c.create_rectangle(x1,y1,x2,y2,fill=fill,outline=outline,width=width)
    def txt(self,x,y,s,size,color,bold=True,**kw):
        self.c.create_text(x,y,text=s,fill=color,font=("Segoe UI",size,"bold" if bold else "normal"),**kw)
    def button(self,x,y,w,h,label,cmd,sub=None,disabled=False):
        fill="#263e5d" if disabled else "#254f69"
        self.c.create_rectangle(x-w/2,y-h/2,x+w/2,y+h/2,fill=fill,outline="#8bd8e8",width=2)
        self.txt(x,y-4 if sub else y,label,17,"#8196a9" if disabled else "#ffffff")
        if sub:self.txt(x,y+17,sub,10,"#c3dce5",False)
        self.buttons.append((x-w/2,y-h/2,x+w/2,y+h/2,cmd,disabled))
    def click(self,e):
        for x1,y1,x2,y2,cmd,dis in reversed(self.buttons):
            if x1<=e.x<=x2 and y1<=e.y<=y2 and not dis: cmd(); return
    def sky(self):
        l=self.level if hasattr(self,"level") else LEVELS[0]
        self.c.configure(bg=l["sky"])
        for x,y in [(140,95),(490,150),(880,90),(1200,130),(1850,85),(2500,130),(3200,90)]:
            sx=(x-self.camera*.2)%(W+180)-80
            self.c.create_oval(sx,y,sx+75,y+35,fill="#f7fdff",outline="")
            self.c.create_oval(sx+25,y-20,sx+88,y+35,fill="#f7fdff",outline="")
            self.c.create_oval(sx+60,y,sx+120,y+35,fill="#f7fdff",outline="")
        for i in range(-1,8):
            x=i*270-(self.camera*.4)%270
            self.c.create_oval(x,330,x+360,560,fill=l["far"],outline="")
            self.c.create_oval(x+90,365,x+440,570,fill=l["hill"],outline="")
        self.c.create_oval(840,55,915,130,fill="#fff0a0",outline="")
    def world(self):
        l=self.level; cam=self.camera
        points=[]
        for x in range(max(0,int(cam)-20),min(l["end"],int(cam)+W+30),10): points.extend((x-cam,terrain_y(l,x)))
        points.extend((W+30,H+40,-30,H+40))
        self.c.create_polygon(*points,fill=l["ground"],outline="")
        edge=[]
        for x in range(max(0,int(cam)-20),min(l["end"],int(cam)+W+30),10): edge.extend((x-cam,terrain_y(l,x)))
        self.c.create_line(*edge,fill=l["grass"],width=12,smooth=True)
        self.c.create_line(*edge,fill="#c4f28b",width=3,smooth=True)
        for px,py,pw in l["platforms"]:
            sx=px-cam; self.rect(sx,py,sx+pw,py+20,"#95633f","#583d30",2)
            self.rect(sx,py,sx+pw,py+6,"#e6b06a")
            for xx in range(int(sx+12),int(sx+pw-8),30): self.rect(xx,py+8,xx+18,py+16,"#b47a4b")
        for cx in l["crates"]:
            sx=cx-cam; gy=terrain_y(l,cx+22)
            self.rect(sx,gy-50,sx+48,gy,"#b77b43","#68452f",3)
            self.c.create_line(sx+5,gy-45,sx+43,gy-5,fill="#e7b77d",width=4)
            self.c.create_line(sx+43,gy-45,sx+5,gy-5,fill="#e7b77d",width=4)
        for sx,_ in l["spikes"]:
            x=sx-cam; y=terrain_y(l,sx)
            self.c.create_polygon(x,y,x+30,y-32,x+60,y,fill="#dce6ed",outline="#65788b",width=2)
            self.c.create_line(x+30,y-25,x+30,y-3,fill="#ffffff",width=3)
        for i,ex in enumerate(l["enemies"]):
            if i in self.dead_enemy: continue
            x=ex-cam; y=terrain_y(l,ex)-17
            self.c.create_oval(x-18,y-17,x+18,y+18,fill="#5b8f45",outline="#31572e",width=3)
            self.c.create_oval(x-10,y-7,x-3,y+2,fill="white",outline="")
            self.c.create_oval(x+3,y-7,x+10,y+2,fill="white",outline="")
            self.c.create_oval(x-7,y-4,x-4,y,fill="#17251c",outline="")
            self.c.create_oval(x+5,y-4,x+8,y,fill="#17251c",outline="")
        for i,bx in enumerate(l["bottles"]):
            if i in self.got_b: continue
            x=bx-cam; y=terrain_y(l,bx)-58
            self.c.create_oval(x-16,y+48,x+16,y+54,fill="#355b4a",outline="")
            self.rect(x-10,y+12,x+10,y+48,"#d9f3ee","#ffffff",2)
            self.rect(x-6,y+2,x+6,y+17,"#c3e8e8","#ffffff")
            self.rect(x-6,y-2,x+6,y+5,"#c84d58")
            self.rect(x-7,y+25,x+7,y+37,"#e45c5c")
            self.c.create_line(x-5,y+17,x-5,y+43,fill="#ffffff",width=2)
        for i,cx in enumerate(l["coins"]):
            if i in self.got_c: continue
            x=cx-cam; y=terrain_y(l,cx)-90-(12 if i%2 else 0)
            self.c.create_oval(x-13,y-13,x+13,y+13,fill="#d99416",outline="#fff1a0",width=2)
            self.c.create_oval(x-8,y-8,x+8,y+8,fill="#ffdf4a",outline="")
        fx=l["end"]-75-cam; fy=terrain_y(l,l["end"]-75)
        self.rect(fx-3,fy-125,fx+3,fy,"#554332")
        self.c.create_polygon(fx,fy-125,fx+70,fy-108,fx,fy-88,fill="#ffdc58",outline="#fff3b0")
    def player(self):
        x=self.x-self.camera; y=self.y; s=SKINS[self.skin_index]
        self.c.create_oval(x-30,terrain_y(self.level,self.x)-6,x+30,terrain_y(self.level,self.x)+5,fill="#3b5848",outline="")
        self.c.create_oval(x-R+3,y-R+5,x+R+3,y+R+5,fill=s["dark"],outline="")
        self.c.create_oval(x-R,y-R,x+R,y+R,fill=s["body"],outline=s["dark"],width=3)
        self.c.create_oval(x-16,y-18,x-3,y-8,fill=s["shine"],outline="")
        self.c.create_oval(x-13,y-9,x-3,y+5,fill="white",outline="")
        self.c.create_oval(x+3,y-9,x+13,y+5,fill="white",outline="")
        self.c.create_oval(x-9,y-4,x-5,y+2,fill="#222333",outline="")
        self.c.create_oval(x+7,y-4,x+11,y+2,fill="#222333",outline="")
        self.c.create_arc(x-9,y+1,x+10,y+17,start=205,extent=130,style=tk.ARC,outline=s["dark"],width=2)
    def hud(self):
        self.rect(16,14,360,90,"#142c43","#b7eaf4",2)
        self.txt(32,34,"ЧЕКУШКА 2D",16,"#ffe27a",anchor="w")
        self.txt(32,65,f"Бутылки {len(self.got_b)}/{len(self.level['bottles'])}    Монеты {len(self.got_c)}/{len(self.level['coins'])}",12,"#ffffff",anchor="w")
        self.rect(420,24,680,36,"#294e68")
        self.rect(420,24,420+260*self.x/self.level["end"],36,"#ffdc58")
        self.txt(550,54,self.level["name"].upper(),10,"#ffffff")
        self.rect(870,16,1080,57,"#142c43","#b7eaf4",2)
        self.txt(975,36,f"★ {self.total_coins}",15,"#ffe27a")
    def particles_draw(self):
        for x,y,vx,vy,life,col in self.particles:
            sx=x-self.camera
            if -10<sx<W+10:
                rr=max(1,int(5*life/.55)); self.c.create_oval(sx-rr,y-rr,sx+rr,y+rr,fill=col,outline="")
    def panel(self,title,sub):
        self.rect(0,0,W,H,"#101d32")
        for x,y,r in [(110,100,90),(980,540,170),(900,80,45)]:
            self.c.create_oval(x-r,y-r,x+r,y+r,fill="#1b3855",outline="")
        self.txt(W/2,120,title,42,"#ffe27a")
        self.txt(W/2,175,sub,15,"#d6edf5",False)
    def check_updates(self):
        if REPO_OWNER == "YOUR_GITHUB_USERNAME" or REPO_NAME == "YOUR_REPO":
            messagebox.showinfo("Обновления", "Сначала укажи ссылку на GitHub-репозиторий. После этого обновления будут работать.")
            return
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
                                       f"Установлена версия {APP_VERSION}.\\nНовая версия: {latest}.\\nСкачать и установить?"):
                return
            self.download_update()
        except Exception as e:
            messagebox.showerror("Ошибка обновления",
                                 "Не удалось проверить обновления. Проверь подключение к интернету и GitHub.\\n\\n" + str(e))

    def download_update(self):
        try:
            req = urllib.request.Request(GAME_URL, headers={"User-Agent": "ChekushkaAdventure"})
            with urllib.request.urlopen(req, timeout=30) as response:
                new_code = response.read()
            if not new_code.startswith(b"") or len(new_code) < 1000:
                raise ValueError("Файл обновления пустой или повреждён")
            folder = os.path.dirname(os.path.abspath(__file__))
            temp_file = os.path.join(folder, "chekushka_adventure.new.py")
            with open(temp_file, "wb") as f:
                f.write(new_code)
            bat_file = os.path.join(folder, "apply_update.bat")
            current_python = sys.executable
            with open(bat_file, "w", encoding="utf-8") as f:
                f.write("@echo off\\r\\n")
                f.write("chcp 65001 >nul\\r\\n")
                f.write("timeout /t 2 /nobreak >nul\\r\\n")
                f.write('copy /Y "chekushka_adventure.new.py" "chekushka_adventure.py" >nul\\r\\n')
                f.write(f'"{current_python}" "chekushka_adventure.py"\\r\\n')
                f.write('del "%~f0"\\r\\n')
            messagebox.showinfo("Обновление", "Обновление скачано. Игра перезапустится.")
            subprocess.Popen(["cmd", "/c", bat_file], cwd=folder, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", "Не удалось установить обновление.\\n\\n" + str(e))

    def draw_menu(self):
        self.panel("ЧЕКУШКА 2D","Маленький герой. Большое приключение.")
        self.buttons=[]
        self.button(W/2,285,300,58,"ИГРАТЬ",lambda:setattr(self,"screen","levels"))
        self.button(W/2,365,300,58,"ВЫБРАТЬ СКИН",lambda:setattr(self,"screen","skins"),f"Открыто монет: {self.total_coins}")
        self.button(W/2,445,300,48,"ПРОВЕРИТЬ ОБНОВЛЕНИЯ",self.check_updates)
        self.txt(W/2,520,"A / D или ← / → — движение     SPACE — прыжок",14,"#d6edf5",False)
        self.txt(W/2,545,"Собирай монеты, обходи шипы и побеждай слизней!",13,"#a9c5d5",False)
        self.txt(W/2,575,f"Версия {APP_VERSION}",11,"#7895aa",False)
    def draw_levels(self):
        self.panel("ВЫБОР УРОВНЯ","Пройди уровень, чтобы открыть следующий")
        self.buttons=[]
        for i,l in enumerate(LEVELS):
            col=i%2; row=i//2; x=W/2+(col-.5)*310; y=265+row*105
            locked=i+1>self.unlocked
            self.button(x,y,275,72,("🔒 " if locked else f"0{i+1}  ")+l["name"],lambda j=i:self.start_level(j), "Закрыт" if locked else l["subtitle"],locked)
        self.button(W/2,555,210,48,"НАЗАД",lambda:setattr(self,"screen","menu"))
    def draw_skins(self):
        self.panel("ВЫБОР СКИНА",f"Твои монеты: {self.total_coins}  •  Выбери внешний вид героя")
        self.buttons=[]
        for i,s in enumerate(SKINS):
            col=i%3; row=i//3; x=250+col*300; y=285+row*145
            self.c.create_oval(x-31,y-36,x+31,y+26,fill=s["body"],outline=s["shine"],width=3)
            self.c.create_oval(x-15,y-17,x-5,y-4,fill="white",outline="")
            self.c.create_oval(x+5,y-17,x+15,y-4,fill="white",outline="")
            owned=(s["price"]==0 or self.total_coins>=s["price"] or getattr(self,"owned_skins",set()).__contains__(i))
            if not hasattr(self,"owned_skins"): self.owned_skins={0}
            # Покупка сохраняется как разблокировка
            if i in self.owned_skins: owned=True
            label="ВЫБРАН" if i==self.skin_index else ("ВЫБРАТЬ" if owned else f"КУПИТЬ • {s['price']} ★")
            def choose(j=i):
                ss=SKINS[j]
                if j not in self.owned_skins:
                    if self.total_coins<ss["price"]: return
                    self.total_coins-=ss["price"]; self.owned_skins.add(j); self.save()
                self.skin_index=j; self.save()
            self.button(x,y+52,190,42,label,choose,s["name"],not owned and self.total_coins<s["price"])
        self.button(W/2,555,210,48,"НАЗАД",lambda:setattr(self,"screen","menu"))
    def draw(self):
        self.c.delete("all"); self.buttons=[]
        if self.screen in ("play","pause","win","dead"):
            self.sky(); self.world(); self.particles_draw()
            self.player(); self.hud()
        if self.screen=="menu": self.draw_menu()
        elif self.screen=="levels": self.draw_levels()
        elif self.screen=="skins": self.draw_skins()
        elif self.screen=="pause":
            self.rect(0,0,W,H,"#101d32"); self.txt(W/2,230,"ПАУЗА",45,"#ffe27a")
            self.txt(W/2,300,"Нажми P или ESC, чтобы продолжить",17,"#ffffff",False)
            self.buttons=[]; self.button(W/2,390,230,52,"В МЕНЮ",lambda:setattr(self,"screen","menu"))
        elif self.screen=="dead":
            self.rect(0,0,W,H,"#101d32"); self.txt(W/2,230,"ОЙ! ПОПАЛСЯ!",42,"#ff8978")
            self.txt(W/2,300,"Попробуй ещё раз — у тебя получится",17,"#ffffff",False)
            self.buttons=[]; self.button(W/2,390,240,54,"ПОВТОРИТЬ",lambda:self.start_level(self.level_index))
            self.button(W/2,465,240,48,"К УРОВНЯМ",lambda:setattr(self,"screen","levels"))
        elif self.screen=="win":
            self.rect(0,0,W,H,"#101d32"); self.txt(W/2,205,"УРОВЕНЬ ПРОЙДЕН!",42,"#ffe27a")
            self.txt(W/2,280,f"Бутылки: {len(self.got_b)}/{len(self.level['bottles'])}    Монеты: {len(self.got_c)}/{len(self.level['coins'])}",18,"#ffffff",False)
            self.buttons=[]
            if self.level_index<len(LEVELS)-1:
                self.button(W/2,375,250,55,"СЛЕДУЮЩИЙ УРОВЕНЬ",lambda:self.start_level(self.level_index+1))
            self.button(W/2,450,250,48,"К УРОВНЯМ",lambda:setattr(self,"screen","levels"))
        self.c.bind("<Button-1>",self.click)
    def loop(self):
        now=time.perf_counter(); dt=min(now-self.last,.035); self.last=now
        self.update(dt); self.draw(); self.root.after(16,self.loop)

if __name__=="__main__":
    root=tk.Tk()
    Game(root)
    root.mainloop()
