import neat.config
import neat.population
import pygame as pg
import os
import random as rand
from pygame.locals import *
import neat

pg.font.init()
SCORE_FONT = pg.font.SysFont('comicsans', 30)

WIDTH = 450
HEIGHT = 700

BIRD_WIDTH = 40
BIRD_HEIGHT = 30

PIPE_WIDTH = 70
PIPE_HEIGHT = 500

BASE_WIDTH = 900
BASE_HEIGHT = 100

GRAVITY = 0.8  # Gravity constant, adjust as needed
JUMP_STRENGTH = -10  # Jump strength, negative value to go up
bird_velocity = 0

start = False
spawn = False
score = 0
pipe_passed = 1

GAME_OVER = False

WIN = pg.display.set_mode((WIDTH, HEIGHT))

FPS = 60

BG = pg.transform.scale(pg.image.load(os.path.join('Assets', 'background-day.png')), (WIDTH, HEIGHT))

BIRD_IMG_FILE = pg.image.load(os.path.join(
    'Assets', 'yellowbird-midflap.png'))
BIRD_IMG = pg.transform.rotate(
    pg.transform.scale(BIRD_IMG_FILE, (BIRD_WIDTH, BIRD_HEIGHT)), 0)

BASE_IMG_FILE = pg.image.load(os.path.join(
    'Assets', 'base.png'))
BASE_IMG = pg.transform.rotate(
    pg.transform.scale(BASE_IMG_FILE, (BASE_WIDTH, BASE_HEIGHT)), 0)

PIPE_IMG_FILE = pg.image.load(os.path.join(
    'Assets', 'pipe-green.png'))
BOTTOM_PIPE_IMG = pg.transform.rotate(
    pg.transform.scale(PIPE_IMG_FILE, (PIPE_WIDTH, PIPE_HEIGHT)), 0)
TOP_PIPE_IMG = pg.transform.rotate(
    pg.transform.scale(PIPE_IMG_FILE, (PIPE_WIDTH, PIPE_HEIGHT)), 180)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

PIPES = []
BASES = []

pipe_count = 0
running = True

BIRD_RECT = pg.Rect((150, 350), (BIRD_WIDTH, BIRD_HEIGHT))


def main_game_loop():
    
    global start
    global score
    global pipe_count
    global running
    clock = pg.time.Clock()

    
    global bird_velocity
    global pipe_passed

    while running:
        clock.tick(FPS)
        BIRD_RECT
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    bird_velocity = JUMP_STRENGTH
                    start = True
        
        if PIPES:
            for pipe in PIPES:
                if BIRD_RECT.x > pipe.x + PIPE_WIDTH and pipe.y != pipe_passed and pipe.y != pipe_count:
                    score += 1
                    pipe_passed = pipe.y
                    pipe_count = PIPES[1].y
                    break

        if start:
            gravity()

        collision()
        base_spawner()
        pipe_spawn()        
        draw_screen(score)
        #print(pg.time.Clock.get_fps(clock)) 
        # prints the fps


def draw_screen(score):

    global start
    score_text = SCORE_FONT.render("Score: " + str(score), 1, WHITE)
    
    WIN.blit(BG, (0,0))
    
    
    for pipe in range(len(PIPES)):
         
        if PIPES[pipe].y < PIPES[pipe - 1].y:
            WIN.blit(TOP_PIPE_IMG, (PIPES[pipe].x, PIPES[pipe].y))
        
        elif PIPES[pipe].y > PIPES[pipe + 1].y:
            WIN.blit(BOTTOM_PIPE_IMG, (PIPES[pipe].x, PIPES[pipe].y))
            pg.draw.line(WIN, (255, 255, 255), BIRD_RECT.center, PIPES[pipe].topright, 2)

    

    WIN.blit(BIRD_IMG, (BIRD_RECT.x, BIRD_RECT.y))
    
    for base in BASES:
        WIN.blit(BASE_IMG, (base.x, base.y))
    
    WIN.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    pg.display.flip()


def gravity():
    
    global bird_velocity
    GRAVITY = .8

    bird_velocity += GRAVITY
    BIRD_RECT.y += bird_velocity

    if BIRD_RECT.y >= HEIGHT - BASE_HEIGHT - BIRD_HEIGHT + 2:
        BIRD_RECT.y = HEIGHT - BASE_HEIGHT - BIRD_HEIGHT
        bird_velocity = 0
    
    elif BIRD_RECT.y <= 3:
        bird_velocity = 0
        
    for pipe in PIPES:
        pipe.x -= 3

    for pipe in PIPES:
        if pipe.x + PIPE_WIDTH < 0:
            PIPES.remove(pipe) 

    for base in BASES:
        base.x -= 3
        if base.right < 0:
            BASES.remove(base)         


def pipe_spawn():

    global spawn
    
    if spawn == False:
        num = rand.randint(300, 500)
        pipe_rect_1 = pg.Rect((525, num), (PIPE_WIDTH, PIPE_HEIGHT))
        pipe_rect_2 = pg.Rect((525, num - 625), (PIPE_WIDTH, PIPE_HEIGHT))
        PIPES.append(pipe_rect_1)
        PIPES.append(pipe_rect_2)
        
        spawn = True
    
    elif spawn == True and PIPES[-1].x < 230:
        num = random()
        pipe_rect_1 = pg.Rect((525, num), (PIPE_WIDTH, PIPE_HEIGHT))
        pipe_rect_2 = pg.Rect((525, num - 625), (PIPE_WIDTH, PIPE_HEIGHT))
        PIPES.append(pipe_rect_1)
        PIPES.append(pipe_rect_2)


def random():
    num = rand.randint(200, 550)

    return num


def base_spawner():
    
    if not BASES:
        base = pg.Rect((0, 600), (BASE_WIDTH, BASE_HEIGHT))
        BASES.append(base)

    if len(BASES) < 3:
        base = pg.Rect((BASES[0].right, 600), (BASE_WIDTH, BASE_HEIGHT))
        BASES.append(base)


def collision():
    
    for pipe in PIPES:
        if BIRD_RECT.colliderect(pipe):
           restart() 
          
    for base in BASES:
        if BIRD_RECT.colliderect(base):
            restart()


def restart():
    global BIRD_RECT, bird_velocity, game_over, score, start, spawn
    BIRD_RECT.y = 300
    bird_velocity = 0
    score = 0
    game_over = False
    start = False
    spawn = False
    PIPES.clear()
    BASES.clear()
    main_game_loop()


if __name__ == "__main__":
    main_game_loop()
    