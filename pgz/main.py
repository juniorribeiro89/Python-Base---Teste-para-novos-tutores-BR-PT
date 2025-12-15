# Jogo Platformer - Um herói que pula em plataformas!
import pgzrun, random, math
from pygame import Rect

# Configurações do jogo
WIDTH = 800   # Largura da tela
HEIGHT = 600  # Altura da tela
GRAVITY = 0.8 # Força da gravidade (puxa para baixo)
JUMP = -15    # Força do pulo (negativo porque sobe)
SPEED = 5     # Velocidade do personagem

# Estados do jogo
MENU = 0      # Tela de menu
PLAYING = 1   # Jogando
OVER = 2      # Fim de jogo

# Classe para animações dos personagens
class Animation:
    def __init__(self, images, speed=5):
        # Lista de imagens para animação
        self.images = images
        self.speed = speed      # Velocidade da animação
        self.frame = 0          # Frame atual
        self.timer = 0          # Contador de tempo
    
    def update(self):
        # Atualiza o frame da animação
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.images)
    
    def image(self):
        # Retorna a imagem atual da animação
        if not self.images:
            return None
        img_name = self.images[self.frame]
        img = getattr(images, img_name, None)
        return img

# Classe base para todos os personagens
class Entity:
    def __init__(self, x, y, w, h):
        # Retângulo que representa o personagem
        self.rect = Rect(x, y, w, h)
        self.vx = 0  # Velocidade horizontal
        self.vy = 0  # Velocidade vertical
        self.facing_right = True  # Direção do personagem
        self.ground = False       # Se está no chão
        self.anim = None          # Animação do personagem
    
    def move(self, platforms):
        # Movimenta o personagem com física
        if not self.ground:
            self.vy += GRAVITY  # Aplica gravidade
        
        # Move o personagem
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Verifica colisão com plataformas
        self.ground = False
        for p in platforms:
            if self.rect.colliderect(p) and self.vy > 0 and self.rect.bottom > p.top:
                self.rect.bottom = p.top  # Para em cima da plataforma
                self.vy = 0               # Zera velocidade vertical
                self.ground = True        # Está no chão

# Classe do jogador (herói)
class Player(Entity):
    def __init__(self):
        super().__init__(100, 100, 30, 50)
        self.lives = 3   # Vidas do jogador
        self.score = 0   # Pontuação
        # Animação do jogador (duas imagens alternadas)
        self.anim = Animation(['player_idle1', 'player_idle2'], 10)
    
    def update(self, platforms, enemies):
        # Atualiza o jogador
        self.move(platforms)
        
        # Verifica colisão com inimigos
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if self.vy > 0 and self.rect.bottom < enemy.rect.bottom:
                    # Pula em cima do inimigo (derrota)
                    enemies.remove(enemy)
                    self.score += 100
                    self.vy = JUMP * 0.7
                else:
                    # Toma danho (perde vida)
                    self.lives -= 1
                    self.rect.x, self.rect.y = 100, 100
        
        # Mantém jogador na tela
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        
        # Atualiza animação
        if self.anim:
            self.anim.update()
        
        # Retorna estado do jogo
        return OVER if self.lives <= 0 else PLAYING
    
    def jump(self):
        # Faz o jogador pular
        if self.ground:
            self.vy = JUMP
            self.ground = False
    
    def draw(self):
        # Desenha o jogador
        if self.anim and self.anim.image():
            img = self.anim.image()
            screen.blit(img, (self.rect.x, self.rect.y))
        else:
            # Desenha um retângulo azul se não tiver sprite
            screen.draw.filled_rect(self.rect, (0, 120, 255))

# Classe dos inimigos
class Enemy(Entity):
    def __init__(self, x, y, r):
        super().__init__(x, y, 32, 32)
        self.start = x  # Posição inicial
        self.range = r  # Alcance do patrulhamento
        self.speed = random.uniform(1, 2.5)  # Velocidade aleatória
        # Animação do inimigo (duas imagens alternadas)
        self.anim = Animation(['enemy_move1', 'enemy_move2'], 7)
    
    def update(self, platforms):
        # Patrulha: vai e volta em uma área
        if abs(self.rect.x - self.start) >= self.range:
            self.speed *= -1  # Inverte direção
            self.facing_right = self.speed > 0  # Atualiza direção
        
        self.vx = self.speed
        self.move(platforms)
        
        # Atualiza animação
        if self.anim:
            self.anim.update()
    
    def draw(self):
        # Desenha o inimigo
        if self.anim and self.anim.image():
            img = self.anim.image()
            screen.blit(img, (self.rect.x, self.rect.y))
        else:
            # Desenha um retângulo vermelho se não tiver sprite
            screen.draw.filled_rect(self.rect, (255, 50, 50))

# Classe para botões do menu
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = Rect(x, y, w, h)  # Área do botão
        self.text = text              # Texto do botão
        self.color = (70, 130, 180)   # Cor normal
        self.hover = False            # Se o mouse está em cima
    
    def draw(self):
        # Desenha o botão
        color = (100, 160, 210) if self.hover else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.rect(self.rect, (255, 255, 255))
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color=(255, 255, 255))

