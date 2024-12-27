import pygame
import random
import sys
import json
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 120

# Colors
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
GRAVITY = 0.375
JUMP_SPEED = -9
PIPE_SPEED = 3
PIPE_GAP = 200
PIPE_FREQUENCY = 1500

class Bird:
    def __init__(self):
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.size = 25
        
    def jump(self):
        self.velocity = JUMP_SPEED
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.velocity > 8:
            self.velocity = 8
        elif self.velocity < -8:
            self.velocity = -8
        
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.size, self.size))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(150, 400)
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.height + PIPE_GAP, 50, WINDOW_HEIGHT))
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, 50, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('Retro Flappy Bird')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.load_highscore()
        self.reset_game()

    def load_highscore(self):
        try:
            with open('highscore.json', 'r') as f:
                self.highscore = json.load(f)['highscore']
        except:
            self.highscore = 0

    def save_highscore(self):
        with open('highscore.json', 'w') as f:
            json.dump({'highscore': self.highscore}, f)

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_active = False
        self.last_pipe = pygame.time.get_ticks()

    def show_menu(self):
        while True:
            self.screen.fill(SKY_BLUE)
            
            # Draw buttons
            play_button = pygame.draw.rect(self.screen, GREEN, (300, 200, 200, 50))
            instructions_button = pygame.draw.rect(self.screen, GREEN, (300, 300, 200, 50))
            exit_button = pygame.draw.rect(self.screen, GREEN, (300, 400, 200, 50))
            
            # Draw text
            self.draw_text('PLAY', 350, 215)
            self.draw_text('INSTRUCTIONS', 320, 315)
            self.draw_text('EXIT', 370, 415)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if play_button.collidepoint(mouse_pos):
                        return 'play'
                    elif instructions_button.collidepoint(mouse_pos):
                        self.show_instructions()
                    elif exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
            
            pygame.display.update()
            self.clock.tick(FPS)

    def show_instructions(self):
        waiting = True
        while waiting:
            self.screen.fill(SKY_BLUE)
            self.draw_text('HOW TO PLAY', 320, 100)
            self.draw_text('Press SPACE to make the bird jump', 250, 200)
            self.draw_text('Avoid the pipes and collect points', 250, 250)
            self.draw_text('Each pipe passed = 1 point', 250, 300)
            self.draw_text('Press any key to return', 250, 400)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waiting = False
                    
            pygame.display.update()
            self.clock.tick(FPS)

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, BLACK)
        self.screen.blit(text_surface, (x, y))

    def run(self):
        while True:
            if self.show_menu() == 'play':
                self.game_loop()

    def show_game_over(self):
        waiting = True
        while waiting:
            self.screen.fill(SKY_BLUE)
            self.draw_text('GAME OVER', 320, 200)
            self.draw_text(f'Score: {self.score}', 350, 250)
            self.draw_text(f'High Score: {self.highscore}', 320, 300)
            self.draw_text('Press any key to continue', 280, 400)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waiting = False
                    
            pygame.display.update()
            self.clock.tick(FPS)

    def game_loop(self):
        self.game_active = True
        
        while self.game_active:
            self.clock.tick_busy_loop(FPS)
            current_time = pygame.time.get_ticks()
            
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.bird.jump()

            # Spawn pipes
            if current_time - self.last_pipe > PIPE_FREQUENCY:
                self.pipes.append(Pipe(WINDOW_WIDTH))
                self.last_pipe = current_time

            # Update
            self.bird.update()
            for pipe in self.pipes:
                pipe.update()
                
                # Check for point scoring
                if not pipe.passed and pipe.x < self.bird.x:
                    self.score += 1
                    pipe.passed = True
                    if self.score > self.highscore:
                        self.highscore = self.score
                        self.save_highscore()

            # Remove off-screen pipes
            self.pipes = [pipe for pipe in self.pipes if pipe.x > -60]

            # Check collisions
            if self.bird.y > WINDOW_HEIGHT or self.bird.y < 0:
                self.game_active = False
                self.show_game_over()
                self.reset_game()

            for pipe in self.pipes:
                if (self.bird.x + self.bird.size > pipe.x and 
                    self.bird.x < pipe.x + 50):
                    if (self.bird.y < pipe.height or 
                        self.bird.y + self.bird.size > pipe.height + PIPE_GAP):
                        self.game_active = False
                        self.show_game_over()
                        self.reset_game()

            # Draw
            self.screen.fill(SKY_BLUE)
            self.bird.draw(self.screen)
            for pipe in self.pipes:
                pipe.draw(self.screen)
                
            self.draw_text(f'Score: {self.score}', 10, 10)
            self.draw_text(f'Highscore: {self.highscore}', 10, 50)

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run() 