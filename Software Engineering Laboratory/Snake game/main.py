import random
import sys
import pygame

# راه‌اندازی اولیه بازی
pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 24
FPS = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
RED = (230, 45, 45)
BUTTON_COLOR = (45, 135, 75)
BUTTON_HOVER = (65, 165, 95)

# فونت‌ها
emoji_font = pygame.font.SysFont(
    ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "DejaVu Sans"],
    28
)
big_emoji_font = pygame.font.SysFont(
    ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "DejaVu Sans"],
    44
)
score_font = pygame.font.SysFont("Arial", 27, bold=True)
button_font = pygame.font.SysFont("Arial", 25, bold=True)
game_over_font = pygame.font.SysFont("Arial", 58, bold=True)

# ساخت پس‌زمینه چمنی با جزئیات ثابت؛ با هر فریم دوباره محاسبه نمی‌شود.
def create_grass_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((48, 112, 52))
    texture_random = random.Random(24)

    # لکه‌های بسیار ملایم برای طبیعی‌تر شدن سطح چمن
    for _ in range(95):
        x = texture_random.randrange(WIDTH)
        y = texture_random.randrange(HEIGHT)
        radius = texture_random.randrange(8, 24)
        shade = texture_random.choice([
            (53, 121, 56), (43, 103, 47), (61, 126, 60)
        ])
        pygame.draw.circle(background, shade, (x, y), radius)

    # تیغه‌های کوتاه چمن
    for _ in range(650):
        x = texture_random.randrange(8, WIDTH - 8)
        y = texture_random.randrange(8, HEIGHT - 8)
        shade = texture_random.choice([
            (91, 151, 72), (75, 139, 65), (37, 91, 43)
        ])
        pygame.draw.line(background, shade, (x, y), (x + 2, y - 4), 1)

    # چند سنگ‌ریزه و تکه خاک کوچک
    for _ in range(55):
        x = texture_random.randrange(8, WIDTH - 8)
        y = texture_random.randrange(8, HEIGHT - 8)
        color = texture_random.choice([
            (115, 91, 58), (137, 112, 73), (94, 85, 63)
        ])
        pygame.draw.circle(background, color, (x, y), 2)

    # قاب ظریف دور محوطه بازی
    pygame.draw.rect(background, (25, 72, 35), (2, 2, WIDTH - 4, HEIGHT - 4), 5)
    pygame.draw.rect(background, (120, 163, 91), (7, 7, WIDTH - 14, HEIGHT - 14), 1)
    return background


grass_background = create_grass_background()


def draw_background():
    """پس‌زمینه چمنی آماده را روی صفحه قرار می‌دهد."""
    screen.blit(grass_background, (0, 0))

# حیوانات قابل شکار؛ امتیاز هر بار که حیوان ظاهر می‌شود تصادفی تعیین می‌شود.
# مار ویژه بزرگ‌تر نمایش داده می‌شود و امتیاز بیشتری دارد.
ANIMALS = [
    {"emoji": "🐭", "name": "Mouse", "min_score": 5, "max_score": 15, "large": False},
    {"emoji": "🐰", "name": "Rabbit", "min_score": 10, "max_score": 25, "large": False},
    {"emoji": "🐸", "name": "Frog", "min_score": 8, "max_score": 20, "large": False},
    {"emoji": "🐦", "name": "Bird", "min_score": 12, "max_score": 30, "large": False},
    {"emoji": "🐔", "name": "Chicken", "min_score": 15, "max_score": 35, "large": False},
    {"emoji": "🐢", "name": "Turtle", "min_score": 20, "max_score": 40, "large": False},
    {"emoji": "🦎", "name": "Lizard", "min_score": 18, "max_score": 38, "large": False},
    {"emoji": "🐍", "name": "Big Snake", "min_score": 60, "max_score": 100, "large": True},
]

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 28, 200, 56)

# مقدار اولیه وضعیت بازی؛ از بروز NameError در صفحه شروع جلوگیری می‌کند.
state = STATE_MENU


