import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 960, 720
TILE = 48

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChatSmart - Cyber Maze Adventure")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BG = (15, 20, 40)
WALL = (30, 50, 90)
TOKEN_COLOR = (255, 215, 0)
WHITE = (255, 255, 255)
GREEN = (40, 200, 100)
RED = (220, 60, 60)
BLUE = (70, 130, 255)
TOP_BAR = (8, 12, 25)

FONT = pygame.font.SysFont("consolas", 22)
BIG_FONT = pygame.font.SysFont("consolas", 42, bold=True)
TITLE_FONT = pygame.font.SysFont("consolas", 64, bold=True)

# ---------------- SAFE IMAGE LOADING ----------------
def load_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((200, 0, 200))
        return surf

good_spy = load_image("assets/good_spy.png", (TILE-6, TILE-6))
bad_spy = load_image("assets/bad_spy.png", (TILE-6, TILE-6))
portal_sprite = load_image("assets/portal.png", (TILE*2, TILE*2))
heart_img = load_image("assets/heart.png", (36, 36))

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

    def spawn(self):
        self.rect = pygame.Rect(TILE+4, TILE+4, TILE-8, TILE-8)

    def move(self, dx, dy):
        self.rect.x += dx
        if is_wall(self.rect):
            self.rect.x -= dx
        self.rect.y += dy
        if is_wall(self.rect):
            self.rect.y -= dy

player = Player()

def get_empty_tiles(level):
    tiles = []
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] == "0":
                tiles.append((x,y))
    return tiles

def is_wall(rect):
    gx = rect.centerx // TILE
    gy = rect.centery // TILE
    return LEVEL[gy][gx] == "1"

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
        x,y = random.choice(empty)
        enemies.append({
            "rect": pygame.Rect(x*TILE, y*TILE, TILE-6, TILE-6),
            "dir": random.choice([(1,0),(-1,0),(0,1),(0,-1)]),
            "speed": 2 + current_level
        })

def fade_transition(color=(0,0,0), speed=5):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(color)
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)

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
            if event.key == pygame.K_ESCAPE:
                if state == "maze":
                    state = "paused"
                elif state == "paused":
                    state = "maze"

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
        screen.blit(TITLE_FONT.render("CHATSMART", True, WHITE),
                    (WIDTH//2 - 220, 150))
        pygame.draw.rect(screen, GREEN, play_button, border_radius=15)
        screen.blit(BIG_FONT.render("PLAY", True, WHITE),
                    (play_button.centerx - 70, play_button.centery - 20))
        pygame.draw.rect(screen, BLUE, tips_button, border_radius=10)
        screen.blit(FONT.render("TIPS & TRICKS", True, WHITE),
                    (tips_button.centerx - 80, tips_button.centery - 12))

    # ---------------- PAUSED ----------------
    elif state == "paused":

        # Draw frozen maze behind (optional)
        # (we don’t move enemies because movement code is only inside "maze")

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        screen.blit(BIG_FONT.render("PAUSED", True, WHITE),
                    (WIDTH // 2 - 120, 200))

        # Resume
        pygame.draw.rect(screen, GREEN, resume_button, border_radius=12)
        screen.blit(FONT.render("Resume", True, WHITE),
                    (resume_button.centerx - 40, resume_button.centery - 12))

        # Restart
        pygame.draw.rect(screen, BLUE, restart_button, border_radius=12)
        screen.blit(FONT.render("Restart Level", True, WHITE),
                    (restart_button.centerx - 65, restart_button.centery - 12))

        # Main Menu
        pygame.draw.rect(screen, RED, menu_button, border_radius=12)
        screen.blit(FONT.render("Main Menu", True, WHITE),
                    (menu_button.centerx - 55, menu_button.centery - 12))


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
            "Use arrow keys to move your agent.",
            "Collect encrypted tokens to unlock the portal.",
            "Avoid hostile spies at all costs.",
            "Report suspicious online behavior.",
            "Answer all quiz questions correctly to advance."
        ]

        for i, t in enumerate(tips):
            tip_text = FONT.render(t, True, WHITE)
            screen.blit(tip_text,
                        (WIDTH // 2 - tip_text.get_width() // 2,
                         220 + i * 50))

        # Back Button
        pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
        screen.blit(FONT.render("BACK", True, WHITE),
                    (back_button.centerx - 30,
                     back_button.centery - 12))

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
            dx,dy=e["dir"]
            e["rect"].x+=dx*e["speed"]
            e["rect"].y+=dy*e["speed"]

            if is_wall(e["rect"]):
                e["rect"].x-=dx*e["speed"]
                e["rect"].y-=dy*e["speed"]
                e["dir"]=random.choice([(1,0),(-1,0),(0,1),(0,-1)])

            screen.blit(bad_spy,
                e["rect"].move(offset_x,offset_y))

            if player.rect.colliderect(e["rect"]) and invincible_timer<=0:
                player.lives-=1
                invincible_timer=1.0
                if player.lives<=0:
                    state="game_over"

        if invincible_timer<=0 or int(invincible_timer*10)%2==0:
            screen.blit(good_spy,
                player.rect.move(offset_x,offset_y))

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
            ts = FONT.render(opt, True, WHITE)
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
        screen.blit(BIG_FONT.render("GAME OVER", True, WHITE),

                    (WIDTH // 2 - 140, 250))

        pygame.draw.rect(screen, GREEN, gameover_restart_button, border_radius=12)
        screen.blit(FONT.render("Restart Game", True, WHITE),
                    (gameover_restart_button.centerx - 70,
                     gameover_restart_button.centery - 12))

        pygame.draw.rect(screen, RED, gameover_quit_button, border_radius=12)

        screen.blit(FONT.render("Quit", True, WHITE),
                    (gameover_quit_button.centerx - 20,
                     gameover_quit_button.centery - 12))

    elif state=="game_complete":
        screen.fill((10,70,30))
        screen.blit(BIG_FONT.render("YOU SAVED CYBER CITY!",True,WHITE),
                    (WIDTH//2-250,300))

    pygame.display.flip()

pygame.quit()
sys.exit()