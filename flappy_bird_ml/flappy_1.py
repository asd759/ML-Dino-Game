import neat.checkpoint
import pygame as pg
import os
import random
import sys
import neat
import math

pg.init()
pg.display.set_caption("Flappy Bird ML")

WIN_WIDTH = 450
WIN_HEIGHT = 700
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BIRD_WIDTH = 40
BIRD_HEIGHT = 30

PIPE_WIDTH = 70
PIPE_HEIGHT = 500

BASE_WIDTH = 900
BASE_HEIGHT = 100

GRAVITY = 0.8  # Gravity constant, adjust as needed
JUMP_STRENGTH = -10  # Jump strength, negative value to go up

FONT = pg.font.Font('freesansbold.ttf', 20)
BIRD_IMG_MID_FLAP_FILE = pg.image.load(os.path.join(
                'Assets', 'yellowbird-midflap.png'))
BIRD_IMG_DOWN_FLAP_FILE = pg.image.load(os.path.join(
                'Assets', 'yellowbird-downflap.png'))
BIRD_IMG_UP_FLAP_FILE = pg.image.load(os.path.join(
                'Assets', 'yellowbird-upflap.png'))

FLYING = [pg.transform.rotate(pg.transform.scale(BIRD_IMG_MID_FLAP_FILE, (BIRD_WIDTH, BIRD_HEIGHT)), 0),
          pg.transform.rotate(pg.transform.scale(BIRD_IMG_DOWN_FLAP_FILE, (BIRD_WIDTH, BIRD_HEIGHT)), 0),
          pg.transform.rotate(pg.transform.scale(BIRD_IMG_UP_FLAP_FILE, (BIRD_WIDTH, BIRD_HEIGHT)), 0)]

PIPE_IMG_FILE = pg.image.load(os.path.join(
    'Assets', 'pipe-green.png'))

# PIPES_IMGS[0] is the top pipe 
# PIPES_IMGS[1] is the bottom pipe
PIPE_IMGS = [pg.transform.rotate(pg.transform.scale(PIPE_IMG_FILE, (PIPE_WIDTH, PIPE_HEIGHT)), 0),
             pg.transform.rotate(pg.transform.scale(PIPE_IMG_FILE, (PIPE_WIDTH, PIPE_HEIGHT)), 180)]

BG = pg.transform.scale(pg.image.load(os.path.join('Assets', 'background-day.png')), (WIN_WIDTH, WIN_HEIGHT))

BASE_IMG_FILE = pg.image.load(os.path.join('Assets', 'base.png'))
BASE_IMG = pg.transform.rotate(pg.transform.scale(BASE_IMG_FILE, (BASE_WIDTH, BASE_HEIGHT)), 0)

HIGH_SCORE = 0

class Bird():
    global X_POS, Y_POS
    X_POS = 150
    Y_POS = 350

    def __init__(self):
        self.img = FLYING[0]
        self.rect = pg.Rect(X_POS, Y_POS, BIRD_WIDTH, BIRD_HEIGHT)
        self.is_jumping = False
        self.jump_vel = 0
    
    def draw(self):
        WIN.blit(self.img, self.rect)

    def jump(self):
        if self.is_jumping:
            self.jump_vel = JUMP_STRENGTH
            self.is_jumping = False

    def gravity(self, start):
            self.jump_vel += GRAVITY
            self.rect.y += self.jump_vel
            
    def update(self, WIN, BIRDS, start):
        self.gravity(start)
        self.draw()

class Pipe():

    def __init__(self):
        self.img_bottom = PIPE_IMGS[0]
        self.img_top = PIPE_IMGS[1]
        rand = random.randint(200, 550)
        self.bottom_rect = pg.Rect((WIN_WIDTH + 25, rand), (PIPE_WIDTH, PIPE_HEIGHT))
        rand -= PIPE_HEIGHT + 125
        self.top_rect = pg.Rect((WIN_WIDTH + 25, rand), (PIPE_WIDTH, PIPE_HEIGHT))
        self.counted = False
        self.target = False

    def draw(self):
        WIN.blit(self.img_top, self.top_rect)
        WIN.blit(self.img_bottom, self.bottom_rect)

    def pipe_move(self, start):
        self.bottom_rect.x -= 2
        self.top_rect.x -= 2

    def update(self, PIPES, start):
        if self.bottom_rect.x < WIN_WIDTH // 2 and self.counted == False:
            self.counted = True
            PIPES.append(Pipe())
        self.pipe_move(start)
        self.draw()