def random_empty_position(occupied):
    """یک خانه خالی برای قرار دادن حیوان انتخاب می‌کند."""
    available = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    return random.choice(available) if available else None


def create_animal(snake_body):
    """یک حیوان تصادفی با امتیاز تصادفی در صفحه قرار می‌دهد."""
    animal = random.choice(ANIMALS).copy()
    animal["score"] = random.randint(animal["min_score"], animal["max_score"])
    position = random_empty_position(snake_body)
    return position, animal


def reset_game():
    """متغیرهای بازی را برای شروع یک دور جدید مقداردهی می‌کند."""
    global snake, direction, next_direction, score
    global animal_position, current_animal, state

    center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    snake = [
        center,
        (center[0] - 1, center[1]),
        (center[0] - 2, center[1]),
        (center[0] - 3, center[1]),
    ]
    direction = RIGHT
    next_direction = RIGHT
    score = 0
    animal_position, current_animal = create_animal(snake)
    state = STATE_PLAYING


def draw_button(rect, text):
    """دکمه را رسم می‌کند و هنگام قرار گرفتن ماوس روی آن رنگش تغییر می‌کند."""
    color = BUTTON_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)
    label = button_font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def cell_center(segment):
    """مرکز پیکسلی یک خانه از صفحه را برمی‌گرداند."""
    return (
        segment[0] * CELL_SIZE + CELL_SIZE // 2,
        segment[1] * CELL_SIZE + CELL_SIZE // 2,
    )


def draw_snake():
    """مار را با بدن پیوسته، قطعه‌های گرد، فلس، چشم و زبان رسم می‌کند."""
    centers = [cell_center(part) for part in snake]

    # بدن اصلی؛ خط ضخیم باعث می‌شود قطعه‌ها به هم متصل دیده شوند.
    if len(centers) > 1:
        pygame.draw.lines(screen, (24, 105, 48), False, centers[::-1], 20)
        pygame.draw.lines(screen, (65, 170, 82), False, centers[::-1], 15)

    # حلقه‌های بدن و فلس‌های کوچک
    for index, center in enumerate(centers[1:], start=1):
        pygame.draw.circle(screen, (35, 135, 60), center, 10)
        pygame.draw.circle(screen, (90, 190, 100), center, 7)
        if index % 2 == 0:
            pygame.draw.circle(
                screen, (25, 100, 45),
                (center[0], center[1] - 2), 2
            )

    # سر مار
    head = centers[0]
    pygame.draw.circle(screen, (30, 145, 58), head, 12)
    pygame.draw.circle(screen, (90, 195, 95), head, 9)

    # جای چشم‌ها با توجه به جهت حرکت تعیین می‌شود.
    dx, dy = direction
    if direction in (RIGHT, LEFT):
        eye_x = head[0] + (4 if dx > 0 else -4)
        eye_positions = [(eye_x, head[1] - 5), (eye_x, head[1] + 5)]
    else:
        eye_y = head[1] + (4 if dy > 0 else -4)
        eye_positions = [(head[0] - 5, eye_y), (head[0] + 5, eye_y)]

    for eye in eye_positions:
        pygame.draw.circle(screen, WHITE, eye, 3)
        pygame.draw.circle(screen, BLACK, eye, 1)

    # زبان دوشاخه کوچک در جلوی سر
    tongue_start = (head[0] + dx * 10, head[1] + dy * 10)
    tongue_end = (head[0] + dx * 16, head[1] + dy * 16)
    pygame.draw.line(screen, RED, tongue_start, tongue_end, 2)
    if direction in (UP, DOWN):
        pygame.draw.line(
            screen, RED,
            tongue_end, (tongue_end[0] - 3, tongue_end[1] + dy * 3), 1
        )
        pygame.draw.line(
            screen, RED,
            tongue_end, (tongue_end[0] + 3, tongue_end[1] + dy * 3), 1
        )
    else:
        pygame.draw.line(
            screen, RED,
            tongue_end, (tongue_end[0] + dx * 3, tongue_end[1] - 3), 1
        )
        pygame.draw.line(
            screen, RED,
            tongue_end, (tongue_end[0] + dx * 3, tongue_end[1] + 3), 1
        )


