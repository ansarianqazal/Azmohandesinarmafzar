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
    """مار را با بدن فلس‌دار و بندبند، سر پهن و دم باریک رسم می‌کند."""
    centers = [cell_center(part) for part in snake]
    if not centers:
        return

    # هر قطعه بدن به شکل بیضی مستقل رسم می‌شود تا ظاهر کرمی و یک‌تکه نداشته باشد.
    # جهت هر قطعه از موقعیت قطعه بعدی به دست می‌آید.
    for index in range(len(centers) - 1, 0, -1):
        x, y = centers[index]
        previous = centers[index - 1]
        vx = previous[0] - x
        vy = previous[1] - y

        # دم به‌تدریج باریک می‌شود.
        taper = max(0.42, 1.0 - (index / max(1, len(centers))) * 0.48)
        half_w = int(9 * taper)
        half_h = int(8 * taper)
        if abs(vx) >= abs(vy):
            body_rect = pygame.Rect(0, 0, CELL_SIZE - 3, max(8, half_h * 2))
        else:
            body_rect = pygame.Rect(0, 0, max(8, half_w * 2), CELL_SIZE - 3)
        body_rect.center = (x, y)

        # سایه و رنگ اصلی بدن
        pygame.draw.ellipse(screen, (83, 35, 24), body_rect.inflate(2, 2))
        pygame.draw.ellipse(screen, (190, 91, 34), body_rect)

        # فلس‌های مورب تیره روی هر بند
        scale_color = (105, 48, 28)
        if abs(vx) >= abs(vy):
            pygame.draw.line(screen, scale_color, (x - 3, y - 5), (x + 1, y + 5), 2)
            pygame.draw.line(screen, (255, 181, 83), (x - 7, y - 3), (x - 4, y + 3), 1)
        else:
            pygame.draw.line(screen, scale_color, (x - 5, y - 2), (x + 5, y + 2), 2)
            pygame.draw.line(screen, (255, 181, 83), (x - 3, y - 6), (x + 3, y - 4), 1)

    # گردن کوتاه و کمی باریک‌تر، برای جدا شدن بصری سر از بدن
    head_x, head_y = centers[0]
    neck = centers[1] if len(centers) > 1 else (
        head_x - direction[0] * CELL_SIZE,
        head_y - direction[1] * CELL_SIZE
    )
    pygame.draw.line(screen, (105, 43, 23), neck, (head_x, head_y), 15)
    pygame.draw.line(screen, (205, 105, 39), neck, (head_x, head_y), 11)

    # سر پهن و لوزی‌مانند؛ نوک سر در جهت حرکت قرار می‌گیرد.
    dx, dy = direction
    if direction == RIGHT:
        head_points = [(head_x + 14, head_y), (head_x + 5, head_y - 11),
                       (head_x - 9, head_y - 9), (head_x - 12, head_y),
                       (head_x - 9, head_y + 9), (head_x + 5, head_y + 11)]
        eyes = [(head_x + 2, head_y - 6), (head_x + 2, head_y + 6)]
    elif direction == LEFT:
        head_points = [(head_x - 14, head_y), (head_x - 5, head_y - 11),
                       (head_x + 9, head_y - 9), (head_x + 12, head_y),
                       (head_x + 9, head_y + 9), (head_x - 5, head_y + 11)]
        eyes = [(head_x - 2, head_y - 6), (head_x - 2, head_y + 6)]
    elif direction == UP:
        head_points = [(head_x, head_y - 14), (head_x - 11, head_y - 5),
                       (head_x - 9, head_y + 9), (head_x, head_y + 12),
                       (head_x + 9, head_y + 9), (head_x + 11, head_y - 5)]
        eyes = [(head_x - 6, head_y - 2), (head_x + 6, head_y - 2)]
    else:
        head_points = [(head_x, head_y + 14), (head_x - 11, head_y + 5),
                       (head_x - 9, head_y - 9), (head_x, head_y - 12),
                       (head_x + 9, head_y - 9), (head_x + 11, head_y + 5)]
        eyes = [(head_x - 6, head_y + 2), (head_x + 6, head_y + 2)]

    pygame.draw.polygon(screen, (83, 35, 24), head_points)
    inner_points = [(head_x + int((px - head_x) * 0.88),
                     head_y + int((py - head_y) * 0.88))
                    for px, py in head_points]
    pygame.draw.polygon(screen, (225, 132, 54), inner_points)
    pygame.draw.polygon(screen, (255, 190, 105), head_points, 1)

    # چشم‌های جانبی و مردمک عمودی، شبیه مار
    for ex, ey in eyes:
        pygame.draw.circle(screen, (255, 238, 190), (ex, ey), 3)
        pygame.draw.ellipse(screen, (25, 20, 16), (ex - 1, ey - 2, 2, 4))

    # زبان قرمز دوشاخه در جلوی پوزه
    tongue_start = (head_x + dx * 11, head_y + dy * 11)
    tongue_tip = (head_x + dx * 19, head_y + dy * 19)
    pygame.draw.line(screen, (190, 25, 35), tongue_start, tongue_tip, 2)
    if dx:
        pygame.draw.line(screen, (190, 25, 35), tongue_tip,
                         (tongue_tip[0] + dx * 4, tongue_tip[1] - 3), 2)
        pygame.draw.line(screen, (190, 25, 35), tongue_tip,
                         (tongue_tip[0] + dx * 4, tongue_tip[1] + 3), 2)
    else:
        pygame.draw.line(screen, (190, 25, 35), tongue_tip,
                         (tongue_tip[0] - 3, tongue_tip[1] + dy * 4), 2)
        pygame.draw.line(screen, (190, 25, 35), tongue_tip,
                         (tongue_tip[0] + 3, tongue_tip[1] + dy * 4), 2)


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
