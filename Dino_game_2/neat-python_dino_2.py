import pygame as pg
import sys
import os
import math
import random as rd
import neat


pg.init()
pg.display.set_caption("game")

scroll = 0

clock = pg.time.Clock()
FPS = 60
WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BG = pg.image.load("Assets/Other/Track.png")
FONT = pg.font.Font('freesansbold.ttf', 20)

WHITE = (255, 255, 255)
RED = (255, 0, 0)

high_score = 0

bird1 = pg.image.load("Assets/Bird/Bird1.png").convert_alpha()
bird2 = pg.image.load("Assets/Bird/Bird2.png").convert_alpha()

# Define a scaling factor
scaling_factor = 1.2  # Scale up by a factor of 2

# Get the original dimensions of the images
bird1_width, bird1_height = bird1.get_size()
bird2_width, bird2_height = bird2.get_size()

# Scale the images up
bird1_scaled = pg.transform.scale(bird1, (bird1_width * scaling_factor, bird1_height * scaling_factor))
bird2_scaled = pg.transform.scale(bird2, (bird2_width * scaling_factor, bird2_height * scaling_factor))


DINO_IMAGES = {
            'Run1': pg.image.load("Assets/Dino/DinoRun1.png").convert_alpha(),
            'Run2': pg.image.load("Assets/Dino/DinoRun2.png").convert_alpha(),
            'Jump': pg.image.load("Assets/Dino/DinoJump.png").convert_alpha(),
            'Duck1': pg.image.load("Assets/Dino/DinoDuck1.png").convert_alpha(),
            'Duck2': pg.image.load("Assets/Dino/DinoDuck2.png").convert_alpha()
        }

OBSTICAL_IMAGES = {
    'small_cactus1': pg.image.load(f"Assets/Cactus/SmallCactus1.png").convert_alpha(),
    'small_cactus2': pg.image.load(f"Assets/Cactus/SmallCactus2.png").convert_alpha(),
    'small_cactus3': pg.image.load(f"Assets/Cactus/SmallCactus3.png").convert_alpha(),
    'large_cactus1': pg.image.load(f"Assets/Cactus/LargeCactus1.png").convert_alpha(),
    'large_cactus2': pg.image.load(f"Assets/Cactus/LargeCactus2.png").convert_alpha(),
    'large_cactus3': pg.image.load(f"Assets/Cactus/LargeCactus3.png").convert_alpha(),
    'bird1': bird1_scaled,
    'bird2': bird2_scaled
    }

class Dino():
    def __init__(self) -> None:
        self.img = DINO_IMAGES['Run1']
        self.rect = self.img.get_rect(topleft=(100,280))
        self.mask = pg.mask.from_surface(self.img)
        self.is_ducking = False
        self.vel_y = 0
        self.gravity_acceleration = 1
        self.jump_strength = -20
        self.is_on_gorund = True
        self.last_update_time = 0
        self.loop = 1
        self.loop_duck = 1
        self.first = True
    
    def draw(self):
        WIN.blit(self.img, self.rect)
    
    def jump(self):
        if self.is_on_gorund and not self.is_ducking:
            self.vel_y = self.jump_strength
            self.is_on_gorund = False
            self.set_mask('Jump')
            
    def gravity(self):
        if not self.is_on_gorund:
            self.vel_y += self.gravity_acceleration  # Apply gravity to the velocity
            self.rect.y += self.vel_y 
        if self.rect.y > 280 and not self.is_ducking: 
            self.rect.y = 280 
            self.vel_y = 0
        if self.rect.y == 280 or self.rect.y == 310:
            self.is_on_gorund = True
    
    def stand_up(self):
        if self.is_ducking:
            self.is_ducking = False
            self.rect.y = 280
            self.img = DINO_IMAGES['Run1']
            self.first = True
    
    def duck(self, elapsed_time):
        if self.is_on_gorund == True:
            self.is_ducking = True
            self.animate_dino_duck(elapsed_time)
    
    def animate_dino_run(self, elapsed_time):
            if elapsed_time - self.last_update_time > 300:
                self.last_update_time = elapsed_time
                if self.loop == 1:
                    self.set_mask('Run1')
                    self.loop = 2
                else:
                    self.set_mask('Run2')
                    self.loop = 1
            
    def animate_dino_duck(self, elapsed_time):
            if elapsed_time - self.last_update_time > 300:
                self.last_update_time = elapsed_time
                if self.loop_duck == 1:
                    self.set_mask('Duck1')
                    self.rect.y = 310
                    self.loop_duck = 2
                else:
                    self.set_mask('Duck2')
                    self.rect.y = 310
                    self.loop_duck = 1
            elif self.first:
                    self.set_mask('Duck1')
                    self.rect.y = 310
                    self.first = False

    def set_mask(self, img_key):
        self.img = DINO_IMAGES[img_key]
        self.rect = self.img.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.img)

    def update(self, elapsed_time):
        if self.is_on_gorund and not self.is_ducking:
            self.animate_dino_run(elapsed_time)
        self.gravity()
        self.draw()
      

