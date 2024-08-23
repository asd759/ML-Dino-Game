import pygame as pg
import sys
import os
import math
import random as rd

pg.init()
pg.display.set_caption("game")

clock = pg.time.Clock()
FPS = 60
WIN_WIDTH = 800
WIN_HEIGHT = 500
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BG = pg.transform.scale(pg.image.load(os.path.join('cave_game_assets', 'cave_2.png')), (WIN_WIDTH, WIN_HEIGHT))
scroll = 0

PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30

direction = 2
run = True



class player():
    global X_POS, Y_POS
    X_POS = 200
    Y_POS = 350

    def __init__(self):
        self.img = None
        self.rect = pg.Rect(X_POS, Y_POS, PLAYER_WIDTH, PLAYER_HEIGHT)
        
    
    def draw(self):
        #WIN.blit(self.img, self.rect)
        pg.draw.rect(WIN, (255,255,255), self.rect)
    
    def gravity(self, direction):
        if direction == 1 and self.rect.y > 80:
            self.rect.y -= 10
            if self.rect.y < 80:
                self.rect.y = 80
        if direction == 2 and self.rect.y < 395:
            self.rect.y += 10
            if self.rect.y > 395:
                self.rect.y = 395
    
    def collision(self, obsticals, players):
        for obstical in obsticals:
            for player in players:
                if player.rect.colliderect(obstical.rect):
                    players.remove(player)

    
    def update(self, direction, obsticals, players):
        self.draw()
        self.gravity(direction)
        self.collision(obsticals, players)


class obstical_1():
    def __init__(self):
        self.rect = self.size()
        self.seen = False
        self.off_screen = False
    
    def size(self):
        width = rd.randint(50, 150)
        height= rd.randint(50, 150)
        y_pos = rd.randint(80, 425 - height)
        return pg.Rect(850, y_pos, width, height)
    
    def move(self, game_speed):
        self.rect.x -= game_speed
    
    def draw(self):
        pg.draw.rect(WIN, (255,255,255), self.rect)

    def update(self, game_speed):
        self.move(game_speed)
        self.draw()


def main_game():
    PLAYERS = [player()]
    OBSTICALS = [obstical_1()]
    global direction, run
    score = 0
    game_speed = 2
    
    while run:
        clock.tick(FPS)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if direction == 1:
                        direction = 2
                    else:
                        direction = 1
            mouse_click = pg.mouse.get_pressed()
            if mouse_click[0]:
                if direction == 1:
                    direction = 2
                else:
                    direction = 1

        # adds obsticals
        for obstical in OBSTICALS:
            if obstical.rect.x < WIN_WIDTH//2 and not obstical.seen:
                obstical.seen = True
                OBSTICALS.append(obstical_1())
            if obstical.rect.right < 10:
                obstical.off_screen = True

        # delets off screen obsticals
        for obstical in OBSTICALS:
            if obstical.off_screen:
                OBSTICALS.remove(obstical)
                break
        
        # scrolls the background depending on how far into the game the player is
        if score % 300 == 0:
            game_speed += 1
        bg_scroll(game_speed)

        # updates the player
        PLAYERS[0].update(direction, OBSTICALS, PLAYERS)
        
        # checks if all players are dead
        if not PLAYERS:
            run = False

        for obstical in OBSTICALS:
            obstical.update(game_speed)
        # updates score
        score += 1
        print(len(OBSTICALS))
        pg.display.update()


def bg_scroll(game_speed):
    global scroll
    tiles = math.ceil(WIN_WIDTH / BG.get_width()) + 1
    for i in range(0, tiles):
            WIN.blit(BG, (i * BG.get_width() + scroll ,0))
        
    scroll -= game_speed

    if abs(scroll) > BG.get_width():
        scroll = 0

if __name__ == "__main__":
    main_game()