import random
import sys
import pygame

# راه‌اندازی اولیه کتابخانه و پنجره بازی
pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 24
FPS = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# رنگ‌های مورد استفاده
BLACK = (0, 0, 0)
WHITE = (245, 245, 245)
RED = (230, 45, 45)
GREEN = (30, 190, 70)
BUTTON_COLOR = (45, 135, 75)
BUTTON_HOVER = (65, 165, 95)

# فونت ایموجی سیستم‌عامل برای نمایش میوه‌ها و مار
emoji_font = pygame.font.SysFont(
    ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "DejaVu Sans"],
    CELL_SIZE
)
score_font = pygame.font.SysFont("Arial", 27, bold=True)
button_font = pygame.font.SysFont("Arial", 25, bold=True)
game_over_font = pygame.font.SysFont("Arial", 58, bold=True)

# هر میوه امتیاز مخصوص خودش را دارد.
FRUITS = [
    ("🍏", 2),
    ("🍎", 4),
    ("🍉", 10),
    ("🍓", 15),
    ("🍌", 20),
    ("🍊", 25),
    ("🍑", 50),
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


def random_empty_position(occupied):
    """یک خانه خالی از صفحه برای قرار دادن میوه انتخاب می‌کند."""
    available = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    return random.choice(available) if available else None


def create_fruit(snake):
    """میوه تصادفی را همراه با امتیاز آن در محل خالی قرار می‌دهد."""
    fruit_type = random.choice(FRUITS)
    position = random_empty_position(snake)
    return position, fruit_type


def reset_game():
    """متغیرهای بازی را برای شروع یک دور جدید مقداردهی می‌کند."""
    global snake, direction, next_direction, score
    global fruit_position, fruit_type, state

    center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
    direction = RIGHT
    next_direction = RIGHT
    score = 0
    fruit_position, fruit_type = create_fruit(snake)
    state = STATE_PLAYING


def draw_button(rect, text):
    """دکمه را رسم می‌کند و هنگام قرار گرفتن ماوس روی آن رنگش تغییر می‌کند."""
    color = BUTTON_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)
    label = button_font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_snake():
    """بدنه مار را با ایموجی مربع سبز نمایش می‌دهد."""
    for segment in snake:
        x = segment[0] * CELL_SIZE
        y = segment[1] * CELL_SIZE
        image = emoji_font.render("🟩", True, GREEN)
        screen.blit(image, (x, y))


def draw_fruit():
    """ایموجی میوه انتخاب‌شده را در خانه مربوط به آن رسم می‌کند."""
    if fruit_position is None:
        return
    x = fruit_position[0] * CELL_SIZE
    y = fruit_position[1] * CELL_SIZE
    image = emoji_font.render(fruit_type[0], True, WHITE)
    screen.blit(image, (x, y))


def handle_direction_key(key):
    """جهت حرکت را تغییر می‌دهد؛ برگشت مستقیم به سمت مخالف مجاز نیست."""
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

    if requested_direction is not None:
        if requested_direction != OPPOSITE_DIRECTIONS[direction]:
            next_direction = requested_direction


def update_game():
    """حرکت مار، برخوردها، خوردن میوه و افزایش امتیاز را مدیریت می‌کند."""
    global snake, direction, next_direction
    global score, fruit_position, fruit_type, state

    direction = next_direction
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # برخورد با دیواره‌های صفحه
    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
        state = STATE_GAME_OVER
        return

    eating = new_head == fruit_position

    # اگر میوه خورده نشود، خانه دم در همین حرکت خالی خواهد شد.
    body_to_check = snake if eating else snake[:-1]
    if new_head in body_to_check:
        state = STATE_GAME_OVER
        return

    snake.insert(0, new_head)

    if eating:
        score += fruit_type[1]
        fruit_position, fruit_type = create_fruit(snake)
        if fruit_position is None:
            state = STATE_GAME_OVER
    else:
        snake.pop()


def draw_playing_screen():
    """صفحه بازی را با نمایش امتیاز، میوه و مار رسم می‌کند."""
    screen.fill(BLACK)
    score_image = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_image, (15, 12))
    draw_fruit()
    draw_snake()


def draw_menu():
    """صفحه شروع را با یک دکمه نمایش می‌دهد."""
    screen.fill(BLACK)
    draw_button(start_button, "START")


def draw_game_over():
    """پیام پایان بازی و دکمه شروع دوباره را نمایش می‌دهد."""
    screen.fill(BLACK)
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
