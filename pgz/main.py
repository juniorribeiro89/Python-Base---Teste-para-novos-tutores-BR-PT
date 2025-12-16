import pgzrun, random, math
from pygame import Rect

WIDTH, HEIGHT = 800, 600
GRAVITY, JUMP, SPEED = 0.8, -15, 5
MENU, PLAYING, OVER = 0, 1, 2

class Animation:
    def __init__(self, images, speed=5):
        self.images, self.speed, self.frame, self.timer, self.flipped = images, speed, 0, 0, False
    def update(self):
        self.timer += 1
        if self.timer >= self.speed: self.timer, self.frame = 0, (self.frame + 1) % len(self.images)
    def image(self):
        if not self.images: return None
        img_name = self.images[self.frame]
        img = getattr(images, img_name, None)
        return img

class Entity:
    def __init__(self, x, y, w, h):
        self.rect, self.vx, self.vy, self.facing_right, self.ground = Rect(x, y, w, h), 0, 0, True, False
    def move(self, platforms):
        if not self.ground: self.vy += GRAVITY
        self.rect.x += self.vx; self.rect.y += self.vy
        self.ground = False
        for p in platforms:
            if self.rect.colliderect(p) and self.vy > 0 and self.rect.bottom > p.top:
                self.rect.bottom, self.vy, self.ground = p.top, 0, True

class Player(Entity):
    def __init__(self):
        super().__init__(100, 100, 30, 50)
        self.lives, self.score, self.anim = 3, 0, Animation(['player_idle1', 'player_idle2'], 10)
    def update(self, platforms, enemies):
        self.move(platforms)
        for e in enemies[:]:
            if self.rect.colliderect(e.rect):
                if self.vy > 0 and self.rect.bottom < e.rect.bottom:
                    enemies.remove(e); self.score += 100; self.vy = JUMP * 0.7
                else: self.lives -= 1; self.rect.x, self.rect.y = 100, 100
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        if self.anim: self.anim.update()
        return OVER if self.lives <= 0 else PLAYING
    def jump(self):
        if self.ground: self.vy = JUMP; self.ground = False
    def draw(self):
        if self.anim and self.anim.image():
            img = self.anim.image()
            screen.blit(img, (self.rect.x, self.rect.y))
        else: screen.draw.filled_rect(self.rect, (0,120,255))

class Enemy(Entity):
    def __init__(self, x, y, r):
        super().__init__(x, y, 32, 32)
        self.start, self.range, self.speed = x, r, random.uniform(1, 2.5)
        self.anim = Animation(['enemy_move1', 'enemy_move2'], 7)
    def update(self, platforms):
        if abs(self.rect.x - self.start) >= self.range: 
            self.speed *= -1; self.facing_right = self.speed > 0
        self.vx = self.speed; self.move(platforms)
        if self.anim: self.anim.update()
    def draw(self):
        if self.anim and self.anim.image():
            img = self.anim.image()
            screen.blit(img, (self.rect.x, self.rect.y))
        else: screen.draw.filled_rect(self.rect, (255,50,50))

class Button:
    def __init__(self, x, y, w, h, t):
        self.rect, self.text, self.color, self.hover = Rect(x, y, w, h), t, (70,130,180), False
    def draw(self):
        c = (100,160,210) if self.hover else self.color
        screen.draw.filled_rect(self.rect, c)
        screen.draw.rect(self.rect, (255,255,255))
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color=(255,255,255))

class Game:
    def __init__(self):
        self.state, self.music_on = MENU, True
        self.buttons = [Button(250,200,300,60,"JOGAR"), Button(250,280,300,60,"MÚSICA: ON"), Button(250,360,300,60,"SAIR")]
        self.reset()
    def reset(self):
        self.player = Player()
        self.platforms = [Rect(0,560,800,40), Rect(200,400,200,20), Rect(500,300,150,20), Rect(100,250,100,20), Rect(400,150,200,20)]
        self.enemies = [Enemy(250,350,100), Enemy(550,250,80), Enemy(150,200,60)]
    def update(self):
        import pygame
        mouse_pos, mouse_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]
        if self.state == MENU:
            for i,b in enumerate(self.buttons):
                b.hover = b.rect.collidepoint(mouse_pos)
                if mouse_click and b.hover:
                    if i == 0: self.state = PLAYING
                    elif i == 1: 
                        self.music_on = not self.music_on
                        b.text = f"MÚSICA: {'ON' if self.music_on else 'OFF'}"
                    elif i == 2: import sys; sys.exit()
        elif self.state == PLAYING:
            self.player.vx = (-SPEED if keyboard.left else SPEED if keyboard.right else 0)
            if keyboard.left: self.player.facing_right = False
            if keyboard.right: self.player.facing_right = True
            if keyboard.up: self.player.jump()
            for e in self.enemies: e.update(self.platforms)
            self.state = self.player.update(self.platforms, self.enemies)
        elif self.state == OVER and mouse_click: self.state = MENU; self.reset()
    def draw(self):
        screen.clear()
        if self.state == MENU:
            screen.fill((40,40,60))
            screen.draw.text("PLATFORMER", center=(400,100), fontsize=60, color=(255,255,255))
            for b in self.buttons: b.draw()
            screen.draw.text("SETAS: MOVER ↑ PULAR", center=(400,500), fontsize=24, color=(200,200,200))
        elif self.state == PLAYING:
            screen.fill((135,206,235))
            for p in self.platforms: screen.draw.filled_rect(p, (100,200,100))
            for e in self.enemies: e.draw()
            self.player.draw()
            screen.draw.text(f"VIDAS: {self.player.lives}", (10,10), fontsize=30, color=(255,255,255))
            screen.draw.text(f"PONTOS: {self.player.score}", (WIDTH-200,10), fontsize=30, color=(255,255,255))
        elif self.state == OVER:
            screen.fill((40,40,60))
            screen.draw.text("FIM DE JOGO", center=(400,200), fontsize=80, color=(255,50,50))
            screen.draw.text(f"PONTUAÇÃO: {self.player.score}", center=(400,300), fontsize=40, color=(255,255,255))

game = Game()
def update(): game.update()
def draw(): game.draw()
def on_mouse_down(pos, button):
    if game.state == MENU and button == 1:
        for i,b in enumerate(game.buttons):
            if b.rect.collidepoint(pos):
                if i == 0: game.state = PLAYING
                elif i == 1: 
                    game.music_on = not game.music_on
                    b.text = f"MÚSICA: {'ON' if game.music_on else 'OFF'}"
                elif i == 2: import sys; sys.exit()
pgzrun.go()