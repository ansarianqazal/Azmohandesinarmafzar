import os
import random
import sys
import time
from contextlib import contextmanager

# اندازه زمین بازی در ترمینال
WIDTH = 36
HEIGHT = 16
GAME_SPEED = 0.14

# رنگ‌ها با کد ANSI؛ در ترمینال‌های جدید ویندوز و لینوکس نمایش داده می‌شوند.
RESET = "\033[0m"
GREEN = "\033[92m"
DARK_GREEN = "\033[32m"
ORANGE = "\033[38;5;208m"
GOLD = "\033[38;5;220m"
BROWN = "\033[38;5;94m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
CYAN = "\033[96m"
GRAY = "\033[90m"

# حیوانات؛ هر بار که حیوان جدیدی ظاهر می‌شود امتیاز آن تصادفی است.
ANIMALS = [
    {"symbol": "M", "name": "Mouse", "min_score": 5, "max_score": 15},
    {"symbol": "R", "name": "Rabbit", "min_score": 10, "max_score": 25},
    {"symbol": "F", "name": "Frog", "min_score": 8, "max_score": 20},
    {"symbol": "B", "name": "Bird", "min_score": 12, "max_score": 30},
    {"symbol": "C", "name": "Chicken", "min_score": 15, "max_score": 35},
    {"symbol": "T", "name": "Turtle", "min_score": 20, "max_score": 40},
    {"symbol": "L", "name": "Lizard", "min_score": 18, "max_score": 38},
    {"symbol": "S", "name": "Big Snake", "min_score": 60, "max_score": 100},
]

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def clear_screen():
    """صفحه ترمینال را پاک می‌کند و مکان‌نما را به ابتدا می‌برد."""
    print("\033[2J\033[H", end="")


@contextmanager
def keyboard_reader():
    """خواندن کلیدها بدون نیاز به فشردن Enter؛ برای ویندوز و لینوکس."""
    if os.name == "nt":
        import msvcrt

        class WindowsReader:
            def read_key(self):
                if not msvcrt.kbhit():
                    return None
                key = msvcrt.getwch()
                if key in ("\x00", "\xe0"):
                    code = msvcrt.getwch()
                    return {
                        "H": "UP", "P": "DOWN",
                        "K": "LEFT", "M": "RIGHT"
                    }.get(code)
                return key.lower()

        yield WindowsReader()
    else:
        import select
        import termios
        import tty

        class UnixReader:
            def __init__(self):
                self.fd = sys.stdin.fileno()
                self.old_settings = termios.tcgetattr(self.fd)
                tty.setcbreak(self.fd)

            def read_key(self):
                ready, _, _ = select.select([sys.stdin], [], [], 0)
                if not ready:
                    return None
                key = sys.stdin.read(1)
                if key == "\x1b":
                    # دریافت کلیدهای جهت‌دار در ترمینال‌های لینوکس و macOS
                    ready, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if ready and sys.stdin.read(1) == "[":
                        ready, _, _ = select.select([sys.stdin], [], [], 0.01)
                        if ready:
                            return {
                                "A": "UP", "B": "DOWN",
                                "D": "LEFT", "C": "RIGHT"
                            }.get(sys.stdin.read(1))
                    return None
                return key.lower()

            def close(self):
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

        reader = UnixReader()
        try:
            yield reader
        finally:
            reader.close()


def random_empty_position(snake):
    """یک موقعیت خالی برای قرار دادن حیوان پیدا می‌کند."""
    free_cells = [
        (x, y)
        for y in range(HEIGHT)
        for x in range(WIDTH)
        if (x, y) not in snake
    ]
    return random.choice(free_cells) if free_cells else None


def create_animal(snake):
    """حیوان و امتیاز تصادفی آن را ایجاد می‌کند."""
    animal = random.choice(ANIMALS).copy()
    animal["score"] = random.randint(animal["min_score"], animal["max_score"])
    return random_empty_position(snake), animal


