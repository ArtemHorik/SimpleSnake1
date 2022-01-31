import pygame as pg

import sys
import time
import random


class Game:
    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 460

    RED = pg.Color("indianred1")
    BLUE = pg.Color("cadetblue")
    DARK_BLUE = pg.Color("darkblue")
    GOLD = pg.Color("darkgoldenrod1")
    GREEN = pg.Color("green")
    BLACK = pg.Color("black")
    BROWN = pg.Color("chocolate")
    MAGENTA = pg.Color("darkmagenta")

    def __init__(self, fps: int):
        """Inits game with given FPS."""
        self.game_init()
        self.surface = pg.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
        pg.display.set_caption("SSnake")
        self.fps = fps  # Game's framerate
        self.fps_clock = pg.time.Clock()
        self.font_path = "data/fonts/Ozone.ttf"
        self.score = 0  # Player's score

    @staticmethod
    def game_init():
        """Inits pygame game"""
        errors = pg.init()
        if errors[1] > 1:
            sys.exit()
        else:
            print("No errors!")

    def refresh(self, fps: int):
        """ Refreshes the screen and sets the frame rate of the game.

            :param int fps: Game FPS
        """
        pg.display.flip()
        self.fps_clock.tick(fps)

    @staticmethod
    def keyboard_events_check():
        """ Responds to keyboard keystrokes.

            :return: "UP"|"DOWN"|"LEFT"|"RIGHT" direction for snake movement.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_RIGHT, pg.K_d):
                    return "RIGHT"
                elif event.key in (pg.K_LEFT, pg.K_a):
                    return "LEFT"
                elif event.key in (pg.K_UP, pg.K_w):
                    return "UP"
                elif event.key in (pg.K_DOWN, pg.K_s):
                    return "DOWN"
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

    def show_score(self, bg_color):
        """Renders player's score."""
        if self.score < 0:
            self.score = 0
        elif self.score >= 100:
            self.win()
        self.surface.fill(bg_color)
        font = pg.font.Font(self.font_path, 30)
        font_render = font.render(f"Score: {self.score:03}", True, Game.BLACK)
        font_rect = font_render.get_rect()
        font_rect.midbottom = (Game.SCREEN_WIDTH / 2, Game.SCREEN_HEIGHT / 5)
        self.surface.blit(font_render, font_rect)

    def win(self):
        """Tells player that he won. Closes the game after 5 seconds."""
        win_font = pg.font.Font(self.font_path, 100)
        font_render = win_font.render(f"YOU WON!", True, Game.RED)
        font_rect = font_render.get_rect()
        font_rect.midbottom = (Game.SCREEN_WIDTH / 2, Game.SCREEN_HEIGHT / 2)
        self.surface.blit(font_render, font_rect)
        pg.display.flip()
        time.sleep(5)
        pg.quit()
        sys.exit()

    def draw_snake(self, snake):
        """Draws a snake every frame.

        :param snake: Snake class
        """
        for pos in snake.body:
            pg.draw.rect(self.surface, snake.color,
                         pg.Rect(pos[0], pos[1], snake.WIDTH, snake.HEIGHT))

    def draw_food(self, foods, bg_color):
        # self.surface.fill(bg_color)
        for food in foods:
            for pos in food.positions:
                # if pos[0] > Game.SCREEN_WIDTH or pos[1] > Game.SCREEN_HEIGHT:
                #     food.create_food()
                pg.draw.rect(self.surface, food.color,
                             pg.Rect(pos[0], pos[1], food.WIDTH, food.HEIGHT))
        # if food.points != 1:
        #     food.change_color()


