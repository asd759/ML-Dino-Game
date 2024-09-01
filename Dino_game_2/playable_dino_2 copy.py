import pygame as pg
import sys
import os
import math
import random as rd


pg.init()
pg.display.set_caption("game")

scroll = 0

clock = pg.time.Clock()
FPS = 60
WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BG = pg.image.load("Assets/Other/Track.png")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

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


class dino():
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
            if elapsed_time - self.last_update_time > 400:
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

    def set_mask(self, img_key):
        self.img = OBSTICAL_IMAGES[img_key]
        self.rect = self.img.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.img)

DINOS = [dino()]
OBSTICALS = [cactus(3)]

def main_game():
    
    run = True
    score = 0
    game_speed = 6
    start_time = pg.time.get_ticks()
    
    
    
    while run:
        clock.tick(FPS)
        elapsed_time = pg.time.get_ticks() - start_time
        pos = pg.mouse.get_pos()
        WIN.fill(WHITE)

        bullet = pg.Surface((10, 10))
        bullet.fill(RED)
        bullet_mask = pg.mask.from_surface(bullet)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    dino.stand_up()

            
        keys_pressed = pg.key.get_pressed()
        for dino in DINOS:
            if keys_pressed[pg.K_SPACE]: dino.jump()
            if keys_pressed[pg.K_DOWN]: dino.duck(elapsed_time)

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
                break

        
        # handles collsions between dinos and obsticals 
        for obstical in OBSTICALS:
            for dino in DINOS:
                if dino.mask.overlap(obstical.mask, (obstical.rect.x - dino.rect.x, obstical.rect.y - dino.rect.y)):
                    # DINOS.remove(dino)
                    print('hit')
                    if len(DINOS) == 0:
                        pg.quit()
                        sys.exit()

        # increments the score and evry 100 points increses the game speed
        score += 0.1
        if round(score) % 100 == 0:
            if round(score) != round(score - 0.1):
                game_speed += 1

        if DINOS[0].mask.overlap(bullet_mask, (pos[0] - DINOS[0].rect.x, pos[1] - DINOS[0].rect.y)):
          print("hit")

    
        WIN.blit(bullet, pos)

        #print(f"the score is {round(score)} the game speed is {game_speed}")
        # controlls the background scroll
        bg_scroll(game_speed)
        # updates dinos
        DINOS[0].update(elapsed_time)
        # updates obsticals both birds and cacti
        for obstical in OBSTICALS:
            obstical.update(game_speed, elapsed_time)

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


if __name__ == "__main__":
    main_game()