class cactus():
    def __init__(self, index, varient=1) -> None:

        self.seen = False
        self.off_screen = False
        self.bird = False
        self.last_update_time = 0
        self.target = False

        match index:
            case 1: self.spawn_small(varient)
            case 2: self.spawn_large(varient)
            case 3: self.spawn_bird()
            
    def spawn_small(self, varient):
        self.img = OBSTICAL_IMAGES[f"small_cactus{varient}"]
        self.rect = self.img.get_rect(topleft=(1060, 300))
        self.mask = pg.mask.from_surface(self.img)

    def spawn_large(self, varient):
        self.img = OBSTICAL_IMAGES[f"large_cactus{varient}"]
        self.rect = self.img.get_rect(topleft=(1050, 280))
        self.mask = pg.mask.from_surface(self.img)

    def spawn_bird(self):
        self.img = OBSTICAL_IMAGES['bird1']
        self.rect = self.img.get_rect(topleft=(980, 210))
        self.mask = pg.mask.from_surface(self.img)
        self.bird = True
        self.loop = 1
        
    def draw(self):
        WIN.blit(self.img, self.rect)

    def animate_bird(self, elapsed_time):
            if elapsed_time - self.last_update_time > 300:
                self.last_update_time = elapsed_time
                if self.loop == 1:
                    self.set_mask('bird1')
                    self.loop = 2
                else:
                    self.set_mask('bird2')
                    self.loop = 1
            WIN.blit(self.img, self.rect)

    def move(self, game_speed):
        self.rect.x -= game_speed

    def update(self, game_speed, elasped_time=None):
        
        if self.bird == True:
            self.animate_bird(elasped_time)
            self.move(game_speed + 2)
        else:
            self.draw()
            self.move(game_speed)

    def is_bird(self):
        if self.bird:
            return True
        else:
            return False


    def set_mask(self, img_key):
        self.img = OBSTICAL_IMAGES[img_key]
        self.rect = self.img.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.img)


