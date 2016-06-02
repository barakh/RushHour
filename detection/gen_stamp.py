<<<<<<< HEAD
import pygame
from detection import HUE_MAX, DIFFERENT_COLORS
import colorsys

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

WIDTH = 330
LENGTH = 770

COLORS = [int(HUE_MAX * (float(i)+0.5)/DIFFERENT_COLORS)
          for i in range(DIFFERENT_COLORS)]

SAT = 1.0
VAL = 1.0

def draw_car(screen, pos, color_pair):
    x = pos[0]
    y = pos[1]

    h0 = float(color_pair[0])/HUE_MAX
    h1 = float(color_pair[1])/HUE_MAX

    sat = SAT
    val = VAL

    color0 = tuple([c * 255 for c in colorsys.hsv_to_rgb(h0, sat, val)])
    color1 = tuple([c * 255 for c in colorsys.hsv_to_rgb(h1, sat, val)])

    points = [(x-WIDTH/2, y-LENGTH/2),
              (x+WIDTH/2, y-LENGTH/2),
              (x+WIDTH/2, y),
              (x-WIDTH/2, y)]

    pygame.draw.polygon(screen, color0, points)

    points = [(x-WIDTH/2, y),
              (x+WIDTH/2, y),
              (x+WIDTH/2, y+LENGTH/2),
              (x-WIDTH/2, y+LENGTH/2)]

    pygame.draw.polygon(screen, color1, points)

if __name__ == '__main__':
    pygame.init()

    clock = pygame.time.Clock()

    screen_width = 2310 # int(WIDTH * DIFFERENT_COLORS * 1.5)
    screen_length = 3190 # int(LENGTH * DIFFERENT_COLORS * 1.2)

    width_space_ratio = 0.9
    len_space_ratio = 0.7
    screen = pygame.display.set_mode((screen_width, screen_length))

    done = False
    while not done:
        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)

        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop

        screen.fill(WHITE)

        x_pos = WIDTH * (0.5 + width_space_ratio)
        y_pos = LENGTH * (0.5 + len_space_ratio)
        for color0_ind, color0 in enumerate(COLORS):
            for color1 in COLORS[(color0_ind+1):]:
                draw_car(screen, (x_pos, y_pos), (color0, color1))
                x_pos += WIDTH * (1 + width_space_ratio)
                if x_pos >= screen_width * 0.9:
                    x_pos = WIDTH * (0.5 + width_space_ratio)
                    y_pos += LENGTH * (1 + len_space_ratio)

        pygame.display.flip()

    pygame.image.save(screen, "cars_{0}_colors.png".format(DIFFERENT_COLORS))
    # pygame.image.save(screen, "cars_hsv_s_{0}_v_{1}.png".format(SAT, VAL))

=======
import pygame
from detection import HUE_MAX, DIFFERENT_COLORS
import colorsys

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

WIDTH = 330
LENGTH = 770

COLORS = [int(HUE_MAX * (float(i)+0.5)/DIFFERENT_COLORS)
          for i in range(DIFFERENT_COLORS)]

SAT = 1.0
VAL = 1.0

def draw_car(screen, pos, color_pair):
    x = pos[0]
    y = pos[1]

    h0 = float(color_pair[0])/HUE_MAX
    h1 = float(color_pair[1])/HUE_MAX

    sat = SAT
    val = VAL

    color0 = tuple([c * 255 for c in colorsys.hsv_to_rgb(h0, sat, val)])
    color1 = tuple([c * 255 for c in colorsys.hsv_to_rgb(h1, sat, val)])

    points = [(x-WIDTH/2, y-LENGTH/2),
              (x+WIDTH/2, y-LENGTH/2),
              (x+WIDTH/2, y),
              (x-WIDTH/2, y)]

    pygame.draw.polygon(screen, color0, points)

    points = [(x-WIDTH/2, y),
              (x+WIDTH/2, y),
              (x+WIDTH/2, y+LENGTH/2),
              (x-WIDTH/2, y+LENGTH/2)]

    pygame.draw.polygon(screen, color1, points)

if __name__ == '__main__':
    pygame.init()

    clock = pygame.time.Clock()

    screen_width = 2310 # int(WIDTH * DIFFERENT_COLORS * 1.5)
    screen_length = 3190 # int(LENGTH * DIFFERENT_COLORS * 1.2)

    width_space_ratio = 0.9
    len_space_ratio = 0.7
    screen = pygame.display.set_mode((screen_width, screen_length))

    done = False
    while not done:
        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)

        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop

        screen.fill(WHITE)

        x_pos = WIDTH * (0.5 + width_space_ratio)
        y_pos = LENGTH * (0.5 + len_space_ratio)
        for color0_ind, color0 in enumerate(COLORS):
            for color1 in COLORS[(color0_ind+1):]:
                draw_car(screen, (x_pos, y_pos), (color0, color1))
                x_pos += WIDTH * (1 + width_space_ratio)
                if x_pos >= screen_width * 0.9:
                    x_pos = WIDTH * (0.5 + width_space_ratio)
                    y_pos += LENGTH * (1 + len_space_ratio)

        pygame.display.flip()

    pygame.image.save(screen, "cars_{0}_colors.png".format(DIFFERENT_COLORS))
    # pygame.image.save(screen, "cars_hsv_s_{0}_v_{1}.png".format(SAT, VAL))

>>>>>>> 6b54dfb619b8f501a0a77dd58eaf8e97feabac75
    pygame.quit()