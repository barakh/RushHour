x = 400
y = 300

import pygame, sys
from serial import Serial

UP = 8
LEFT = 9
RIGHT = 10
DOWN = 2
W = 0xB #UP
A = 0xC #LEFT
D = 0xD #RIGHT
S = 0x3
Y = 5
G = 6
J = 7
H = 4

com = Serial("/dev/ttyACM0", 115200)
for i in xrange(2):
    for pin in xrange(14):
        data = i * 0x10
        data += pin
        com.write(chr(data))
        

bkg = (255, 211, 0)
clr = (0, 0, 0)
squ = (8, 11, 134)

pygame.init()
size = (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Bloxy")
pygame.key.set_repeat(1, 1)
font = pygame.font.SysFont("Stencil", 20)
clock = pygame.time.Clock()

output = 0x00
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            output = 0x00
        elif event.type == pygame.KEYUP:
            output = 0x10
        else:
            continue

        if event.key == pygame.K_LEFT:
            output |= LEFT
        elif event.key == pygame.K_RIGHT:
            output |= RIGHT
        elif event.key == pygame.K_UP:
            output |= UP
        elif event.key == pygame.K_DOWN:
            output |= DOWN
        elif event.key == pygame.K_w:
            output |= W
        elif event.key == pygame.K_d:
            output |= D
        elif event.key == pygame.K_a:
            output |= A
        elif event.key == pygame.K_s:
            output |= S
        elif event.key == pygame.K_y:
            output |= Y
        elif event.key == pygame.K_g:
            output |= G
        elif event.key == pygame.K_j:
            output |= J
        elif event.key == pygame.K_h:
            output |= H
        com.write(chr(output))
        print hex(output)

    keys_pressed = pygame.key.get_pressed()

    if keys_pressed[pygame.K_LEFT]:
        x -= 5
    if keys_pressed[pygame.K_RIGHT]:
        x += 5
    if keys_pressed[pygame.K_UP]:
        y -= 5
    if keys_pressed[pygame.K_DOWN]:
        y += 5

    if x > 800:
        x = 0
    if x < 0:
        x = 800
    if y > 600:
        y = 0
    if y < 0:
        y = 600

    screen.fill(bkg)
    text = font.render('(' + str(x) + ',' + str(y) + ')', True, clr)
    screen.blit(text, [10, 10])
    pygame.draw.rect(screen, squ, [x - 10, y - 10, 20, 20])

    pygame.display.flip()
    clock.tick(60)