def main_game(genomes, config):
    global high_score
    run = True
    score = 0
    game_speed = 6
    start_time = pg.time.get_ticks()
    DINOS = []
    OBSTICALS = [cactus(3)]
    

    # neat stuff
    ge = []
    nets = []
    
    for genome_id, genome in genomes:
        DINOS.append(Dino())
        ge.append(genome)
        net = net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
    
    
    
    while run:
        clock.tick(FPS)
        elapsed_time = pg.time.get_ticks() - start_time
        pos = pg.mouse.get_pos()
        WIN.fill(WHITE)
        target_obstical = None

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # removes obsticals that are off screen and adds new ones
        for obstical in OBSTICALS:
            if obstical.rect.x < WIN_WIDTH//2 and not obstical.seen:
                obstical.seen = True
                
                # randomly picks either a large or small cactus 
                index = rd.randint(1,3)

                # randomly chooses wich tyoe of large or small cactus
                varient = rd.randint(1,3)
                OBSTICALS.append(cactus(index, varient))

            

            if obstical.rect.right < 10:
                obstical.off_screen = True

        # delets off screen obsticals
        for obstical in OBSTICALS:
            if obstical.off_screen:
                OBSTICALS.remove(obstical)

        
        # handles collsions between dinos and obsticals 
        for obstical in OBSTICALS:
                for i in reversed(range(len(DINOS))):  # Use reversed to avoid index shifting issues
                    dino = DINOS[i]
                    # makes it so that the object clostes to the dinos is the one that they are looking at 
                    if len(OBSTICALS) == 1:
                        OBSTICALS[0].target = True
                    if obstical.rect.x < dino.rect.x:
                        obstical.target = False
                        OBSTICALS[1].target = True
                    if obstical.target:
                        target_obstical = obstical

                # Check for collision between dino and obstacle
                    if dino.mask.overlap(obstical.mask, (obstical.rect.x - dino.rect.x, obstical.rect.y - dino.rect.y)):
                        # Collision detected: penalize fitness and remove the dino, its genome, and its network
                        ge[i].fitness -= 1   
                        
                        # Remove the dino, genome, and network from their respective lists
                        DINOS.pop(i)
                        ge.pop(i)
                        nets.pop(i)
                        
        # increments the score and evry 100 points increses the game speed
        score += 0.1
        if round(score) % 100 == 0:
            if round(score) != round(score - 0.1):
                game_speed += 1              

        if target_obstical:
            for i, dino in enumerate(DINOS):
                dis = distance(dino.rect.center, target_obstical.rect.center)
            
                output = nets[i].activate((dino.rect.x, dis, game_speed, score, target_obstical.rect.y, target_obstical.rect.width, target_obstical.rect.height, target_obstical.is_bird()))
                action = output.index(max(output))

                # Determine action based on the highest output value
                if action == 0:  # Jump
                    dino.jump()
                elif action == 1:  # Duck
                    dino.duck(elapsed_time)
                else:  # Stand up
                    dino.stand_up()

        # shows stats
        stats(round(score), len(DINOS), high_score)
        # controlls the background scroll
        bg_scroll(game_speed)
        # updates dinos
        for i, dino in enumerate(DINOS):
            if target_obstical.is_bird() and action == 1:
                ge[i].fitness += 1
            elif action == 1:
                ge[i].fitness -= 0.1


            ge[i].fitness += 0.01
            dino.update(elapsed_time)
            visual(target_obstical, dino)
        # updates obsticals both birds and cacti
        for obstical in OBSTICALS:
            obstical.update(game_speed, elapsed_time)

        # If no dinos remain, exit the loop
        if len(DINOS) == 0:
            if score > high_score:
                high_score = round(score)
            break

        # updates display
        pg.display.update()


def bg_scroll(game_speed):

    global scroll
    tiles = math.ceil(WIN_WIDTH / BG.get_width()) + 1
    for i in range(0, tiles):
            WIN.blit(BG, (i * BG.get_width() + scroll ,350))
        
    scroll -= game_speed

    if abs(scroll) > BG.get_width():
        scroll = 0


def stats(score, DINOS, high_score):
        text_1 = FONT.render(f'Current Score: {str(score)}', True, RED)
        text_2 = FONT.render(f'Dinos alive:  {DINOS}', True, RED)
        text_3 = FONT.render(f'Genaration: {p.generation + 1}', True, RED)
        text_4 = FONT.render(f'High Score:  {high_score}', True, RED)
        
        WIN.blit(text_1, (750, 25))
        WIN.blit(text_2, (750, 50))
        WIN.blit(text_3, (750, 75))
        WIN.blit(text_4, (750, 100))


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def visual(target_obstical, dino):
        pg.draw.line(WIN, RED, (dino.rect.center), (target_obstical.rect.center))



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
    p.run(main_game)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'dino2_config.txt')
    run_neat(config_path)