# Classe principal do jogo
class Game:
    def __init__(self):
        self.state = MENU      # Estado inicial: menu
        self.music_on = True   # Música ligada
        # Cria os botões do menu
        self.buttons = [
            Button(250, 200, 300, 60, "JOGAR"),
            Button(250, 280, 300, 60, "MÚSICA: ON"),
            Button(250, 360, 300, 60, "SAIR")
        ]
        self.reset()  # Prepara o jogo
    
    def reset(self):
        # Reinicia o jogo
        self.player = Player()  # Cria jogador
        # Cria plataformas (retângulos onde se pode pisar)
        self.platforms = [
            Rect(0, 560, 800, 40),    # Chão
            Rect(200, 400, 200, 20),  # Plataforma 1
            Rect(500, 300, 150, 20),  # Plataforma 2
            Rect(100, 250, 100, 20),  # Plataforma 3
            Rect(400, 150, 200, 20)   # Plataforma 4
        ]
        # Cria inimigos
        self.enemies = [
            Enemy(250, 350, 100),  # Inimigo 1
            Enemy(550, 250, 80),   # Inimigo 2
            Enemy(150, 200, 60)    # Inimigo 3
        ]
    
    def update(self):
        # Atualiza o jogo a cada frame
        import pygame
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        if self.state == MENU:
            # Menu principal
            for i, btn in enumerate(self.buttons):
                btn.hover = btn.rect.collidepoint(mouse_pos)
                if mouse_click and btn.hover:
                    if i == 0:  # Botão JOGAR
                        self.state = PLAYING
                    elif i == 1:  # Botão MÚSICA
                        self.music_on = not self.music_on
                        btn.text = f"MÚSICA: {'ON' if self.music_on else 'OFF'}"
                    elif i == 2:  # Botão SAIR
                        import sys
                        sys.exit()
        
        elif self.state == PLAYING:
            # Jogo rodando
            
            # Controles do jogador
            if keyboard.left:
                self.player.vx = -SPEED
                self.player.facing_right = False
            elif keyboard.right:
                self.player.vx = SPEED
                self.player.facing_right = True
            else:
                self.player.vx = 0
            
            # Pulo
            if keyboard.up:
                self.player.jump()
            
            # Atualiza inimigos
            for enemy in self.enemies:
                enemy.update(self.platforms)
            
            # Atualiza jogador e verifica se perdeu
            self.state = self.player.update(self.platforms, self.enemies)
        
        elif self.state == OVER and mouse_click:
            # Fim de jogo - volta ao menu
            self.state = MENU
            self.reset()
    
    def draw(self):
        # Desenha tudo na tela
        screen.clear()
        
        if self.state == MENU:
            # Desenha menu
            screen.fill((40, 40, 60))  # Fundo escuro
            screen.draw.text("PLATFORMER", center=(400, 100), fontsize=60, color=(255, 255, 255))
            
            # Desenha botões
            for btn in self.buttons:
                btn.draw()
            
            # Instruções
            screen.draw.text("SETAS: MOVER   ↑ PULAR", center=(400, 500), fontsize=24, color=(200, 200, 200))
        
        elif self.state == PLAYING:
            # Desenha jogo
            screen.fill((135, 206, 235))  # Céu azul
            
            # Desenha plataformas
            for platform in self.platforms:
                screen.draw.filled_rect(platform, (100, 200, 100))
            
            # Desenha inimigos
            for enemy in self.enemies:
                enemy.draw()
            
            # Desenha jogador
            self.player.draw()
            
            # Desenha informações (HUD)
            screen.draw.text(f"VIDAS: {self.player.lives}", (10, 10), fontsize=30, color=(255, 255, 255))
            screen.draw.text(f"PONTOS: {self.player.score}", (WIDTH - 200, 10), fontsize=30, color=(255, 255, 255))
        
        elif self.state == OVER:
            # Desenha tela de fim de jogo
            screen.fill((40, 40, 60))
            screen.draw.text("FIM DE JOGO", center=(400, 200), fontsize=80, color=(255, 50, 50))
            screen.draw.text(f"PONTUAÇÃO: {self.player.score}", center=(400, 300), fontsize=40, color=(255, 255, 255))

# Cria o jogo
game = Game()

# Funções que o Pygame Zero precisa
def update():
    # Chamada a cada frame para atualizar
    game.update()

def draw():
    # Chamada a cada frame para desenhar
    game.draw()

def on_mouse_down(pos, button):
    # Quando clica com o mouse
    if game.state == MENU and button == 1:
        for i, btn in enumerate(game.buttons):
            if btn.rect.collidepoint(pos):
                if i == 0:
                    game.state = PLAYING
                elif i == 1:
                    game.music_on = not game.music_on
                    btn.text = f"MÚSICA: {'ON' if game.music_on else 'OFF'}"
                elif i == 2:
                    import sys
                    sys.exit()

# Inicia o jogo!
pgzrun.go()