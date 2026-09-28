import pygame
import random
import math
import asyncio
from pygame.math import Vector2

WIDTH, HEIGHT = 1400, 900
NUM_ASTEROIDS = 1

class Asteroid:
    def __init__(self, x, v, r):
        self.x = x
        self.v = v
        self.r = r

    def m(self):
        return self.r**2

class Missile:
    def __init__(self, x, v):
        self.x = x
        self.v = v

class Ship:
    def __init__(self, x, v, a, w, accel, drag = 1):
        self.x = x
        self.v = v
        self.a = a
        self.w = w
        self.accel = accel
        self.drag = drag


asteroids = []

async def run(screen, clock, player_image, enemy_image):
    global asteroids
    asteroids = [Asteroid(Vector2(random.uniform(100, WIDTH - 100), random.uniform(100, HEIGHT - 100)), Vector2(random.uniform(-3, 3), random.uniform(-3, 3)), random.uniform(6, 24)) for _ in range(NUM_ASTEROIDS)]
    enemies = [Ship(Vector2(100, 100), Vector2(0, 0), random.uniform(0, 360), 0, 1, .8), Ship(Vector2(WIDTH-100, 100), Vector2(0, 0), random.uniform(0, 360), 0, 1, .8), Ship(Vector2(WIDTH - 100, HEIGHT - 100), Vector2(0, 0), random.uniform(0, 360), 0, 1, .8), Ship(Vector2(100, HEIGHT - 100), Vector2(0, 0), random.uniform(0, 360), 0, 1, .8)]
    missiles = []
    player = Ship(Vector2(WIDTH/2, HEIGHT/2), Vector2(0, 0), 0, 0, .5, .95)

    running = True
    for a in asteroids:
        if player.x.distance_to(a.x) < 3 * a.r:
            a.x += (a.x - player.x).normalize() * (3 * a.r - (a.x-player.x).length())
        a.v = (a.x - player.x).normalize() * a.v.length()
        
    while running and asteroids:
        target = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and asteroids:
                target = Vector2(0, -1).rotate(-player.a) + player.x

        if random.randint(0, 200) == 67:
            enemies.append(Ship(Vector2(100, 100), Vector2(0, 0), random.uniform(0, 360), 0, 1, .8))

        if target:
            missiles.append(Missile(player.x.copy(), (target - player.x).normalize() * 7))
            target = None

        for m in missiles:
            m.x += m.v

        for a in asteroids:
            a.x += a.v

        for i in range (0, len(asteroids)):
            a = asteroids[i]
            for j in range(i+1, len(asteroids)):
                A = asteroids[j]
                if math.dist(a.x, A.x) < a.r + A.r and ((a.x - A.x).dot(a.v) < 0 or (A.x - a.x).dot(A.v) < 0):
                    unit = (a.x - A.x) / (a.x - A.x).length()
                    common = (2 / (a.m() + A.m())) * unit.dot(a.v - A.v) * unit
                    diff = (a.x - A.x) / (a.x-A.x).length() * min(0,a.r + A.r)
                    a.x -= diff
                    A.x += diff
                    a.v += -A.m() * common
                    A.v += a.m() * common

        for a in asteroids:
            if a.x.x - a.r < 0 or a.x.x + a.r > WIDTH:
                a.v.x *= -1
                a.x.x = max(a.r, min(a.x.x, WIDTH-a.r))
            elif a.x.y - a.r < 0 or a.x.y + a.r > HEIGHT:
                a.v.y *= -1
                a.x.y = max(a.r, min(a.x.y, HEIGHT-a.r))

        for m in missiles:
            flag = False
            for a in asteroids:
                if (m.x - a.x).length() < 3 + a.r:
                    flag = True
                    asteroids.remove(a)
            for e in enemies:
                if (m.x - e.x).length() < 30:
                    flag = True
                    enemies.remove(e)
            if flag:
                missiles.remove(m)

        for a in asteroids:
            if player.x.distance_to(a.x) < a.r + 20:
                running = False
        for e in enemies:
            if player.x.distance_to(e.x) < + 30:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.a += 5
        elif keys[pygame.K_RIGHT]:
            player.a -= 5
            
        if keys[pygame.K_UP]:   
            player.v += Vector2(0, -1).rotate(-player.a) * player.accel
            
        player.x += player.v
        player.x.x %= WIDTH
        player.x.y %= HEIGHT

        for e in enemies:
            if e.x.distance_squared_to(player.x) < 250000 and (e.x - player.x).normalize().dot(Vector2(0, -1).rotate(-e.a)) > .7:
                e.v += Vector2(0, 1).rotate(-e.a) * e.accel
                e.w -= 20/360 * Vector2(0, -1).rotate(-e.a).angle_to((e.x - player.x).normalize())
                e.v *= .95
            else:
                e.w = 1
                e.v += Vector2(0, 1).rotate(-e.a) * e.accel
                e.v *= e.drag
            e.x += e.v
            e.w *= e.drag
            e.a += e.w
            e.x.x %= WIDTH
            e.x.y %= HEIGHT
        
        screen.fill((0,0,0))

        for a in asteroids:
            pygame.draw.circle(screen, (128,128,128), a.x, a.r)
        for m in missiles:
            pygame.draw.circle(screen, (255, 0, 0), m.x, 3)
        for e in enemies:
            rotated_enemy = pygame.transform.rotate(enemy_image, e.a)
            enemy_rect = rotated_enemy.get_rect(center=(e.x.x, e.x.y))
            screen.blit(rotated_enemy, enemy_rect)
            
        rotated_ship = pygame.transform.rotate(player_image, player.a)
        ship_rect = rotated_ship.get_rect(center=(player.x.x, player.x.y))
        screen.blit(rotated_ship, ship_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    clock = pygame.time.Clock()
    player_image = pygame.image.load("assets/player.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (30, 60))
    enemy_image = pygame.image.load("assets/enemy.png").convert_alpha()
    enemy_image = pygame.transform.scale(enemy_image, (30, 30))

    while True:
        await run(screen, clock, player_image, enemy_image)

        if not pygame.get_init():
            break

        # Keep the browser event loop alive while showing the end screen.
        cont = True
        while cont:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    cont = False

            font = pygame.font.Font(None, 50)
            text_surface = font.render(
                "You Won! Press Space to play again..." if not asteroids
                else "You Died! Press Space to play again...",
                True,
                (255, 255, 255),
            )
            screen.fill((0, 0, 0))
            screen.blit(text_surface, (WIDTH / 2 - 250, HEIGHT / 2))
            pygame.display.flip()
            await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
