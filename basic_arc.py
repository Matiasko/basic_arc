"""
Basic_arc - game by Mateusz Kalamarz created as a preject for Python programming course
Based on Arcanoid game
Contact <mateusz.kalamarz@o2.pl>
"""
import sys, os
import pygame
import random

SCREEN_SIZE   = 640,480

LEVEL = 1

# Object dimensions
BRICK_WIDTH   = 60
BRICK_HEIGHT  = 15
PADDLE_WIDTH  = 60-10*LEVEL
PADDLE_HEIGHT = 12
BALL_DIAMETER = 16
BALL_RADIUS   = BALL_DIAMETER / 2

MAX_PADDLE_X = SCREEN_SIZE[0] - PADDLE_WIDTH
MAX_BALL_X   = SCREEN_SIZE[0] - BALL_DIAMETER
MAX_BALL_Y   = SCREEN_SIZE[1] - BALL_DIAMETER

# Paddle Y coordinate
PADDLE_Y = SCREEN_SIZE[1] - PADDLE_HEIGHT - 10

# Color constants
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE  = (0,0,255)
BRICK_COLOR = (200,200,0)

# State constants
STATE_BALL_IN_PADDLE = 0
STATE_PLAYING = 1
STATE_WON = 2
STATE_GAME_OVER = 3
STATE_PAUSED = 4

# Sounds
pygame.mixer.pre_init(11025, -16, 2, 256)
pygame.mixer.init()
brick_dead = pygame.mixer.Sound('brick_dead.wav')
palet_hit = pygame.mixer.Sound('palet_hit.wav')
chill = pygame.mixer.Sound('jazz.wav')

class Basic_arc:

    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Basic_arc - game by Mateusz Kalamarz")
        
        self.clock = pygame.time.Clock()

        if pygame.font:
            self.font = pygame.font.Font(None,30)
        else:
            self.font = None

        self.init_game()

        
    def init_game(self):
        self.lives = 3
        self.score = 0
        self.state = STATE_BALL_IN_PADDLE
        self.before_paused = STATE_BALL_IN_PADDLE

        self.paddle   = pygame.Rect(300,PADDLE_Y,PADDLE_WIDTH,PADDLE_HEIGHT)
        self.ball     = pygame.Rect(300,PADDLE_Y - BALL_DIAMETER,BALL_DIAMETER,BALL_DIAMETER)

        self.ball_vel = [5,-5]

        self.create_bricks()
        

    def create_bricks(self):
        y_ofs = 35
        self.bricks = []
        self.RGB= [tuple(random.sample(range(256),3)) for e in range(0,7*8)]
        for i in range(7): #rows
            x_ofs = 35
            for j in range(8): #columns
                self.bricks.append(pygame.Rect(x_ofs,y_ofs,BRICK_WIDTH,BRICK_HEIGHT))
                x_ofs += BRICK_WIDTH + 10
            y_ofs += BRICK_HEIGHT + 5

    def draw_bricks(self):
        for brick, color in zip(self.bricks,self.RGB):
            pygame.draw.rect(self.screen, color, brick)
        
    def check_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.state != STATE_PAUSED:
            self.paddle.left -= 5
            if self.paddle.left < 0:
                self.paddle.left = 0

        if keys[pygame.K_RIGHT] and self.state != STATE_PAUSED:
            self.paddle.left += 5
            if self.paddle.left > MAX_PADDLE_X:
                self.paddle.left = MAX_PADDLE_X

        if keys[pygame.K_SPACE] and self.state == STATE_BALL_IN_PADDLE:
            self.ball_vel = [5,-5]
            self.state = STATE_PLAYING
        elif keys[pygame.K_RETURN] and (self.state in (STATE_GAME_OVER, STATE_WON)):
            self.init_game()

        if keys[pygame.K_p]:
            if self.state != STATE_PAUSED:
                self.before_paused = self.state
                self.state = STATE_PAUSED
                chill.play(-1)
            else:
                self.state = self.before_paused
                chill.stop()
    
        if keys[pygame.K_q] and (self.state in (STATE_WON, STATE_GAME_OVER, STATE_PAUSED)):
            pygame.display.quit()
            sys.exit()

    def move_ball(self):
        self.ball.left += self.ball_vel[0]
        self.ball.top  += self.ball_vel[1]

        if self.ball.left <= 0:
            self.ball.left = 0
            self.ball_vel[0] = -self.ball_vel[0]
        elif self.ball.left >= MAX_BALL_X:
            self.ball.left = MAX_BALL_X
            self.ball_vel[0] = -self.ball_vel[0]
        
        if self.ball.top < 0:
            self.ball.top = 0
            self.ball_vel[1] = -self.ball_vel[1]
        elif self.ball.top >= MAX_BALL_Y:            
            self.ball.top = MAX_BALL_Y
            self.ball_vel[1] = -self.ball_vel[1]

    def handle_collisions(self):
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                brick_dead.play(loops=0, maxtime=0, fade_ms=0)
                self.score += 3
                self.ball_vel[1] = -self.ball_vel[1]
                self.RGB.remove(self.RGB[self.bricks.index(brick)])
                self.bricks.remove(brick)
                break

        if len(self.bricks) == 0:
            self.state = STATE_WON
            
        if self.ball.colliderect(self.paddle):
            palet_hit.play()
            self.ball.top = PADDLE_Y - BALL_DIAMETER
            self.ball_vel[1] = -self.ball_vel[1]
        elif self.ball.top > self.paddle.top:
            self.lives -= 1
            if self.lives > 0:
                self.state = STATE_BALL_IN_PADDLE
            else:
                self.state = STATE_GAME_OVER

    def show_stats(self):
        if self.font:
            font_surface = self.font.render("SCORE: " + str(self.score) + " LIVES: " + str(self.lives), False, WHITE)
            self.screen.blit(font_surface, (205,5))

    def show_message(self,message):
        if self.font:
            size = self.font.size(message)
            font_surface = self.font.render(message,False, WHITE)
            x = (SCREEN_SIZE[0] - size[0]) / 2
            y = (SCREEN_SIZE[1] - size[1]) / 2
            self.screen.blit(font_surface, (x,y))
        
            
    def run(self):
        while 1:            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()

            self.clock.tick(50)
            self.screen.fill(BLACK)
            self.check_input()

            if self.state == STATE_PLAYING:
                self.move_ball()
                self.handle_collisions()
            elif self.state == STATE_BALL_IN_PADDLE:
                self.ball.left = self.paddle.left + self.paddle.width / 2
                self.ball.top  = self.paddle.top - self.ball.height
                self.show_message("PRESS SPACE TO LAUNCH THE BALL")
            elif self.state == STATE_PAUSED:
                self.show_message("PRESS P TO RESUME OR Q TO QUIT")
            elif self.state == STATE_GAME_OVER:
                self.show_message("GAME OVER. PRESS ENTER TO PLAY AGAIN OR Q TO QUIT")
            elif self.state == STATE_WON:
                self.show_message("YOU WON! PRESS ENTER TO PLAY AGAIN OR Q TO QUIT")
                
            self.draw_bricks()

            # Draw paddle
            pygame.draw.rect(self.screen, BLUE, self.paddle)

            # Draw ball
            pygame.draw.circle(self.screen, WHITE, (self.ball.left + BALL_RADIUS, self.ball.top + BALL_RADIUS), BALL_RADIUS)

            self.show_stats()

            pygame.display.flip()

if __name__ == "__main__":
    Basic_arc().run()
