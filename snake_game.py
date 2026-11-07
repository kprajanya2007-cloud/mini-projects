import tkinter as tk
import random

# ---------- Settings ----------
CELL = 20                 # size of one square (pixels)
COLS = 24
ROWS = 24
START_DELAY = 140         # milliseconds per move (lower = faster)
MIN_DELAY = 60            # fastest speed
HS_FILE = "snake_highscore.txt"

DIRECTIONS = {
    "up": (0, -1), "w": (0, -1),
    "down": (0, 1), "s": (0, 1),
    "left": (-1, 0), "a": (-1, 0),
    "right": (1, 0), "d": (1, 0),
}


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("Snake Game")
        root.resizable(False, False)

        self.info = tk.StringVar()
        tk.Label(root, textvariable=self.info, font=("Arial", 13, "bold")).pack(pady=4)
        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg="#111111", highlightthickness=0)
        self.canvas.pack()

        self.high = self.load_high()
        self.job = None
        root.bind("<Key>", self.on_key)
        self.new_game()

    # ---------- High score ----------
    def load_high(self):
        try:
            with open(HS_FILE) as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def save_high(self):
        try:
            with open(HS_FILE, "w") as f:
                f.write(str(self.high))
        except Exception:
            pass

    # ---------- Game setup ----------
    def new_game(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        mx, my = COLS // 2, ROWS // 2
        self.snake = [(mx, my), (mx - 1, my), (mx - 2, my)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.delay = START_DELAY
        self.started = False
        self.paused = False
        self.over = False
        self.won = False
        self.place_food()
        self.refresh()

    def place_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in self.snake]
        if not free:
            self.food = None
            return
        self.food = random.choice(free)

    # ---------- Input ----------
    def on_key(self, event):
        k = event.keysym.lower()

        if k == "r" or (k == "space" and (self.over or self.won)):
            self.new_game()
            return
        if self.over or self.won:
            return
        if k == "p" and self.started:
            self.paused = not self.paused
            if not self.paused:
                self.schedule()
            self.refresh()
            return
        if k in DIRECTIONS and not self.paused:
            d = DIRECTIONS[k]
            # cannot reverse straight into yourself
            if (d[0] + self.dir[0], d[1] + self.dir[1]) != (0, 0):
                self.next_dir = d
                if not self.started:
                    self.started = True
                    self.schedule()

    # ---------- Game loop ----------
    def schedule(self):
        self.job = self.root.after(self.delay, self.step)

    def step(self):
        self.job = None
        if self.paused or self.over or self.won:
            return

        self.dir = self.next_dir
        hx, hy = self.snake[0]
        nx, ny = hx + self.dir[0], hy + self.dir[1]
        ate = (nx, ny) == self.food
        body = self.snake if ate else self.snake[:-1]

        # wall or self collision
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS or (nx, ny) in body:
            self.over = True
            if self.score > self.high:
                self.high = self.score
                self.save_high()
            self.refresh()
            return

        self.snake.insert(0, (nx, ny))
        if ate:
            self.score += 10
            self.delay = max(MIN_DELAY, self.delay - 4)   # speeds up
            self.place_food()
            if self.food is None:                          # board full
                self.won = True
                if self.score > self.high:
                    self.high = self.score
                    self.save_high()
                self.refresh()
                return
        else:
            self.snake.pop()

        self.refresh()
        self.schedule()

    # ---------- Drawing ----------
    def refresh(self):
        self.info.set(f"Score: {self.score}     High Score: {self.high}")
        c = self.canvas
        c.delete("all")

        if self.food:
            fx, fy = self.food
            c.create_oval(fx * CELL + 3, fy * CELL + 3,
                          fx * CELL + CELL - 3, fy * CELL + CELL - 3,
                          fill="#ff4d4d", outline="")

        for i, (x, y) in enumerate(self.snake):
            color = "#7CFC00" if i == 0 else "#2ecc40"
            c.create_rectangle(x * CELL + 1, y * CELL + 1,
                               x * CELL + CELL - 1, y * CELL + CELL - 1,
                               fill=color, outline="")

        cx, cy = COLS * CELL // 2, ROWS * CELL // 2
        if self.over:
            self.overlay("GAME OVER", f"Score: {self.score}\nPress SPACE or R to restart", cx, cy)
        elif self.won:
            self.overlay("YOU WIN!", "Board is full!\nPress SPACE or R to restart", cx, cy)
        elif self.paused:
            self.overlay("PAUSED", "Press P to continue", cx, cy)
        elif not self.started:
            self.overlay("SNAKE", "Press an arrow key or WASD to start", cx, cy)

    def overlay(self, title, text, cx, cy):
        c = self.canvas
        c.create_text(cx, cy - 25, text=title, fill="white", font=("Arial", 28, "bold"))
        c.create_text(cx, cy + 20, text=text, fill="#dddddd",
                      font=("Arial", 12), justify="center")


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()