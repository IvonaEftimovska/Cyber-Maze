import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 960, 720
TILE = 48

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Maze Adventure")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BG = (10, 5, 25)             # deep purple background
WALL = (40, 0, 80)           # dark neon purple
TOKEN_COLOR = (0, 255, 255)  # bright cyan
WHITE = (180, 255, 255)      # soft neon white
GREEN = (0, 255, 150)        # neon green
RED = (255, 50, 150)         # hot pink
BLUE = (0, 200, 255)         # electric blue
TOP_BAR = (15, 0, 35)

FONT = pygame.font.SysFont("consolas", 22)
BIG_FONT = pygame.font.SysFont("consolas", 42, bold=True)
TITLE_FONT = pygame.font.SysFont("consolas", 64, bold=True)

# ---------------- SAFE IMAGE LOADING ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((200, 0, 200))
        return surf

SPRITE_SIZE = TILE - 6

good_spy = load_image(resource_path("assets/good_spy.png"), (SPRITE_SIZE, SPRITE_SIZE))
bad_spy = load_image(resource_path("assets/bad_spy.png"), (SPRITE_SIZE, SPRITE_SIZE))
portal_sprite = load_image(resource_path("assets/portal.png"), (TILE*2, TILE*2))
heart_img = load_image(resource_path("assets/heart.png"), (36, 36))

# ---------------- LEVELS ----------------
LEVELS = [
[
"11111111111111111111",
"10000000000000000001",
"10111111101111111101",
"10000000100000000001",
"10111011101110111101",
"10001000000000100001",
"11101011111110101111",
"10000010000000100001",
"10111010111110101101",
"10000000000000000001",
"11111111111111111111",
],
[
"11111111111111111111",
"10000000000000000001",
"10111101111101111101",
"10000001000001000001",
"10111011101110111001",
"10000000000000000001",
"11101111111111011111",
"10000000001000000001",
"10111110101011111001",
"10000000000000000001",
"11111111111111111111",
],
[
"11111111111111111111",
"10000000000000000001",
"10111111111111111101",
"10000000000000000001",
"10111101111111011101",
"10000001000001000001",
"11101111011101111011",
"10000000000000000001",
"10111111101111111101",
"10000000000000000001",
"11111111111111111111",
]
]