def draw_animal():
    """حیوان هدف را نمایش می‌دهد؛ مار ویژه با اندازه بزرگ‌تر رسم می‌شود."""
    if animal_position is None:
        return

    center = cell_center(animal_position)
    font = big_emoji_font if current_animal["large"] else emoji_font
    image = font.render(current_animal["emoji"], True, WHITE)
    screen.blit(image, image.get_rect(center=center))


def handle_direction_key(key):
    """جهت حرکت را تغییر می‌دهد و از برگشت ناگهانی به عقب جلوگیری می‌کند."""
    global next_direction

    requested_direction = None
    if key in (pygame.K_UP, pygame.K_w):
        requested_direction = UP
    elif key in (pygame.K_DOWN, pygame.K_s):
        requested_direction = DOWN
    elif key in (pygame.K_LEFT, pygame.K_a):
        requested_direction = LEFT
    elif key in (pygame.K_RIGHT, pygame.K_d):
        requested_direction = RIGHT

    # در هر حرکت فقط یک تغییر جهت پذیرفته می‌شود تا مار نتواند دور بزند.
    if (
        requested_direction is not None
        and next_direction == direction
        and requested_direction != OPPOSITE_DIRECTIONS[direction]
    ):
        next_direction = requested_direction


def update_game():
    """حرکت مار، برخوردها، خوردن حیوان و افزایش امتیاز را مدیریت می‌کند."""
    global snake, direction, next_direction
    global score, animal_position, current_animal, state

    direction = next_direction
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # برخورد با دیواره‌های صفحه
    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
        state = STATE_GAME_OVER
        return

    eating = new_head == animal_position

    # اگر حیوان خورده نشود، خانه دم در همین حرکت خالی خواهد شد.
    body_to_check = snake if eating else snake[:-1]
    if new_head in body_to_check:
        state = STATE_GAME_OVER
        return

    snake.insert(0, new_head)

    if eating:
        score += current_animal["score"]
        animal_position, current_animal = create_animal(snake)
        if animal_position is None:
            state = STATE_GAME_OVER
    else:
        snake.pop()


def draw_playing_screen():
    """صفحه بازی را با نمایش امتیاز، حیوان و مار رسم می‌کند."""
    draw_background()
    score_image = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_image, (15, 12))
    draw_animal()
    draw_snake()


def draw_menu():
    """صفحه شروع را با یک دکمه نمایش می‌دهد."""
    draw_background()
    draw_button(start_button, "START")


def draw_game_over():
    """پیام پایان بازی و دکمه شروع دوباره را نمایش می‌دهد."""
    draw_background()
    # پنل تیره نیمه‌شفاف برای خوانایی پیام پایان بازی
    panel = pygame.Surface((460, 190), pygame.SRCALPHA)
    panel.fill((18, 48, 25, 215))
    screen.blit(panel, panel.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    message = game_over_font.render("GAME OVER", True, RED)
    screen.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 65)))
    button = pygame.Rect(WIDTH // 2 - 115, HEIGHT // 2 + 15, 230, 56)
    draw_button(button, "START AGAIN")
    return button


def main():
    global state

    game_over_button = pygame.Rect(
        WIDTH // 2 - 115, HEIGHT // 2 + 15, 230, 56
    )
    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, 1000 // FPS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == STATE_MENU and start_button.collidepoint(event.pos):
                    reset_game()
                elif state == STATE_GAME_OVER and game_over_button.collidepoint(event.pos):
                    reset_game()

            elif event.type == pygame.KEYDOWN and state == STATE_PLAYING:
                handle_direction_key(event.key)

            elif event.type == move_event and state == STATE_PLAYING:
                update_game()

        if state == STATE_MENU:
            draw_menu()
        elif state == STATE_PLAYING:
            draw_playing_screen()
        else:
            game_over_button = draw_game_over()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
