import thumby
import random
import time

# Initialize display and set FPS
thumby.display.setFPS(30)

# Bitmaps for grid cells (6x6 pixels)
unknown_bitmap = bytearray([255,129,129,129,129,255])  # '?'
hit_bitmap = bytearray([129,66,36,36,66,129])        # 'X'
miss_bitmap = bytearray([255,129,129,129,129,255])     # 'O'
cursor_bitmap = bytearray([255,128,128,128,128,255])   # Border

# Create sprite objects
cell_sprites = [
    thumby.Sprite(6, 6, unknown_bitmap, 0, 0),
    thumby.Sprite(6, 6, hit_bitmap, 0, 0),
    thumby.Sprite(6, 6, miss_bitmap, 0, 0)
]
cursor_sprite = thumby.Sprite(6, 6, cursor_bitmap, 0, 0)

# Game state
GRID_SIZE = 5
MAX_MOVES = 15
SHIPS = [(3, "Carrier"), (2, "Destroyer")]  # (length, name)
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # Ship positions
player_grid = [['?'] * GRID_SIZE for _ in range(GRID_SIZE)]  # Player view
cursor_x, cursor_y = 0, 0
moves_left = MAX_MOVES
hits_needed = sum(length for length, _ in SHIPS)
hits = 0
game_state = "start"  # start, playing, won, lost

def place_ships():
    """Randomly place ships on the grid."""
    global grid
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    for length, _ in SHIPS:
        placed = False
        while not placed:
            orient = random.choice(['h', 'v'])  # Horizontal or vertical
            if orient == 'h':
                x = random.randint(0, GRID_SIZE - length)
                y = random.randint(0, GRID_SIZE - 1)
                # Check if space is free
                if all(grid[y][x+i] == 0 for i in range(length)):
                    for i in range(length):
                        grid[y][x+i] = 1
                    placed = True
            else:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - length)
                if all(grid[y+i][x] == 0 for i in range(length)):
                    for i in range(length):
                        grid[y+i][x] = 1
                    placed = True

def draw_grid():
    """Draw the game grid."""
    thumby.display.fill(0)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = player_grid[y][x]
            sprite = cell_sprites[0 if cell == '?' else 1 if cell == 'X' else 2]
            sprite.x = x * 7 + 5  # 6px sprite + 1px gap
            sprite.y = y * 7 + 2
            thumby.display.drawSprite(sprite)
    # Draw cursor
    cursor_sprite.x = cursor_x * 7 + 5
    cursor_sprite.y = cursor_y * 7 + 2
    thumby.display.drawSprite(cursor_sprite)
    # Draw status
    thumby.display.drawText(f"M:{moves_left} H:{hits}", 40, 2, 1)
    if game_state == "start":
        thumby.display.drawText("Press B", 40, 12, 1)
        thumby.display.drawText("to Start", 40, 22, 1)
    elif game_state == "won":
        thumby.display.drawText("You Win!", 40, 12, 1)
        thumby.display.drawText("B:Restart", 40, 22, 1)
    elif game_state == "lost":
        thumby.display.drawText("You Lose!", 40, 12, 1)
        thumby.display.drawText("B:Restart", 40, 22, 1)
    thumby.display.update()

def handle_input():
    """Handle player input."""
    global cursor_x, cursor_y, game_state, moves_left, hits, player_grid
    if game_state == "start" or game_state == "won" or game_state == "lost":
        if thumby.buttonB.pressed():
            # Reset game
            global grid, player_grid, moves_left, hits, cursor_x, cursor_y
            place_ships()
            player_grid = [['?'] * GRID_SIZE for _ in range(GRID_SIZE)]
            moves_left = MAX_MOVES
            hits = 0
            cursor_x, cursor_y = 0, 0
            game_state = "playing"
        return
    if game_state != "playing":
        return
    # Move cursor
    if thumby.buttonU.justPressed() and cursor_y > 0:
        cursor_y -= 1
    if thumby.buttonD.justPressed() and cursor_y < GRID_SIZE - 1:
        cursor_y += 1
    if thumby.buttonL.justPressed() and cursor_x > 0:
        cursor_x -= 1
    if thumby.buttonR.justPressed() and cursor_x < GRID_SIZE - 1:
        cursor_x += 1
    # Fire
    if thumby.buttonA.justPressed():
        if player_grid[cursor_y][cursor_x] == '?':
            moves_left -= 1
            if grid[cursor_y][cursor_x] == 1:
                player_grid[cursor_y][cursor_x] = 'X'
                hits += 1
                thumby.audio.play(1000, 200)  # Hit sound
            else:
                player_grid[cursor_y][cursor_x] = 'O'
                thumby.audio.play(200, 200)   # Miss sound
            # Check game over
            if hits >= hits_needed:
                game_state = "won"
            elif moves_left <= 0:
                game_state = "lost"

# Initialize game
place_ships()

# Main game loop
while True:
    draw_grid()
    handle_input()
    time.sleep(0.1)  # Small delay for input responsiveness