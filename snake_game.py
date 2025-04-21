import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        if self.next_direction:
            self.direction = self.next_direction
        head = self.get_head_position()
        x, y = self.direction
        new_position = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        if new_position in self.positions[1:]:
            return False  # Game over
        
        self.positions.insert(0, new_position)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.score += 1
        return True

    def grow_snake(self):
        self.grow = True

    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            color = DARK_GREEN if i == 0 else GREEN
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    snake = Snake()
    food = Food()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if game_over:
                    if event.key == K_SPACE:
                        snake = Snake()
                        food = Food()
                        game_over = False
                else:
                    if event.key == K_UP:
                        snake.change_direction(UP)
                    elif event.key == K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == K_RIGHT:
                        snake.change_direction(RIGHT)

        if not game_over:
            if not snake.update():
                game_over = True

            if snake.get_head_position() == food.position:
                snake.grow_snake()
                food.randomize_position()
                while food.position in snake.positions:
                    food.randomize_position()

        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        if game_over:
            game_over_text = font.render("Game Over! Press SPACE to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

        score_text = font.render(f"Score: {snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 