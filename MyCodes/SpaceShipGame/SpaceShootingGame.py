import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1300, 700
BILLY_WIDTH, BILLY_HEIGHT = 100, 80
BILLA_WIDTH, BILLA_HEIGHT = 100, 80
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
FPS = 60
MOVE = 5
MAX_BULLETS = 5
BULLET_VELOCITY = 10

# Custom Events for Hits
BILLY_HIT = pygame.USEREVENT + 1
BILLA_HIT = pygame.USEREVENT + 2

# Window Setup
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SpaceWar.exe")
BORDER = pygame.Rect(SCREEN_WIDTH//2 - 5, 0, 10, SCREEN_HEIGHT)

# Assets (Using placeholders if files don't exist)
try:
    background = pygame.transform.scale(pygame.image.load('Space.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    billy_img = pygame.transform.scale(pygame.image.load('battleship.png'), (BILLY_WIDTH, BILLY_HEIGHT))
    billa_img = pygame.transform.flip(billy_img, True, False)
except:
    # Fallback if you don't have the images in the folder
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((10, 10, 30))
    billy_img = pygame.Surface((BILLY_WIDTH, BILLY_HEIGHT))
    billy_img.fill(BLUE)
    billa_img = pygame.Surface((BILLA_WIDTH, BILLA_HEIGHT))
    billa_img.fill(RED)

def draw_win(bi, ba, bullets_billy, bullets_billa, billy_health, billa_health):
    WIN.blit(background, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    
    # Draw Spaceships
    WIN.blit(billy_img, (bi.x, bi.y))
    WIN.blit(billa_img, (ba.x, ba.y))
    
    # Draw Bullets
    for bullet in bullets_billy:
        pygame.draw.rect(WIN, BLUE, bullet)
    for bullet in bullets_billa:
        pygame.draw.rect(WIN, RED, bullet)
        
    pygame.display.update()

def handle_bullets(bullets_billy, bullets_billa, bi, ba):
    # Move Billy's Bullets
    for bullet in bullets_billy[:]:
        bullet.x += BULLET_VELOCITY
        if ba.colliderect(bullet):
            pygame.event.post(pygame.event.Event(BILLA_HIT))
            bullets_billy.remove(bullet)
        elif bullet.x > SCREEN_WIDTH:
            bullets_billy.remove(bullet)

    # Move Billa's Bullets
    for bullet in bullets_billa[:]:
        bullet.x -= BULLET_VELOCITY
        if bi.colliderect(bullet):
            pygame.event.post(pygame.event.Event(BILLY_HIT))
            bullets_billa.remove(bullet)
        elif bullet.x < 0:
            bullets_billa.remove(bullet)

def billy_movement(key, bi):
    if key[pygame.K_w] and bi.y - MOVE > 0:
        bi.y -= MOVE
    if key[pygame.K_s] and bi.y + MOVE < SCREEN_HEIGHT - BILLY_HEIGHT:
        bi.y += MOVE
    if key[pygame.K_d] and bi.x + MOVE < BORDER.x - BILLY_WIDTH:
        bi.x += MOVE
    if key[pygame.K_a] and bi.x - MOVE > 0:
        bi.x -= MOVE

def billa_movement(key, ba):
    if key[pygame.K_i] and ba.y - MOVE > 0:
        ba.y -= MOVE
    if key[pygame.K_k] and ba.y + MOVE < SCREEN_HEIGHT - BILLA_HEIGHT:
        ba.y += MOVE
    if key[pygame.K_l] and ba.x + MOVE < SCREEN_WIDTH - BILLA_WIDTH:
        ba.x += MOVE
    if key[pygame.K_j] and ba.x - MOVE > BORDER.x + BORDER.width:
        ba.x -= MOVE

def main():
    bi = pygame.Rect(100, 300, BILLY_WIDTH, BILLY_HEIGHT)
    ba = pygame.Rect(1100, 300, BILLA_WIDTH, BILLA_HEIGHT)
    
    bullets_billy = []
    bullets_billa = []
    
    billy_health = 10
    billa_health = 10
    
    clock = pygame.time.Clock()
    run = True
    
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                # Billy Shoots (F key)
                if event.key == pygame.K_f and len(bullets_billy) < MAX_BULLETS:
                    bullet = pygame.Rect(bi.x + bi.width, bi.y + bi.height//2 - 2, 15, 5)
                    bullets_billy.append(bullet)
                
                # Billa Shoots (H key)
                if event.key == pygame.K_h and len(bullets_billa) < MAX_BULLETS:
                    bullet = pygame.Rect(ba.x, ba.y + ba.height//2 - 2, 15, 5)
                    bullets_billa.append(bullet)

            if event.type == BILLY_HIT:
                billy_health -= 1
                print(f"Billy Health: {billy_health}")
            
            if event.type == BILLA_HIT:
                billa_health -= 1
                print(f"Billa Health: {billa_health}")

        # Check Win Condition
        if billy_health <= 0 or billa_health <= 0:
            print("Game Over!")
            run = False

        keys_pressed = pygame.key.get_pressed()
        billy_movement(keys_pressed, bi)
        billa_movement(keys_pressed, ba)
        
        handle_bullets(bullets_billy, bullets_billa, bi, ba)
        
        draw_win(bi, ba, bullets_billy, bullets_billa, billy_health, billa_health)

    pygame.quit()

if __name__ == "__main__":
    main()