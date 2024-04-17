import time
import pygame
import random
import math

fps = 60
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))

white = (255, 255, 255)
BACKGROUNDCLR = (0, 52, 102)

ground_scroll = 0
scroll_speed = 3
pipe_frequency = 3000  # Milliseconds
pass_pipe = False
last_pipe = pygame.time.get_ticks() - pipe_frequency
flying = False
game_over = False
score = 0
live = True
revive = False
default_Speed = 7
Boost = 30
Count = 0
AllMovementSpeed = False
BGx = 0
BGxdp = 0

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')
    default_font = pygame.font.Font('assets/fonts/flappy-bird.ttf', 60)
    game_sounds = {
        'click': pygame.mixer.Sound('assets/sounds/click.wav'),
        'die': pygame.mixer.Sound('assets/sounds/die.wav'),
        'point': pygame.mixer.Sound('assets/sounds/Score-hit.wav'),
        'jump': pygame.mixer.Sound('assets/sounds/whoosh.wav'),
        'whoosh': pygame.mixer.Sound('assets/sounds/air-whoosh.wav')
    }
    game_images = {
        'background': pygame.image.load('assets/images/Backgroundnyan.png').convert_alpha(),
        'background1': pygame.image.load('assets/images/backgroundnyan.png').convert_alpha(),
        'ground': pygame.image.load('assets/images/ground.png').convert_alpha(),
        'logo': pygame.image.load('assets/images/logonyan.png').convert_alpha(),
        'score_menu': pygame.image.load('assets/images/Menu.png').convert_alpha(),
        'restart_button': pygame.image.load('assets/images/Start-button.png').convert_alpha(),
        'pipe': pygame.image.load('assets/images/pipenyan.png').convert_alpha()
    }

    def round_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier

    def Reset():
        global AllMovementSpeed, Count
        AllMovementSpeed = False
        Count = 0 


    def draw_text(text, font, text_col, x, y):
        new_text = font.render(text, True, text_col)
        screen.blit(new_text, (x, y))


    def reset_game():
        pipe_group.empty()
        flappy.rect.x = 100
        flappy.rect.y = int(screen_height / 2)
        new_score = 0
        return new_score


    class Bird(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.images = []
            self.index = 0
            self.counter = 0
            for num in range(1, 4):
                img = pygame.image.load(f'assets/images/nyan{num}.png').convert_alpha()
                self.images.append(img)
            self.image = self.images[self.index]
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]
            self.vel = 0
            self.clicked = False

        def update(self):
            if flying:
                # Gravity
                self.vel += 0.5
                if self.vel > 8:
                    self.vel = 8
                if self.rect.bottom < 768:
                    self.rect.y += int(self.vel)

            if not game_over:
                # Jump
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                    self.clicked = True
                    self.vel = 0
                    self.vel -= 10
                    game_sounds['jump'].play()

                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

                # Handle The Animation
                self.counter += 1
                flap_cooldown = 5

                if self.counter > flap_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images):
                        self.index = 0
                self.image = self.images[self.index]

                # Rotate The Bird
                self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
            else:
                self.image = pygame.transform.rotate(self.images[self.index], -90)


    class Pipe(pygame.sprite.Sprite):
        def __init__(self, x, y, position):
            pygame.sprite.Sprite.__init__(self)
            self.image = game_images['pipe']
            self.rect = self.image.get_rect()
            # Position 1 Is From The Top, -1 Is From The Bottom
            if position == 1:
                pipe_gap = random.randint(150, 300)
                self.image = pygame.transform.flip(self.image, False, True)
                self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
            if position == -1:
                pipe_gap = random.randint(150, 300)
                self.rect.topleft = [x, y + int(pipe_gap / 2)]

        def update(self):
            self.rect.x -= scroll_speed
            if self.rect.x < -78:
                self.kill()


    class RestartButton:
        def __init__(self, x, y, image):
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

        def draw(self):
            action = False

            # Get Mouse Position
            pos = pygame.mouse.get_pos()

            # Check If Mouse Is Over The Button
            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1:
                    action = True
                    game_sounds['click'].play()

            # Draw Button
            screen.blit(self.image, (self.rect.x, self.rect.y))

            return action

    def Dash(On):
        global AllMovementSpeed
        global Count
        global scroll_speed
        global default_Speed
        if On:
            print("ok")
            AllMovementSpeed = True
        if AllMovementSpeed:
            HalfFPS = fps//2
            Count += 1
            if Count < HalfFPS/4:
                scroll_speed += Boost/round_down(HalfFPS/4)
            elif Count > HalfFPS/4 and Count < 3*(HalfFPS/4):
                scroll_speed = default_Speed+Boost
            elif Count > 3*(HalfFPS/4) and Count < HalfFPS:
                scroll_speed -= Boost/round_down(HalfFPS/4)
        if Count == fps//2:
            print("1")
            AllMovementSpeed = False
            Count = 0
            scroll_speed = default_Speed
        On = False
        #print(Count)


    bird_group = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()

    flappy = Bird(100, int(screen_height / 2))
    floppy = Bird(100, int(screen_height / 2))

    bird_group.add(flappy)

    # Create Restart Button Instance
    restart_button = RestartButton(screen_width // 2 - 107, screen_height // 2 + 118, game_images['restart_button'])
    Whoosh_sound = pygame.mixer.Sound(game_sounds['whoosh'])

    run = True
    while run:

        clock.tick(fps)
        screen.fill(BACKGROUNDCLR)

        # Draw Background
        if BGx + game_images['background'].get_width() <= screen_width:
            BGx = -60
        BGy = flappy.rect.y//10
        screen.blit(game_images['background'], (BGx, screen_height - game_images['background'].get_height() - BGy -40))

        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)

        # Draw The Ground
        if BGx + game_images['ground'].get_width() <= screen_width:
            BGy = flappy.rect.y//10
        screen.blit(game_images['ground'], (ground_scroll, screen_height - game_images['ground'].get_height() - BGy + 60))

        draw_text(str(score), default_font, white, int(screen_width / 2), 20)

        # Check The Score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe is False:
                pass_pipe = True
            if pass_pipe:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    game_sounds['point'].play()
                    score += 1
                    pass_pipe = False

        # Look For Collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True

        # Check If Bird Has Hit The Ground
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        if game_over is False and flying is True:
            # Generate New Pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            # Draw And Scroll The Ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()

        # Check For Game Over And Reset
        if game_over is True:
            screen.blit(game_images['background1'], (screen_width * 0, screen_height * 0))
            screen.blit(game_images['score_menu'], (screen_width // 2 - 89, screen_height // 2 - 174))
            size = (478, 129)
            game_over_logo = pygame.transform.scale(game_images['logo'], size)
            screen.blit(game_over_logo, (193, 74))
            draw_text("{}".format(score), default_font, white, 415, 355)
            if live:
                game_sounds['die'].play()
                live = False
            if restart_button.draw() is True:
                game_over = False
                game_sounds['jump'].set_volume(0)
                if not revive:
                    time.sleep(1)
                    game_sounds['jump'].set_volume(1)
                    revive = True
                if not live:
                    live = True
                score = reset_game()
                if revive is True:
                    revive = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and flying is False and game_over is False:
                flying = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    Whoosh_sound.play()
                    Dash(True)
        Dash(False)

        pygame.display.update()

    pygame.quit()
