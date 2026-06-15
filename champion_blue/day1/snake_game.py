"""
<prompt>
  <task>
    파이썬으로 기본 내장 라이브러리만 이용해서 지렁이 게임 코드를 작성해줘.
  </task>
</prompt>
"""

import tkinter as tk
import random


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
GAME_SPEED = 100

WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("지렁이 게임")

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="black"
        )
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.change_direction)

        self.reset_game()
        self.game_loop()

    def reset_game(self):
        self.snake = [
            [GRID_WIDTH // 2, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
            [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2],
        ]

        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.game_over = False

        self.food = self.create_food()

    def create_food(self):
        while True:
            food = [
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            ]

            if food not in self.snake:
                return food

    def change_direction(self, event):
        key = event.keysym

        opposite = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }

        if key in opposite and opposite[key] != self.direction:
            self.next_direction = key

    def move_snake(self):
        self.direction = self.next_direction

        head_x, head_y = self.snake[0]

        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1

        new_head = [head_x, head_y]

        if (
            head_x < 0 or
            head_x >= GRID_WIDTH or
            head_y < 0 or
            head_y >= GRID_HEIGHT or
            new_head in self.snake
        ):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.create_food()
        else:
            self.snake.pop()

    def draw(self):
        self.canvas.delete("all")

        self.canvas.create_text(
            60,
            15,
            text=f"Score: {self.score}",
            fill="white",
            font=("Arial", 14)
        )

        food_x = self.food[0] * CELL_SIZE
        food_y = self.food[1] * CELL_SIZE

        self.canvas.create_oval(
            food_x,
            food_y,
            food_x + CELL_SIZE,
            food_y + CELL_SIZE,
            fill="red"
        )

        for index, part in enumerate(self.snake):
            x = part[0] * CELL_SIZE
            y = part[1] * CELL_SIZE

            color = "lime" if index == 0 else "green"

            self.canvas.create_rectangle(
                x,
                y,
                x + CELL_SIZE,
                y + CELL_SIZE,
                fill=color,
                outline="black"
            )

        if self.game_over:
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 - 20,
                text="GAME OVER",
                fill="white",
                font=("Arial", 28, "bold")
            )

            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 20,
                text="Press R to Restart",
                fill="white",
                font=("Arial", 16)
            )

    def game_loop(self):
        if not self.game_over:
            self.move_snake()

        self.draw()

        self.root.after(GAME_SPEED, self.game_loop)


def restart_game(event, game):
    if event.keysym.lower() == "r":
        game.reset_game()


root = tk.Tk()
game = SnakeGame(root)

root.bind("<KeyPress-r>", lambda event: restart_game(event, game))
root.bind("<KeyPress-R>", lambda event: restart_game(event, game))

root.mainloop()
