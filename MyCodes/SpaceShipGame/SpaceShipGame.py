import pygame

#BILLY -> LEFT_SPACESHIP
#BILLA -> RIGHT_SPACESHIP
SCREEN_WIDTH,SCREEN_HEIGHT=1300,700
BILLY_WIDTH,BILLY_HEIGHT=150,100
BILLA_WIDTH,BILLA_HEIGHT=150,100
WHITE=(255,255,255)
BLACK=(0,0,0)
BLUE=(0,0,255)
RED=(255,0,0)
FPS=60
MOVE=5
MAX_BULLETS=30
BULLET_VELOCITY=10

class bull(object):
    def __init__(self,colour=BLUE,x=0,y=0):
        self.x=x
        self.y=y
        self.colour=colour
        self.width=80
        self.height=5

WIN=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
border=pygame.Rect(SCREEN_WIDTH/2-5,0,10,SCREEN_HEIGHT)
pygame.display.set_caption("SpaceWar.exe")

background=pygame.transform.scale(pygame.image.load('Space.jpg'),(SCREEN_WIDTH,SCREEN_HEIGHT))
billy=pygame.transform.scale(pygame.image.load('battleship.png'),(BILLY_WIDTH,BILLY_HEIGHT))
billa=pygame.transform.flip(pygame.transform.scale(pygame.image.load('battleship.png'),(BILLA_WIDTH,BILLA_HEIGHT)),flip_x=180,flip_y=0)

def draw_win(bi,ba,fire_billy,fire_billa,bullets_billy,bullets_billa):
    WIN.fill(WHITE)
    WIN.blit(background,(0,0))
    pygame.draw.rect(WIN,BLACK,border)
    WIN.blit(billa,(ba.x,ba.y))
    WIN.blit(billy,(bi.x,bi.y))
    for bullet in bullets_billy:
        if fire_billy:
            pygame.draw.rect(WIN,bullet.colour,(bullet.x,bullet.y,bullet.width,bullet.height))
        if bullet.x>SCREEN_WIDTH:
            bullets_billy.pop(bullets_billy.index(bullet))
    for bullet in bullets_billa:
        if fire_billa:
            pygame.draw.rect(WIN,bullet.colour,(bullet.x,bullet.y,bullet.width,bullet.height))
        if bullet.x+bullet.width<0:
            bullets_billa.pop(bullets_billa.index(bullet))
    pygame.display.update()

def main():

    global x,y
    clock=pygame.time.Clock()
    bi=pygame.Rect(300,300,BILLY_WIDTH,BILLY_HEIGHT)
    ba=pygame.Rect(900,300,BILLA_WIDTH,BILLA_HEIGHT)
    fire_billy=False
    fire_billa=False
    run=True
    bullets_billy=[]
    bullets_billa=[]
    while run:
        clock.tick(FPS)
        #BULLET_MOVEMENT
        for bullet in bullets_billy:
            bullet.x+=BULLET_VELOCITY
        for bullet in bullets_billa:
            bullet.x-=BULLET_VELOCITY

        #QUITTING_HANDLER
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False

        #MOVEMENT_HANDLER
        key=pygame.key.get_pressed()
        if key[pygame.K_f]:
            fire_billy=True
            x=bi.x+133
            y=bi.y+80
            if len(bullets_billy)<MAX_BULLETS:
                bullets_billy.append(bull(RED,x,y))
        if key[pygame.K_h]:
            fire_billa=True
            x=ba.x-63
            y=ba.y+80
            if len(bullets_billa)<MAX_BULLETS:
                bullets_billa.append(bull(BLUE,x,y))
        billy_movement(key,bi)
        billa_movement(key,ba)


        #DRAWING_WINDOW
        draw_win(bi,ba,fire_billy,fire_billa,bullets_billy,bullets_billa)
        


    pygame.quit()

def billy_movement(key,bi):
    if key[pygame.K_w] and bi.y-MOVE>0:
        bi.y-=MOVE #up
    if key[pygame.K_s] and bi.y+MOVE<SCREEN_HEIGHT-BILLY_HEIGHT:
        bi.y+=MOVE #down
    if key[pygame.K_d] and bi.x+MOVE<(SCREEN_WIDTH/2-5)-BILLY_WIDTH:
        bi.x+=MOVE #right
    if key[pygame.K_a] and bi.x-MOVE>0:
        bi.x-=MOVE #left
def billa_movement(key,ba):
    if key[pygame.K_i] and ba.y-MOVE>0:
        ba.y-=MOVE #up
    if key[pygame.K_k] and ba.y+MOVE<SCREEN_HEIGHT-BILLA_HEIGHT:
        ba.y+=MOVE #down
    if key[pygame.K_l] and ba.x+MOVE<SCREEN_WIDTH-BILLA_WIDTH:
        ba.x+=MOVE #right
    if key[pygame.K_j] and ba.x-MOVE>SCREEN_WIDTH/2+5:
        ba.x-=MOVE #left

if __name__=="__main__":
    main()
