#!/usr/bin/env python3

"""
My Spacer program. Author david-emm. Last mod: 30/08/22.
Written to play on a Linux system. but should be OK on Windows.

A Space ship based game built as an exercise using pygame and set up to use
all of the available display screen, up to 1920 x 1080. If you want a frame
with a title remove pg.FULLSCREEN in line 272/3. Requires the following imports
to be installed: pygame, os, random.

Controls.
LEFT arrow and RIGHT arrow, when pressed, turn the space ship on it's centre.
UP arrow, when pressed, turns on thrust in the forward direction only. Note
thrust stops when UP arrow is released. The ship also stops which is not what
really happens in space!

The space bar, when pressed, fires a laser missile.

The number of laser missiles is shown in the Laser bar and is initially
200 missiles. Hitting the gold asteroid reloads missiles.

Initially you have 4 lives - remaining lives are shown as mini space ships.

Press the 'B' key to start the game.
"""

# pylint: disable=no-member

# These are the import statements
import os
from os import path
import random
import pygame as pg

os.environ['SDL_VIDEO_CENTERED'] = '1'
vec = pg.math.Vector2

"""These are the initial constants"""
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
FONT_NAME = 'arial'
FPS = 60
SHIP_ROT_SPEED = 20
SHIP_VEL = 35
BULLET_VEL = 50
ROCK_VEL = 5
WEAPON_OFFSET = vec(40, 0)
AST_RANGE = 7
POWERUP_PCT = 3
HS_FILE = "highscore.txt"

"""Now set layers - instructs pygame which layer to put on top"""
EXPLOSION_LAYER = 3
SHIP_LAYER = 2
BULLET_LAYER = 1
ROCK_LAYER = 1

