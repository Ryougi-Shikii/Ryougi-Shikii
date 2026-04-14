import pygame

FPS=60
SPEED=7
SCREEN_WIDTH,SCREEN_HEIGHT=1100,700
BUNNY_WIDTH,BUNNY_HEIGHT=300,200
ULTRA_WIDTH,ULTRA_HEIGHT=300,200
WHITE=(225,225,245)

WIN=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("expt")
bunny=pygame.transform.scale(pygame.image.load('bunny.png'),(BUNNY_WIDTH,BUNNY_HEIGHT))
backgroung=pygame.transform.scale(pygame.image.load('space.jpg'),(SCREEN_WIDTH,SCREEN_HEIGHT))
ultra=pygame.transform.scale(pygame.image.load('ultra.png'),(ULTRA_WIDTH,ULTRA_HEIGHT))

def chi_movement(keys,ult):
    if keys[pygame.K_i] and ult.y>0:
        ult.y-=SPEED #up
    if keys[pygame.K_k] and ult.y<SCREEN_HEIGHT-ULTRA_HEIGHT:
        ult.y+=SPEED #down
    if keys[pygame.K_j] and ult.x>0:
        ult.x-=SPEED #left
    if keys[pygame.K_l] and ult.x<SCREEN_WIDTH-ULTRA_WIDTH:
        ult.x+=SPEED #right
def bun_movement(keys,bun):
    if keys[pygame.K_w] and bun.y>0:
        bun.y-=SPEED #up
    if keys[pygame.K_s] and bun.y<SCREEN_HEIGHT-BUNNY_HEIGHT:
        bun.y+=SPEED #down
    if keys[pygame.K_a] and bun.x>0:
        bun.x-=SPEED #left
    if keys[pygame.K_d] and bun.x<SCREEN_WIDTH-BUNNY_WIDTH:
        bun.x+=SPEED #right

def display(bun,ult):
    pygame.display.update()
    WIN.fill(WHITE)
    WIN.blit(backgroung,(0,0))
    WIN.blit(bunny,(bun.x,bun.y))
    WIN.blit(ultra,(ult.x,ult.y))

def main():
    clock=pygame.time.Clock()
    bun=pygame.Rect(50,320,BUNNY_WIDTH,BUNNY_HEIGHT)
    ult=pygame.Rect(530,320,ULTRA_WIDTH,ULTRA_HEIGHT)
    run=True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
        keys=pygame.key.get_pressed()
        
        bun_movement(keys,bun)
        chi_movement(keys,ult)

        display(bun,ult)
    pygame.quit()



if __name__=='__main__':
    main()