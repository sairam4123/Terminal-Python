import pygame
import random
from pygame import math
from math import copysign


def signi(i: float) -> int:
    if i == 0:
        return 0
    return copysign(1, i)


def particle_smoothing(x: float) -> float:
    if x < 0.01:
        return x
    return x**-1 / 100


pygame.init()

num = 100
screen = pygame.display.set_mode((640, 480))

circles = [[random.randint(40, 600), random.randint(40, 440)] for _ in range(num)]
velocities = [[0, 50] for _ in range(num)]
colors = [
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for _ in range(num)
]
sizes = [7 for _ in range(num)]
collisions = [[False, False] for _ in range(num)]

clock = pygame.time.Clock()

should_quit = False
while not should_quit:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.constants.QUIT:
            should_quit = True

    screen.fill((255, 255, 255))
    delta = clock.tick(120) / 1000
    mouse_pos = pygame.mouse.get_pos()
    btn_press = pygame.mouse.get_pressed()
    cir_dir = 1 if btn_press[0] > 0 else -1 if btn_press[-1] > 0 else 0

    for i in range(len(circles)):
        if 0 > (circles[i][0] - sizes[i]) or (circles[i][0] + sizes[i]) > 640:
            if not collisions[i][0]:
                velocities[i][0] = -velocities[i][0] * 0.89
                # colors[i] = (
                #     random.randint(0, 255),
                #     random.randint(0, 255),
                #     random.randint(0, 255),
                # )
                collisions[i][0] = True
        else:
            collisions[i][0] = False

        if 0 > (circles[i][1] - sizes[i]) or (circles[i][1] + sizes[i]) > 480:
            if not collisions[i][1]:
                velocities[i][1] = -velocities[i][1] * 0.89
                # colors[i] = (
                #     random.randint(0, 255),
                #     random.randint(0, 255),
                #     random.randint(0, 255),
                # )
                collisions[i][1] = True
        else:
            collisions[i][1] = False

        circles[i][0] += velocities[i][0] * delta
        circles[i][1] += velocities[i][1] * delta

        # Gravity
        velocities[i][1] += 9.8 * delta

        # Air friction
        velocities[i][0] -= -signi(velocities[i][0]) * 0.02 * delta
        velocities[i][1] -= -signi(velocities[i][1]) * 0.02 * delta

        # Mouse Force
        dir = math.Vector2(circles[i]) - math.Vector2(mouse_pos)
        velocities[i][0] += (
            -dir.normalize().x
            * 100
            * dir.length()
            * delta
            * (dir.length() < 50)
            * cir_dir
        )
        velocities[i][1] += (
            -dir.normalize().y
            * 100
            * dir.length()
            * delta
            * (dir.length() < 50)
            * cir_dir
        )

        for circle in circles:
            distance = (math.Vector2(circle) - math.Vector2(circles[i])).length()
            infl = particle_smoothing(distance) * (distance < 20)
            velocities[i][0] += -velocities[i][0] * infl * 1 * delta
            velocities[i][1] += -velocities[i][1] * infl * 1 * delta

        # velocities[i][0] += (
        #     -sum([velocities[j][0] for j in range(num) if i != j]) / (num - 1)
        # ) * delta
        # velocities[i][1] += (
        #     -sum([velocities[j][1] for j in range(num) if i != j]) / (num - 1)
        # ) * delta

    for circle, size, color in zip(circles, sizes, colors):
        pygame.draw.circle(screen, color, circle, size)

    pygame.display.flip()