class Snake:
    # In pixels
    WIDTH = 10
    HEIGHT = 10
    MOVE = 10
    # FPS_LOCK = 10

    OPPOSITES = {"UP": "DOWN", "LEFT": "RIGHT"}  # Forbidden snake head moves

    def __init__(self, game: Game, snake_color):
        """
        Inits snake.

        :param game: Game class
        :param snake_color: Any pygame color object
        """
        self.game = game
        self.color = snake_color  # Any pygame color
        self.head_pos = [100, 50]  # [x, y]  Start position of snake
        self.head_x, self.head_y = self.head_pos[0], self.head_pos[1]
        self.body = [self.head_pos]
        self.length = 1  # Snake body length

        self.moves = {"UP": (0, -Snake.MOVE),
                      "DOWN": (0, Snake.MOVE),
                      "LEFT": (-Snake.MOVE, 0),
                      "RIGHT": (Snake.MOVE, 0)}
        self.direction = None  # At the start of the game snake doesn't move.

    def change_direction(self, new_direction: str):
        """
        Changes the direction of the snake.

        :param new_direction: "UP"|"DOWN"|"LEFT"|"RIGHT"
        """
        opposites = dict(Snake.OPPOSITES)
        opposites.update({v: k for k, v in Snake.OPPOSITES.items()})
        if self.direction != opposites[new_direction]:
            self.direction = new_direction

    def change_head_pos(self):
        """
        Changes snake head position.
        """
        if self.direction:
            for i, change in enumerate(self.moves[self.direction]):
                self.head_pos[i] += change

    def check_borders(self, screen_w, screen_h):
        """ Checks where snake head is.
            If it's out of the border, changes head position
            to the opposite border. If it's on a snake body -
            function cuts the tail.
        """
        x, y = self.head_pos[0], self.head_pos[1]
        if x >= screen_w:
            self.head_pos[0] = 0
        elif x < 0:
            self.head_pos[0] = screen_w
        elif y >= screen_h:
            self.head_pos[1] = 0
        elif y < 0:
            self.head_pos[1] = screen_h
        for i, pos in enumerate(self.body[1:]):
            if self.head_pos == pos:
                self.game.score -= len(self.body[i:])
                new_body = self.body[:i + 1]
                self.body = new_body
                self.length = len(new_body)

    def snake_mechanism(self, foods: tuple):
        """
        Make snake move and calls function to check
        if snake ate something.
        Takes tuple of food classes to check.

        :param foods: tuple of food classes
        """
        self.body.insert(0, list(self.head_pos))
        if len(self.body) >= self.length:
            self.body.pop()
        if self.length <= len(self.body):
            self.length += 1
        self._check_food(foods)

    def _check_food(self, foods: tuple):
        """
        Checks if head of a snake is at food position.

        :param foods: tuple of food classes
        """
        for food in foods:
            for pos in food.positions:
                if self.head_pos == pos:
                    food.delete_food(pos)
                    self.length += food.points
                    self.game.score += food.points
                    return

    def eat(self):
        self.length += 1


class Food:
    # In pixels
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, game, color, amount_at_start: int):
        """Inits food. Spawns given amount at start of the game.

        :param game: Main game class
        :param color: Any pygame color object
        """
        self.color = color
        self.positions = []  # [[x, y], [[x, y]] food positions
        self.amount = 0
        self.points = 1
        self.game = game
        for _ in range(amount_at_start):
            # Spawns food at the start of the game.
            self.create_food()

    def create_food(self):
        """Spawns food on random coordinates.
        """
        x = (random.randint(1, (self.game.SCREEN_WIDTH - 10) // 10) * 10)
        y = (random.randint(1, (self.game.SCREEN_HEIGHT - 10) // 10) * 10)
        self.positions.append([x, y])
        self.amount += 1

    def delete_food(self, pos: list):
        """Removes food from the given position."""
        self.positions.remove(pos)
        self.amount -= 1


class SuperFood(Food):
    COLOR_CHANGE_LIMIT = 2  # Frequency limit for color change

    def __init__(self, game, amount_at_start: int):
        """Inits superfood. Spawns given amount at start of the game.

        :param game: Main game class
        """
        self.colors = [game.DARK_BLUE, game.RED, game.BROWN, game.MAGENTA]
        self.color = random.choice(self.colors)
        super(SuperFood, self).__init__(game, self.color, amount_at_start)
        self.points = random.randint(5, 11)
        self.change_limit = SuperFood.COLOR_CHANGE_LIMIT

    def change_color(self):
        """ Changes SuperFood color randomly, with limited frequency.
        """
        if self.change_limit <= 0:
            rgb = [random.randint(1, 255) for _ in range(3)]
            self.color = pg.Color(*rgb)
            self.change_limit += SuperFood.COLOR_CHANGE_LIMIT
        self.change_limit -= 1


def main():
    game = Game(18)
    simple_food = Food(game, game.RED, 1)
    superfood = SuperFood(game, 0)
    all_food = (simple_food, superfood)
    snake = Snake(game, game.GREEN)
    bg_color = game.BLUE  # Background color
    game.game_init()

    superfood_counter = 30 * game.fps  # First SuperFood spawns after 30sec
    while True:
        direction = game.keyboard_events_check()
        if direction:  # Snake start moving
            snake.change_direction(direction)
        snake.change_head_pos()
        snake.check_borders(game.SCREEN_WIDTH, game.SCREEN_HEIGHT)
        snake.snake_mechanism(all_food)
        game.show_score(bg_color)
        if game.score >= 100:  # Player wins when reaches 100 points
            game.win()
        game.draw_snake(snake)
        superfood.change_color()

        if not simple_food.amount:
            simple_food.create_food()
        if superfood_counter == 0:  # When SuperFood counter reaches 0, spawns SuperFood
            superfood.create_food()
            # Sets superfood counter randomly from 30 to 100 seconds
            superfood_counter += random.randint(30 * game.fps, 100 * game.fps)
        superfood_counter -= 1
        game.draw_food(all_food, bg_color)

        game.refresh(game.fps)


if __name__ == "__main__":
    main()
