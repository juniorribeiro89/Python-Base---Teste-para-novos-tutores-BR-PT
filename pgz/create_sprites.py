from PIL import Image, ImageDraw
import os
os.makedirs('images', exist_ok=True)

# Player sprites
for i in [1, 2]:
    img = Image.new('RGBA', (32, 50), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 5, 22, 17], fill=(0,120,255))  # Cabeça
    draw.rectangle([12, 17, 20, 35], fill=(0,100,200))  # Corpo
    draw.rectangle([14, 35, 18, 45], fill=(0,80,160))  # Pernas
    img.save(f'images/player_idle{i}.png')

# Enemy sprites  
for i in [1, 2]:
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([5, 5, 27, 27], fill=(255,50,50))  # Corpo
    draw.ellipse([11, 11, 15, 15], fill=(255,255,255))  # Olho
    draw.ellipse([17, 11, 21, 15], fill=(255,255,255))  # Olho
    img.save(f'images/enemy_move{i}.png')
print("Sprites criados!")