class Ship(pg.sprite.Sprite):
    """Load Ship class."""

    def __init__(self, game, x, y, dt):
        x = int(x)
        y = int(y)
        self.groups = game.all_sprites
        self._layer = SHIP_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.angle = 0
        self.image = self.game.one_ship
        self.rect = self.image.get_rect()
        self.pos = (x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.rot_speed = 0
        self.vel = vec(0, 0)
        self.dt = dt
        self.energy = self.game.energy
        self.shoot_delay = 500
        self.last_shot = pg.time.get_ticks()

    def update(self):
        if self.energy > 50:
            self.shoot_delay = 250
        self.rot = (self.rot + self.rot_speed * self.dt) % 360
        self.image = pg.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.pos += self.vel * self.dt
        self.rect.center = int(self.pos.x), int(self.pos.y)
        """Wrap ship round screen."""
        self.rect.centerx %= self.game.WIDTH
        self.rect.centery %= self.game.HEIGHT

    def get_keys(self):
        self.image = self.game.one_ship
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.rot_speed = SHIP_ROT_SPEED
        if keys[pg.K_RIGHT]:
            self.rot_speed = -SHIP_ROT_SPEED
        if keys[pg.K_UP]:
            self.image = self.game.two_ship
            self.vel = vec(SHIP_VEL, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            direction = vec(1, 0).rotate(-self.rot)
            pos = self.rect.center + WEAPON_OFFSET.rotate(-self.rot)
            rot = self.rot
            Bullet(gm, pos, direction, rot, self.dt)
            self.game.fire_sound.play()
            self.energy -= 0.5
            if self.energy <= 0:
                self.game.playing = False

class Bullet(pg.sprite.Sprite):
    """Load Bullet class."""

    def __init__(self, game, pos, direction, rot, dt):
        self.groups = game.all_sprites, game.bullets
        self._layer = BULLET_LAYER
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = self.game.bullet
        self.dt = dt
        self.rot = rot
        self.image = pg.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = int(self.pos.x), int(self.pos.y)
        self.vel = direction * (SHIP_VEL + BULLET_VEL)

    def update(self):
        self.pos += self.vel * self.dt
        self.rect.center = int(self.pos.x), int(self.pos.y)
        """kill it if it moves off the screen"""
        if (self.rect.centerx > self.game.WIDTH or self.rect.centerx < 0
                or self.rect.centery > self.game.HEIGHT
                or self.rect.centery < 0):
            self.kill()

class Rocks(pg.sprite.Sprite):
    """Load Rocks class."""

    def __init__(self, game, dt):
        self.groups = game.all_sprites, game.rocks
        self._layer = ROCK_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_orig = random.choice(game.asteroid_images)
        self.image_index = game.asteroid_images.index(self.image_orig)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.image = pg.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.angle = random.randrange(-3, 6)
        self.ast_rot_angle = random.randrange(-3, 3)
        self.dt = dt
        self.dir = vec(random.randrange(-10, -3), random.randrange(1, 5))
        self.rect = self.image.get_rect()
        self.pos = vec(self.game.WIDTH, random.randrange(1, 500))
        self.rect.center = int(self.pos.x), int(self.pos.y)
        self.vel = self.dir * ROCK_VEL
        self.size = self.image_index % 2

    def update(self):
        self.angle += self.ast_rot_angle
        self.angle = self.angle % 360
        self.image = self.image_orig.copy()
        self.image = pg.transform.scale(self.image, (60, 60))
        self.image = pg.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.pos += self.vel * self.dt
        self.rect.center = int(self.pos.x), int(self.pos.y)
        """Wrap rocks round screen"""
        self.rect.x %= self.game.WIDTH
        self.rect.y %= self.game.HEIGHT

class Ball(pg.sprite.Sprite):
    """Load Ball class."""

    def __init__(self, game, dt):
        self.groups = game.all_sprites, game.ball
        self._layer = ROCK_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_orig = game.g_ball
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.image = pg.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.angle = random.randrange(-3, 6)
        self.ast_rot_angle = random.randrange(-3, 3)
        self.dt = dt
        self.dir = vec(random.randrange(-10, -3), random.randrange(1, 5))
        self.rect = self.image.get_rect()
        self.pos = vec(int(self.game.WIDTH), int(random.randrange(1, 500)))
        self.rect.center = self.pos
        self.vel = self.dir * ROCK_VEL

    def update(self):
        self.angle += self.ast_rot_angle
        self.angle = self.angle % 360
        self.image = self.image_orig.copy()
        self.image = pg.transform.scale(self.image, (40, 40))
        self.image = pg.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.pos += self.vel * self.dt
        self.rect.center = self.pos
        if (self.rect.centerx > self.game.WIDTH or self.rect.centerx < 0
                or self.rect.centery > self.game.HEIGHT
                or self.rect.centery < 0):
            self.kill()

class Explosion(pg.sprite.Sprite):
    """Load Explosion class."""

    def __init__(self, game, center, size):
        self.groups = game.all_sprites, game.explosions
        self._layer = EXPLOSION_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = size
        self.frame = 0
        self.frame_rate = 20
        self.image = game.explosion_anim[self.size][self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Game:
    """Load Game class."""

    def __init__(self):
        """Get screen size and intilise sound settings and pygame.
           Initialise start variables.
        """
        pg.mixer.pre_init(44100, -16, 8, 1024)
        pg.init()
        pg.mouse.set_visible(False)
        infoObject = pg.display.Info()
        self.WIDTH = int(infoObject.current_w)
        self.HEIGHT = int(infoObject.current_h)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(FPS) / 100.0
        self.screentime = 0
        self.wtime = int(self.screentime / 20 % self.WIDTH)
        self.running = True
        self.screen = pg.display.set_mode(
            (self.WIDTH, self.HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption("Asteroids")
        self.playing = None
        self.load_images()

    def load_images(self):
        """Load all game graphics."""
        folder = path.join(path.dirname(__file__), 'img')
        try:
            self.dir = path.dirname(__file__)
            try:
                with open(path.join(self.dir, HS_FILE), 'r') as f:
                    self.highscore = int(f.read())
            except IOError:
                print("No file highscore.txt found")
                self.highscore = 0
            self.stars = pg.image.load(os.path.join(
                folder, 'stars.png')).convert()
            self.debris = pg.image.load(os.path.join(
                folder, 'debris.png')).convert_alpha()
            self.one_ship = pg.image.load(os.path.join(
                folder, 'one_ship.png')).convert()#
            self.one_ship.set_colorkey(BLACK)  # black is transparent
            self.two_ship = pg.image.load(os.path.join(
                folder, 'two_ship.png')).convert()
            self.two_ship.set_colorkey(BLACK)  # black is transparent
            self.little_ship = pg.image.load(
                os.path.join(folder, 'mini_one_ship.png')).convert()
            self.little_ship.set_colorkey(BLACK)  # black is transparent
            self.bullet = pg.image.load(os.path.join(
                folder, 'laser_bullet.png')).convert()
            self.bullet.set_colorkey(BLACK)  # black is transparent
            self.g_ball = pg.image.load(
                os.path.join(folder, 'Gold_ball.png')).convert()
            self.g_ball.set_colorkey(BLACK)
            self.asteroid_list = ['asteroid-1.png',
                                  'asteroid-2.png',
                                  'asteroid-3.png',
                                  'asteroid-4.png',
                                  'asteroid-5.png',
                                  'asteroid-6.png',
                                  'asteroid-7.png']
            self.asteroid_images: str = []
            for ast in self.asteroid_list:
                self.asteroid_images.append(pg.image.load(
                    os.path.join(folder, ast)).convert())
            exp_frames = []
            self.explosion_anim: str = {}
            self.explosion_anim[0] = []
            self.explosion_anim[1] = []
            self.explosion_anim[2] = []
            image = pg.image.load(
                os.path.join(folder, 'explosion.png')).convert_alpha()
            width, height = image.get_size()
            w, h = 64, 64
            for i in range(int(height / h)):
                for j in range(int(width / w)):
                    exp_frames.append(image.subsurface((j * w, i * h, w, h)))
            for count in range(len(exp_frames)):
                img_lg = pg.transform.scale(exp_frames[count], (75, 75))
                self.explosion_anim[0].append(img_lg)
                img_sm = pg.transform.scale(exp_frames[count], (40, 40))
                self.explosion_anim[1].append(img_sm)
                img_end = pg.transform.scale(exp_frames[count], (100, 100))
                self.explosion_anim[2].append(img_end)

        except OSError as err:
            print("OS error: {0}".format(err))
        self.load_sounds()

    def load_sounds(self):
        """Load all sound files."""
        self.snd_dir = path.join(self.dir, 'snd')
        self.fire_sound = pg.mixer.Sound(path.join(self.snd_dir, 'laser.ogg'))
        self.fire_sound.set_volume(0.25)
        self.explosion_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'rumble.ogg'))
        self.explosion_sound.set_volume(0.25)

    def new(self):
        """Initialise all groups."""
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.bullets = pg.sprite.Group()
        self.rocks = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.ball = pg.sprite.Group()

        """These are the initial game variables and game controls."""
        self.my_lives = 3
        self.my_score = 0
        self.energy = 100
        self.rock_timer = 0
        self.ship = Ship(self, self.WIDTH / 2, self.HEIGHT / 2, self.dt)
        self.run()

    def run(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'space.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.6)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        """Check for end event."""
        for event in pg.event.get():
            if (event.type == pg.QUIT or event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE):
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        """Update main game loop."""
        self.screentime += 1
        self.wtime = int(self.screentime / 20 % self.WIDTH)
        self.ship.get_keys()
        self.ship.update()
        self.bullets.update()
        self.rocks.update()
        self.explosions.update()
        self.ball.update()

        """Spawn rocks."""
        now = pg.time.get_ticks()
        if len(self.rocks.sprites()) < AST_RANGE:
            if now - self.rock_timer > 500 + random.choice(
                    [-50, 0, 50, 100, 150]):
                self.rock_timer = now
                Rocks(gm, self.dt)

        """Check to see if a rock hits the ship."""
        rock_hits = pg.sprite.spritecollide(
            self.ship, self.rocks, True, pg.sprite.collide_rect_ratio(0.5))
        if rock_hits:
            self.explosion_sound.play()
            Explosion(gm, self.ship.rect.center, 1)
            self.my_lives -= 1
            if self.my_lives == 0:
                self.explosion_sound.play()
                # Explosion(gm, self.ship.rect.center, 2)
                self.playing = False

        """Check to see if a bullet hit a rock."""
        bullet_hits = pg.sprite.groupcollide(
            self.rocks, self.bullets, True, True,
            pg.sprite.collide_circle_ratio(0.5))
        for hit in bullet_hits:
            Explosion(gm, hit.rect.center, 0)
            self.explosion_sound.play()
            self.my_score += 10

        """Spawn energy ball."""
        if not self.ball and self.ship.energy < 50 and random.randrange(
                100) < POWERUP_PCT:
            Ball(gm, self.dt)

        """Check to see if a bullet hit an energy ball."""
        ball_hits = pg.sprite.groupcollide(
            self.ball, self.bullets, True, True,
            pg.sprite.collide_circle_ratio(0.5))
        for hit in ball_hits:
            Explosion(gm, hit.rect.center, 0)
            self.explosion_sound.play()
            self.ship.energy = 100

    def draw(self):
        """Draw game screen."""
        self.screen.blit(self.stars, (0, 0))
        self.screen.blit(self.debris, ((self.wtime - self.WIDTH), 0))
        self.screen.blit(self.debris, (self.wtime, 0))
        self.draw_lives(self.screen, 120, 30, self.my_lives, self.little_ship)
        self.draw_text("Laser Missiles: ", 22, WHITE, self.WIDTH - 330, 36)
        self.draw_energy_bar(
            self.screen, self.WIDTH - 250, 40, self.ship.energy)
        self.draw_text("Score: " + str(
            self.my_score), 22, WHITE, self.WIDTH / 2, 15)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def show_start_screen(self):
        """Game splash/start screen."""
        pg.mixer.music.load(path.join(self.snd_dir, 'start.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.3)
        self.screen.blit(self.stars, (0, 0))
        self.screen.blit(
            self.one_ship, (self.WIDTH // 2 - 50, self.HEIGHT // 4))
        self.draw_text(
            "Left arrow turns ship left. Right arrow turns ship right.",
            22, WHITE, self.WIDTH / 2, self.HEIGHT / 2)
        self.draw_text(
            "Up arrow accelerates ship.",
            22, WHITE, self.WIDTH // 2, self.HEIGHT // 2 + 45)
        self.draw_text(
            "Space bar fires missile.",
            22, WHITE, self.WIDTH // 2, self.HEIGHT // 2 + 90)
        self.draw_text(
            "Press the 'B' key to play",
            22, WHITE, self.WIDTH // 2, self.HEIGHT * 3 // 4)
        self.draw_text(
            "Or press the 'Esc' key to end",
            22, WHITE, self.WIDTH // 2, self.HEIGHT * 3 // 4 + 45)
        self.draw_text(
            "Highest Score: " + str(self.highscore),
            22, WHITE, self.WIDTH // 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_end_screen(self):
        """Draw game over/continue screen."""
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'start.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.3)
        self.screen.blit(self.stars, (0, 0))
        self.screen.blit(self.one_ship, (
            self.WIDTH // 2 - 50, self.HEIGHT // 4))
        self.draw_text(
            "GAME OVER", 48, WHITE, self.WIDTH // 2, self.HEIGHT // 4 + 100)
        self.draw_text(
            "Score: " + str(self.my_score), 22, WHITE,
            self.WIDTH // 2, self.HEIGHT // 2)
        self.draw_text(
            "Press the 'B' key to play again", 22, WHITE,
            self.WIDTH / 2, self.HEIGHT * 3 // 4)
        self.draw_text(
            "Or press the 'Esc' key to end", 22, WHITE,
            self.WIDTH // 2, self.HEIGHT * 3 // 4 + 45)
        if self.my_score > self.highscore:
            self.highscore = self.my_score
            self.draw_text(
                "NEW HIGH SCORE!", 22, WHITE, self.WIDTH // 2,
                self.HEIGHT // 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.my_score))
        else:
            self.draw_text("High Score: " + str(
                self.highscore), 22, WHITE,
                           self.WIDTH / 2, self.HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        """Waiting for key press to clear start and end game screens."""
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if (event.type == pg.QUIT or event.type == pg.KEYDOWN
                        and event.key == pg.K_ESCAPE):
                    waiting = False
                    self.running = False
                if (event.type == pg.KEYDOWN
                        and event.key == pg.K_b):
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        """Now add text to display."""
        x = int(x)
        y = int(y)
        size = int(size)
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_lives(self, surf, x, y, lives, pic):
        """Now add little ship images for lives display."""
        for life in range(lives):
            img_rect = pic.get_rect()
            img_rect.x = x + 50 * life
            img_rect.y = y
            surf.blit(pic, img_rect)

    def draw_energy_bar(self, surf, x, y, pct):
        """Now add energy bar."""
        if pct < 0:
            pct = 0
        bar_length = 200
        bar_height = 20
        fill = int((pct / 100) * bar_length)
        outline_rect = pg.Rect(int(x), int(y), bar_length, bar_height)
        fill_rect = pg.Rect(int(x), int(y), fill, bar_height)
        if pct >= 66:
            pg.draw.rect(surf, GREEN, fill_rect)
            pg.draw.rect(surf, WHITE, outline_rect, 1)
        elif pct >= 33:
            pg.draw.rect(surf, ORANGE, fill_rect)
            pg.draw.rect(surf, WHITE, outline_rect, 1)
        else:
            pg.draw.rect(surf, RED, fill_rect)
            pg.draw.rect(surf, WHITE, outline_rect, 1)

#Create the game object and start.
gm = Game()
gm.show_start_screen()
while gm.running:
    gm.new()
    gm.show_end_screen()

#End of game.
pg.quit()
