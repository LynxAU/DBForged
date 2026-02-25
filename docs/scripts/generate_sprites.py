#!/usr/bin/env python
"""
Pixel art sprite generator for Kame Island.
Generates simple pixel art sprites for game use.
"""

from PIL import Image, ImageDraw
import os

# Output directory
OUTPUT_DIR = "sprites"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color palettes
SAND_COLOR = (237, 201, 175)
SAND_DARK = (210, 170, 140)
WATER_COLOR = (60, 160, 220)
WATER_DARK = (40, 130, 190)
WATER_LIGHT = (100, 200, 255)
TREE_TRUNK = (101, 67, 33)
TREE_LEAVES = (34, 139, 34)
TREE_LEAVES_LIGHT = (60, 180, 60)
HOUSE_WALL = (240, 230, 200)
HOUSE_ROOF = (180, 60, 40)
HOUSE_DOOR = (101, 67, 33)
HOUSE_WINDOW = (135, 206, 250)
FLOOR_WOOD = (160, 110, 70)
FLOOR_DARK = (130, 90, 55)
SKY_BLUE = (135, 206, 235)

def create_pixel_art(size=32):
    """Create all sprite assets."""
    
    # 1. SAND TILE
    sand = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sand)
    # Base sand color
    draw.rectangle([0, 0, size-1, size-1], fill=SAND_COLOR)
    # Add texture dots
    for _ in range(8):
        import random
        x = random.randint(2, size-4)
        y = random.randint(2, size-4)
        draw.rectangle([x, y, x+2, y+2], fill=SAND_DARK)
    sand.save(f"{OUTPUT_DIR}/sand.png")
    print("Created: sand.png")
    
    # 2. WATER TILE
    water = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(water)
    # Base water
    draw.rectangle([0, 0, size-1, size-1], fill=WATER_COLOR)
    # Wave highlights
    for i in range(0, size, 6):
        draw.line([(i, size//3), (i+4, size//3)], fill=WATER_LIGHT, width=1)
        draw.line([(i+2, 2*size//3), (i+6, 2*size//3)], fill=WATER_LIGHT, width=1)
    water.save(f"{OUTPUT_DIR}/water.png")
    print("Created: water.png")
    
    # 3. TREE
    tree = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tree)
    # Trunk
    trunk_width = max(3, size // 6)
    trunk_x = (size - trunk_width) // 2
    draw.rectangle([trunk_x, size//2, trunk_x + trunk_width, size-2], fill=TREE_TRUNK)
    # Leaves (circular blob)
    center = size // 2
    radius = size // 3
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], fill=TREE_LEAVES)
    draw.ellipse([center-radius//2, center-radius//2, center+radius//2, center+radius//2], fill=TREE_LEAVES_LIGHT)
    tree.save(f"{OUTPUT_DIR}/tree.png")
    print("Created: tree.png")
    
    # 4. HOUSE EXTERIOR
    house = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(house)
    # Walls
    wall_top = size // 4
    wall_bottom = size - 4
    draw.rectangle([4, wall_top, size-4, wall_bottom], fill=HOUSE_WALL, outline=(180, 170, 140), width=1)
    # Roof (triangle)
    roof_points = [(size//2, 2), (2, wall_top), (size-2, wall_top)]
    draw.polygon(roof_points, fill=HOUSE_ROOF, outline=(140, 40, 30))
    # Door
    door_width = size // 4
    door_x = (size - door_width) // 2
    draw.rectangle([door_x, wall_bottom-12, door_x+door_width, wall_bottom], fill=HOUSE_DOOR, outline=(80, 50, 20))
    # Window
    win_size = 6
    draw.rectangle([size-12, wall_top+4, size-12+win_size, wall_top+4+win_size], fill=HOUSE_WINDOW, outline=(100, 150, 200))
    house.save(f"{OUTPUT_DIR}/house.png")
    print("Created: house.png")
    
    # 5. HOUSE INTERIOR (floor)
    interior = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(interior)
    # Wooden floor planks
    plank_height = 4
    for y in range(0, size, plank_height):
        # Alternate colors for plank effect
        color = FLOOR_WOOD if (y // plank_height) % 2 == 0 else FLOOR_DARK
        draw.rectangle([2, y, size-2, y+plank_height-1], fill=color)
    # Add some wood grain lines
    for i in range(3):
        import random
        y = random.randint(4, size-4)
        draw.line([(4, y), (size-4, y)], fill=(140, 100, 60), width=1)
    interior.save(f"{OUTPUT_DIR}/house_interior.png")
    print("Created: house_interior.png")
    
    # 6. SKY BACKGROUND (optional)
    sky = Image.new('RGBA', (size, size), SKY_BLUE)
    sky.save(f"{OUTPUT_DIR}/sky.png")
    print("Created: sky.png")
    
    print(f"\nAll sprites saved to {OUTPUT_DIR}/")

def create_spritesheet(size=32):
    """Create a spritesheet with all elements."""
    
    # 6 sprites in a row
    sprites = []
    names = ["sand", "water", "tree", "house", "house_interior", "sky"]
    
    for name in names:
        try:
            img = Image.open(f"{OUTPUT_DIR}/{name}.png")
            sprites.append(img)
        except:
            print(f"Missing: {name}.png")
    
    if sprites:
        # Create horizontal spritesheet
        width = sprites[0].width
        height = sprites[0].height
        sheet = Image.new('RGBA', (width * len(sprites), height))
        
        for i, sprite in enumerate(sprites):
            sheet.paste(sprite, (i * width, 0))
        
        sheet.save(f"{OUTPUT_DIR}/spritesheet.png")
        print(f"Created spritesheet.png")

if __name__ == "__main__":
    print("Generating Kame Island sprites...")
    create_pixel_art(32)
    create_spritesheet(32)
    print("\nDone! You can find the sprites in the 'sprites' folder.")