def reset_game():
    """وضعیت بازی را از ابتدا تنظیم می‌کند."""
    center = (WIDTH // 2, HEIGHT // 2)
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
    return snake, direction, next_direction, score, animal_position, current_animal


def draw_board(snake, animal_position, current_animal, score):
    """زمین چمنی، مار، حیوان و امتیاز را در ترمینال چاپ می‌کند."""
    board = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
    colors = [[GREEN for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # بافت ساده چمن با نقطه‌های پراکنده
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x * 7 + y * 11) % 19 == 0:
                board[y][x] = "."

    # حیوان هدف
    if animal_position is not None:
        ax, ay = animal_position
        board[ay][ax] = current_animal["symbol"]
        colors[ay][ax] = YELLOW if current_animal["symbol"] != "S" else RED

    # بدن و سر مار
    for index, (x, y) in enumerate(snake):
        board[y][x] = "@" if index == 0 else "o"
        colors[y][x] = GOLD if index == 0 else ORANGE

    clear_screen()
    print(f"{GREEN}╔" + "═" * WIDTH + f"╗{RESET}")
    for y in range(HEIGHT):
        line = f"{GREEN}║{RESET}"
        for x in range(WIDTH):
            char = board[y][x]
            color = colors[y][x]
            if char == ".":
                color = DARK_GREEN
            line += f"{color}{char}{RESET}"
        line += f"{GREEN}║{RESET}"
        print(line)
    print(f"{GREEN}╚" + "═" * WIDTH + f"╝{RESET}")
    print(f"{WHITE}Score: {score}{RESET}    "
          f"{YELLOW}Target: {current_animal['name']} "
          f"(+{current_animal['score']} points){RESET}")
    print(f"{GRAY}@ = Snake head   o = Snake body   "
          f"{YELLOW}{current_animal['symbol']} = Target animal{RESET}")


def show_menu():
    """منوی آغاز بازی را در ترمینال نمایش می‌دهد."""
    clear_screen()
    print(f"{GREEN}")
    print("  SNAKE GAME - TERMINAL EDITION")
    print("  " + "=" * 32)
    print(f"{RESET}")
    print(f"{ORANGE}       /\/\")
    print("      ( o  o )")
    print(f"       \_==_/ {RESET}")
    print()
    print(f"{WHITE}  The snake is hungry! Find the animals.{RESET}")
    print()
    print(f"{CYAN}  Controls: Arrow keys or W A S D{RESET}")
    print(f"{CYAN}  Press ENTER to start, Q to quit.{RESET}")
    print()


def show_game_over(score):
    """صفحه پایان بازی و امتیاز نهایی را نمایش می‌دهد."""
    clear_screen()
    print(f"{RED}")
    print("  ╔══════════════════════════════╗")
    print("  ║          GAME OVER           ║")
    print("  ╚══════════════════════════════╝")
    print(f"{RESET}")
    print(f"{WHITE}  Final score: {GOLD}{score}{RESET}")
    print()
    print(f"{CYAN}  Press R to play again or Q to quit.{RESET}")


def change_direction(key, direction, next_direction):
    """جهت مار را تغییر می‌دهد و جلوی برگشت مستقیم را می‌گیرد."""
    key_directions = {
        "w": UP, "s": DOWN, "a": LEFT, "d": RIGHT,
        "UP": UP, "DOWN": DOWN, "LEFT": LEFT, "RIGHT": RIGHT,
    }
    requested = key_directions.get(key)
    if (requested is not None
            and next_direction == direction
            and requested != OPPOSITE[direction]):
        return requested
    return next_direction


def update_game(snake, direction, next_direction, score,
                animal_position, current_animal):
    """حرکت، برخورد، خوردن حیوان و امتیازگیری را مدیریت می‌کند."""
    direction = next_direction
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # برخورد با دیواره
    if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
        return snake, direction, score, animal_position, current_animal, False

    eating = new_head == animal_position
    body_to_check = snake if eating else snake[:-1]

    # برخورد با بدن خود مار
    if new_head in body_to_check:
        return snake, direction, score, animal_position, current_animal, False

    snake.insert(0, new_head)

    if eating:
        score += current_animal["score"]
        animal_position, current_animal = create_animal(snake)
        if animal_position is None:
            return snake, direction, score, animal_position, current_animal, False
    else:
        snake.pop()

    return snake, direction, score, animal_position, current_animal, True


def play_game(reader):
    """حلقه اصلی بازی؛ حرکت خودکار است و ورودی‌ها بدون Enter خوانده می‌شوند."""
    (snake, direction, next_direction, score,
     animal_position, current_animal) = reset_game()

    running = True
    while running:
        key = reader.read_key()
        if key in ("q", "\x1b"):
            return "quit", score
        if key is not None:
            next_direction = change_direction(key, direction, next_direction)

        (snake, direction, score, animal_position,
         current_animal, alive) = update_game(
            snake, direction, next_direction, score,
            animal_position, current_animal
        )

        draw_board(snake, animal_position, current_animal, score)
        if not alive:
            return "game_over", score

        time.sleep(GAME_SPEED)

    return "quit", score


def main():
    """اجرای منو، بازی و امکان شروع دوباره."""
    try:
        with keyboard_reader() as reader:
            while True:
                show_menu()
                while True:
                    key = reader.read_key()
                    if key == "q":
                        clear_screen()
                        print("Thanks for playing!")
                        return
                    if key in ("\r", "\n"):
                        break
                    time.sleep(0.05)

                result, final_score = play_game(reader)
                if result == "quit":
                    clear_screen()
                    print("Game closed.")
                    return

                show_game_over(final_score)
                while True:
                    key = reader.read_key()
                    if key == "q":
                        clear_screen()
                        print("Thanks for playing!")
                        return
                    if key == "r":
                        break
                    time.sleep(0.05)
    except (KeyboardInterrupt, EOFError):
        clear_screen()
        print("Game interrupted. Goodbye!")


if __name__ == "__main__":
    main()