def eval_genomes(genomes, config):
    global score
    clock = pg.time.Clock()
    run = True
    start = False
    score = 0
    top_y = 0
    bottom_y = 0
    BIRDS = []
    PIPES = [Pipe()]
    BASES = []
    pipes_to_remove = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        BIRDS.append(Bird())
        ge.append(genome)
        net = net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0


    def stats():
        text_1 = FONT.render(f'Current Score: {str(score)}', True, (255, 255, 255))
        text_2 = FONT.render(f'birds alive:  {str(len(BIRDS))}', True, (255, 255, 255))
        text_3 = FONT.render(f'Genaration: {p.generation + 1}', True, (255, 255, 255))
        text_4 = FONT.render(f'High Score:  {HIGH_SCORE}', True, (255, 255, 255))
        
        WIN.blit(text_1, (250, 25))
        WIN.blit(text_2, (290, 655))
        WIN.blit(text_3, (290, 675))
        WIN.blit(text_4, (290, 635))



    def BackGround():
        WIN.blit(BG, (0,0))


    def Base():
        if not BASES:
            base = pg.Rect((0, 600), (BASE_WIDTH, BASE_HEIGHT))
            BASES.append(base)

        if len(BASES) < 3:
            base = pg.Rect((BASES[0].right, 600), (BASE_WIDTH, BASE_HEIGHT))
            BASES.append(base)
        
        for base in BASES:
            base.x -= 2
            if base.right < 0:
                BASES.remove(base)
        
        for base in BASES:
            WIN.blit(BASE_IMG, (base.x, base.y))
    

    def target():
        global score, HIGH_SCORE
        if len(PIPES) == 1:
            for pipe in PIPES:
                pipe.target = True
        
        for i, pipe in enumerate(PIPES):
            for bird in BIRDS:
                if pipe.bottom_rect.right < bird.rect.x and pipe.target == True:
                    score += 1
                    pipe.target = False
                    ge[i].fitness += 1
                if len(PIPES) > 1:
                    if PIPES[1].target == False and pipe.bottom_rect.right > bird.rect.x and PIPES[0].target == False:
                        pipe.target = True
        if score > HIGH_SCORE:
            HIGH_SCORE = score


    def vision():
        for pipe in PIPES:
            for bird in BIRDS:
                if pipe.target == True:
                    pg.draw.line(WIN, (255, 255, 255), (bird.rect.center), (pipe.bottom_rect.topright), 2)
                    pg.draw.line(WIN, (255, 255, 255), (bird.rect.center), (pipe.top_rect.bottomright), 2)


    def remove(index):
        BIRDS.pop(index)
        ge.pop(index)
        nets.pop(index)


    def distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    
# main game loop
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.QUIT
                sys.exit()

        # sets the BG                     
        BackGround()

        # updates bird
        for bird in BIRDS:
            bird.update(WIN, BIRDS, start)
        
        # updates pipes and checks for collisions and checks wich pipes are of screen 
        for pipe in PIPES:
            pipe.update(PIPES, start)
            for i, bird in enumerate(BIRDS):
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    ge[i].fitness -= 1    
                    remove(i)
                if pipe.bottom_rect.right + PIPE_WIDTH < 0:
                    pipes_to_remove.append(pipe)

        # checks of bird hit ground or roof if yes -1 fitness 
        for i, bird in enumerate(BIRDS):
            if bird.rect.y + BIRD_HEIGHT > WIN_HEIGHT - 100 or bird.rect.y < 0:
                    ge[i].fitness -= 1
                    remove(i)
                    
        # removes pipes that are off screen
        PIPES = [pipe for pipe in PIPES if pipe.bottom_rect.right + PIPE_WIDTH >= 0]
        
        # checks if all the birds are dead
        if not BIRDS: 
            break

        # finds distance between bird and top and bottom pipes
        dis_bottom = 0
        dis_top = 0
        for pipe in PIPES:
            if pipe.target == True:
                dis_bottom = distance((bird.rect.center), (pipe.bottom_rect.topright))
                dis_top = distance((bird.rect.center), (pipe.top_rect.bottomright))
        
        # gives fitnes for the bird y being inbetween the top and bottom pipe
        for pipe in PIPES:
            for i, bird in enumerate(BIRDS):
                if pipe.target and pipe.top_rect.bottom < bird.rect.centery < pipe.bottom_rect.top:
                    ge[i].fitness += .1
                if pipe.target and pipe.top_rect.bottom > bird.rect.centery > pipe.bottom_rect.top:
                    ge[i].fitness -= .05
        


        # activates the neuarl net
        for i, pipe in enumerate(PIPES):
            if pipe.target:
                top_y = PIPES[i].top_rect.bottom
                bottom_y = PIPES[i].bottom_rect.top

            for i, bird in enumerate(BIRDS):
                output = nets[i].activate((bird.rect.y, dis_bottom, dis_top, top_y, bottom_y))
                if output[0] > 0.5:
                    bird.is_jumping = True
                    bird.jump()
    
        # creats the bottom 
        Base()
        # renders the text the score, genartion, alive and highscore
        stats()
        # makes sure the bir is only foucusing on the pipe right in front of it and updates the score and highscore
        target() 
        # draws the bird vision the two whit lines
        vision()         
        clock.tick(60)
        pg.display.update()
    


def run_neat(config_path):
    global p
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    # if you want to load form a check point comment out this line
    p = neat.Population(config)
    #and uncomment this line and specify the checkpoint at the end
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-21')
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(2))
    p.run(eval_genomes)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'flappy_config.txt')
    run_neat(config_path)