# ---------------- QUIZ WITH EXPLANATIONS ----------------
QUIZ_BANK = [
[
{"q":"Stranger asks for your password",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Never share passwords. Always report suspicious behavior."},

{"q":"Friend asks to play Minecraft",
 "options":["Answer","Block","Report"],
 "c":0,
 "exp":"Talking to real friends about games is safe."},

{"q":"Free iPhone link!",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Free prizes online are often scams."},
],
[
{"q":"Unknown user wants your address",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Your home address is private information."},

{"q":"Someone bullying in chat",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Cyberbullying should always be reported."},

{"q":"App asks for school name",
 "options":["Answer","Block","Report"],
 "c":1,
 "exp":"School information should not be shared online."},
],
[
{"q":"Send photo for free skins",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Never send personal photos to strangers."},

{"q":"Pop-up says you're hacked",
 "options":["Answer","Block","Report"],
 "c":1,
 "exp":"Suspicious pop-ups should be blocked."},

{"q":"Fake giveaway message",
 "options":["Answer","Block","Report"],
 "c":2,
 "exp":"Giveaway scams are very common online."},
]
]

# ---------------- STATE ----------------
state = "menu"
current_level = 0
current_question = 0
quiz_score = 0
feedback_active = False
feedback_text = ""
feedback_color = WHITE
explanation_text = ""
level_result_data = {}
invincible_timer = 0

play_button = pygame.Rect(WIDTH//2 - 200, 350, 400, 100)
tips_button = pygame.Rect(WIDTH//2 - 150, 480, 300, 70)
back_button = pygame.Rect(50, 600, 200, 60)
resume_button = pygame.Rect(WIDTH//2 - 150, 300, 300, 70)
restart_button = pygame.Rect(WIDTH//2 - 150, 400, 300, 70)
menu_button = pygame.Rect(WIDTH//2 - 150, 500, 300, 70)
gameover_restart_button = pygame.Rect(WIDTH//2 - 150, 380, 300, 70)
gameover_quit_button = pygame.Rect(WIDTH//2 - 150, 470, 300, 70)


# ---------------- PLAYER ----------------
class Player:
    def __init__(self):
        self.speed = 4
        self.lives = 3
        self.spawn()
        self.facing_right = True

    def spawn(self):
        self.rect = pygame.Rect(TILE + 3, TILE + 3, SPRITE_SIZE, SPRITE_SIZE)

    def move(self, dx, dy):

        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        self.rect.x += dx
        if is_wall(self.rect):
            self.rect.x -= dx

        self.rect.y += dy
        if is_wall(self.rect):
            self.rect.y -= dy

        self.rect.x = max(0, min(self.rect.x, len(LEVEL[0]) * TILE - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, len(LEVEL) * TILE - self.rect.height))

player = Player()

def get_empty_tiles(level):
    tiles = []
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] == "0":
                tiles.append((x,y))
    return tiles

def is_wall(rect):
    corners = [
        (rect.left, rect.top),
        (rect.right - 1, rect.top),
        (rect.left, rect.bottom - 1),
        (rect.right - 1, rect.bottom - 1),
    ]

    for px, py in corners:
        gx = px // TILE
        gy = py // TILE

        if gy < 0 or gy >= len(LEVEL):
            return True
        if gx < 0 or gx >= len(LEVEL[0]):
            return True

        if LEVEL[gy][gx] == "1":
            return True

    return False

def load_level():
    global LEVEL, tokens, enemies, portal
    LEVEL = LEVELS[current_level]
    tokens = []
    enemies = []
    portal = None
    player.spawn()
    player.lives = 3

    empty = get_empty_tiles(LEVEL)

    for (x,y) in random.sample(empty, min(15,len(empty))):
        tokens.append(pygame.Rect(x*TILE+18, y*TILE+18, 12, 12))

    for i in range(1 + current_level):
        x, y = random.choice(empty)
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        enemies.append({
            "rect": pygame.Rect(x * TILE + 3, y * TILE + 3, SPRITE_SIZE, SPRITE_SIZE),
            "dir": direction,
            "speed": 2 + current_level,
            "facing_right": True if direction[0] >= 0 else False
        })

def fade_transition(color=(0,0,0), speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(color)
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)

def draw_glow_rect(surface, color, rect, glow_radius=8):
    glow_surf = pygame.Surface(
        (rect.width + glow_radius*2, rect.height + glow_radius*2),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        glow_surf,
        (*color, 40),
        (glow_radius, glow_radius, rect.width, rect.height),
        border_radius=8
    )

    surface.blit(glow_surf, (rect.x - glow_radius, rect.y - glow_radius))

def draw_neon_button(surface, rect, color, text, font):
    mouse = pygame.mouse.get_pos()

    # Slight hover brightness
    if rect.collidepoint(mouse):
        glow_color = tuple(min(c + 40, 255) for c in color)
    else:
        glow_color = color

    # Glow
    draw_glow_rect(surface, glow_color, rect, 12)

    # Main button
    pygame.draw.rect(surface, glow_color, rect, border_radius=12)

    # Text
    text_surface = font.render(text, False, TOP_BAR)
    surface.blit(text_surface,
                 (rect.centerx - text_surface.get_width() // 2,
                  rect.centery - text_surface.get_height() // 2))

# ---------------- MAIN LOOP ----------------
running = True
while running:
    dt = clock.tick(60)/1000
    screen.fill(BG)

    if invincible_timer > 0:
        invincible_timer -= dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Press P to pause
            if event.key == pygame.K_p:
                if state == "maze":
                    state = "paused"

            # Press ESC to quit game
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # GAME OVER BUTTON CLICKS
        if state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
            if gameover_restart_button.collidepoint(event.pos):
                current_level = 0
                load_level()
                current_question = 0
                quiz_score = 0
                state = "maze"

            elif gameover_quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

        # MENU
        if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if play_button.collidepoint(event.pos):
                current_level = 0
                load_level()
                state = "maze"
            if tips_button.collidepoint(event.pos):
                state = "tips"

        if state == "tips" and event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.collidepoint(event.pos):
                state = "menu"

        # PAUSE MENU CLICKS
        if state == "paused" and event.type == pygame.MOUSEBUTTONDOWN:
            if resume_button.collidepoint(event.pos):
                state = "maze"

            elif restart_button.collidepoint(event.pos):
                load_level()
                state = "maze"

            elif menu_button.collidepoint(event.pos):
                state = "menu"

        # QUIZ CLICK
        if state == "quiz" and event.type == pygame.MOUSEBUTTONDOWN:

            # If feedback is currently shown → go to next question
            if feedback_active:
                feedback_active = False
                feedback_text = ""
                explanation_text = ""

                current_question += 1

                if current_question >= len(QUIZ_BANK[current_level]):
                    level_result_data = {
                        "score": quiz_score,
                        "total": len(QUIZ_BANK[current_level])
                    }
                    state = "level_result"

            else:
                options = QUIZ_BANK[current_level][current_question]["options"]
                mx, my = pygame.mouse.get_pos()

                for i, opt in enumerate(options):
                    r = pygame.Rect(280, 300 + i * 80, 400, 60)
                    if r.collidepoint(mx, my):

                        question_data = QUIZ_BANK[current_level][current_question]

                        if i == question_data["c"]:
                            quiz_score += 1
                            feedback_text = "Correct!"
                            feedback_color = GREEN
                        else:
                            feedback_text = "Wrong!"
                            feedback_color = RED

                        explanation_text = question_data["exp"]
                        feedback_active = True

        # RESULT CLICK
        if state == "level_result" and event.type == pygame.MOUSEBUTTONDOWN:
            if quiz_score == level_result_data["total"]:
                current_level += 1
                if current_level >= len(LEVELS):
                    state = "game_complete"
                else:
                    fade_transition()
                    load_level()
                    state = "maze"
            else:
                fade_transition()
                load_level()
                state = "maze"

            current_question = 0
            quiz_score = 0

    # ---------------- MENU ----------------
    if state == "menu":
        screen.blit(TITLE_FONT.render("CYBER MAZE", True, WHITE),
                    (WIDTH//2 - 220, 150))
        draw_neon_button(screen, play_button, GREEN, "PLAY", BIG_FONT)
        draw_neon_button(screen, tips_button, BLUE, "TIPS & TRICKS", FONT)

    # ---------------- PAUSED ----------------
    elif state == "paused":

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        screen.blit(BIG_FONT.render("PAUSED", True, WHITE),
                    (WIDTH // 2 - 120, 200))

        # Resume
        draw_neon_button(screen, resume_button, GREEN, "Resume Game", FONT)

        # Restart
        draw_neon_button(screen, restart_button, BLUE, "Restart Level", FONT)

        # Main Menu
        draw_neon_button(screen, menu_button, RED, "Main Menu", FONT)


    # ---------------- TIPS ----------------
    elif state == "tips":

        screen.fill((15, 20, 50))  # darker cyber background

        # Styled Header
        header = BIG_FONT.render("AGENT TRAINING BRIEFING", True, GREEN)
        screen.blit(header,
                    (WIDTH // 2 - header.get_width() // 2, 80))

        # Subtitle line
        pygame.draw.line(screen, BLUE,
                         (WIDTH // 2 - 250, 150),
                         (WIDTH // 2 + 250, 150), 3)

        # Mission Tips
        tips = [
            "Use the arrow keys to move through the cyber maze.",
            "Collect all data tokens to unlock the exit portal.",
            "Avoid enemy spies — they drain your lives.",
            "Answer cybersecurity questions correctly to advance.",
            "Press P to pause the mission at any time."
        ]

        for i, t in enumerate(tips):
            tip_text = FONT.render(t, True, WHITE)
            screen.blit(tip_text,
                        (WIDTH // 2 - tip_text.get_width() // 2,
                         220 + i * 50))

        # Back Button
        draw_neon_button(screen, back_button, BLUE, "BACK", FONT)

    # ---------------- MAZE ----------------
    elif state == "maze":

        pygame.draw.rect(screen, TOP_BAR, (0,0,WIDTH,60))
        level_title = FONT.render(f"LEVEL {current_level + 1}", True, WHITE)
        screen.blit(level_title, (WIDTH // 2 - level_title.get_width() // 2, 18))
        for i in range(player.lives):
            screen.blit(heart_img,(20+i*45,12))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-player.speed,0)
        if keys[pygame.K_RIGHT]: player.move(player.speed,0)
        if keys[pygame.K_UP]: player.move(0,-player.speed)
        if keys[pygame.K_DOWN]: player.move(0,player.speed)

        ROWS = len(LEVEL)
        COLS = len(LEVEL[0])
        offset_x = (WIDTH - COLS*TILE)//2
        offset_y = (HEIGHT - ROWS*TILE)//2

        for y in range(ROWS):
            for x in range(COLS):
                if LEVEL[y][x]=="1":
                    pygame.draw.rect(screen,WALL,
                        (offset_x+x*TILE,
                         offset_y+y*TILE,
                         TILE,TILE))

        for t in tokens[:]:
            draw_rect = t.move(offset_x,offset_y)
            pygame.draw.rect(screen,TOKEN_COLOR,draw_rect)
            if player.rect.colliderect(t):
                tokens.remove(t)

        if not tokens and portal is None:
            empty = get_empty_tiles(LEVEL)
            x,y = random.choice(empty)
            portal = pygame.Rect(x*TILE,y*TILE,TILE*2,TILE*2)

        if portal:
            portal_scale = 1 + 0.1 * pygame.time.get_ticks() % 10 / 10
            scaled_size = int(TILE * 2 * portal_scale)

            animated_portal = pygame.transform.scale(
                portal_sprite,
                (scaled_size, scaled_size)
            )

            draw_rect = animated_portal.get_rect(center=portal.move(offset_x, offset_y).center)
            screen.blit(animated_portal, draw_rect)

            if player.rect.colliderect(portal):
                state = "quiz"

        for e in enemies:
            dx, dy = e["dir"]
            if dx > 0:
                e["facing_right"] = True
            elif dx < 0:
                e["facing_right"] = False

            e["rect"].x += dx * e["speed"]
            e["rect"].y += dy * e["speed"]

            if is_wall(e["rect"]):
                e["rect"].x-=dx*e["speed"]
                e["rect"].y-=dy*e["speed"]
                e["dir"]=random.choice([(1,0),(-1,0),(0,1),(0,-1)])

            enemy_sprite = bad_spy

            # If moving RIGHT → flip
            if e["facing_right"]:
                enemy_sprite = pygame.transform.flip(bad_spy, True, False)

            draw_pos = e["rect"].move(offset_x, offset_y)

            screen.blit(enemy_sprite, e["rect"].move(offset_x, offset_y))

            #screen.blit(enemy_sprite,
                       # e["rect"].move(offset_x, offset_y))

            if player.rect.colliderect(e["rect"]) and invincible_timer<=0:
                player.lives-=1
                invincible_timer=1.0
                if player.lives<=0:
                    state="game_over"

        if invincible_timer<=0 or int(invincible_timer*10)%2==0:
            if player.facing_right:
                sprite = good_spy
            else:
                sprite = pygame.transform.flip(good_spy, True, False)

            draw_pos = player.rect.move(offset_x, offset_y)

            screen.blit(sprite, player.rect.move(offset_x, offset_y))
            #screen.blit(sprite, draw_pos)

    # ---------------- QUIZ ----------------
    elif state == "quiz":

        screen.fill((20, 10, 40))

        total = len(QUIZ_BANK[current_level])

        # Question Counter
        counter = FONT.render(
            f"Level {current_level + 1} - Question {current_question + 1}/{total}",
            True, WHITE)
        screen.blit(counter, (WIDTH // 2 - counter.get_width() // 2, 80))

        # Question Text
        q = QUIZ_BANK[current_level][current_question]["q"]

        # Wrap question text
        max_width = 700
        words = q.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if FONT.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        for i, line in enumerate(lines):
            qs = FONT.render(line.strip(), True, WHITE)
            screen.blit(qs, (WIDTH // 2 - qs.get_width() // 2, 150 + i * 30))

        # Answer Buttons
        options = QUIZ_BANK[current_level][current_question]["options"]
        for i, opt in enumerate(options):
            r = pygame.Rect(280, 300 + i * 80, 400, 60)
            pygame.draw.rect(screen, BLUE, r, border_radius=10)
            ts = FONT.render(opt, True, TOP_BAR)
            screen.blit(ts, (r.centerx - ts.get_width() // 2,
                             r.centery - ts.get_height() // 2))

        # ---- FEEDBACK DISPLAY ----
        if feedback_active:

            # Feedback title
            fb = BIG_FONT.render(feedback_text, True, feedback_color)
            fb_y = 520
            screen.blit(fb, (WIDTH // 2 - fb.get_width() // 2, fb_y))

            # Wrapped explanation
            words = explanation_text.split(" ")
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if FONT.size(test_line)[0] <= 700:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            start_y = fb_y + 60

            for i, line in enumerate(lines):
                exp_surface = FONT.render(line.strip(), True, WHITE)
                screen.blit(exp_surface,
                            (WIDTH // 2 - exp_surface.get_width() // 2,
                             start_y + i * 28))

            continue_text = FONT.render("Click anywhere to continue...", True, WHITE)
            screen.blit(continue_text,
                        (WIDTH // 2 - continue_text.get_width() // 2,
                         start_y + len(lines) * 28 + 20))

            # ---- PROGRESSION LOGIC (CRITICAL FIX) ----


    # ---------------- LEVEL RESULT ----------------
    elif state == "level_result":

        screen.fill((20,30,60))

        score = level_result_data["score"]
        total = level_result_data["total"]
        percent = score / total

        if percent == 1:
            rating = "GOLD AGENT"
            color = (255,215,0)
        elif percent >= 0.7:
            rating = "SILVER DEFENDER"
            color = (180,180,180)
        else:
            rating = "BRONZE ROOKIE"
            color = (205,127,50)

        screen.blit(BIG_FONT.render("LEVEL COMPLETE!",True,WHITE),
                    (WIDTH//2-200,200))
        screen.blit(FONT.render(f"Correct: {score} / {total}",True,WHITE),
                    (WIDTH//2-100,300))
        screen.blit(BIG_FONT.render(rating,True,color),
                    (WIDTH//2-200,380))
        screen.blit(FONT.render("Click to continue",True,WHITE),
                    (WIDTH//2-120,500))



    elif state == "game_over":

        screen.fill((80, 10, 10))

        # ---- Title ----

        title_surface = BIG_FONT.render("GAME OVER", True, WHITE)

        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))

        screen.blit(title_surface, title_rect)

        # ---- Buttons (Centered Group) ----

        button_spacing = 90

        gameover_restart_button.center = (WIDTH // 2, HEIGHT // 2)

        gameover_quit_button.center = (WIDTH // 2, HEIGHT // 2 + button_spacing)

        draw_neon_button(screen, gameover_restart_button, GREEN, "Restart Mission", FONT)

        draw_neon_button(screen, gameover_quit_button, RED, "Abort Mission", FONT)


    elif state=="game_complete":
        screen.fill((10,70,30))
        screen.blit(BIG_FONT.render("YOU SAVED CYBER CITY!",True,WHITE),
                    (WIDTH//2-250,300))

    # CRT Scanlines
    # for y in range(0, HEIGHT, 4):
    #    pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y), 1)

    scanline = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
    scanline.fill((0, 0, 0, 60))  # transparent black

    for y in range(0, HEIGHT, 4):
        screen.blit(scanline, (0, y))


    pygame.display.flip()

pygame.quit()
sys.exit()