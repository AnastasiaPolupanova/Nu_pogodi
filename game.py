import pygame
from pygame import sprite, image, freetype, Color
from pygame.constants import *
import enum
import random
import math


class Wolf(sprite.Sprite):
    def __init__(self, player_position):
        sprite.Sprite.__init__(self)
        self._bodyLeft = image.load('data/WolfBodyLeft.png')
        self._bodyRight = image.load('data/WolfBodyRight.png')
        self._armDownLeft = image.load('data/armDownLeft.png')
        self._armDownRight = image.load('data/armDownRight.png')
        self._armUpLeft = image.load('data/armUpLeft.png')
        self._armUpRight = image.load('data/armUpRight.png')

        self._player_position = player_position
        self._arms_position = (0, 0)

        self.BodyIsLeft = True
        self.ArmsAreUp = True

    def try_catch_egg(self, egg):
        if egg.egg_location == Egg.EggLocation.LEFT_UP:
            return self.BodyIsLeft and self.ArmsAreUp
        elif egg.egg_location == Egg.EggLocation.LEFT_DOWN:
            return self.BodyIsLeft and not self.ArmsAreUp
        elif egg.egg_location == Egg.EggLocation.RIGHT_UP:
            return not self.BodyIsLeft and self.ArmsAreUp
        else:
            return not self.BodyIsLeft and not self.ArmsAreUp

    def draw(self, screen):
        if self.BodyIsLeft:
            screen.blit(self._bodyLeft, self._player_position)
            if self.ArmsAreUp:
                screen.blit(self._armUpLeft, self._arms_position)
            else:
                screen.blit(self._armDownLeft, self._arms_position)
        else:
            screen.blit(self._bodyRight, self._player_position)
            if self.ArmsAreUp:
                screen.blit(self._armUpRight, self._arms_position)
            else:
                screen.blit(self._armDownRight, self._arms_position)


class Egg(sprite.Sprite):
    class EggLocation(enum.Enum):
        LEFT_UP = 0
        LEFT_DOWN = 1
        RIGHT_UP = 2
        RIGHT_DOWN = 3

    EGG_POSITIONS = [None for enum_value in EggLocation]
    EGG_POSITIONS[EggLocation.LEFT_UP.value] = [(60, 120), (90, 140), (120, 160), (120, 370), (60, 370)]
    EGG_POSITIONS[EggLocation.LEFT_DOWN.value] = [(60, 260), (90, 275), (120, 290), (120, 370), (60, 370)]
    EGG_POSITIONS[EggLocation.RIGHT_UP.value] = [(520, 120), (495, 135), (460, 160), (460, 370), (520, 370)]
    EGG_POSITIONS[EggLocation.RIGHT_DOWN.value] = [(520, 260), (495, 270), (460, 290), (460, 370), (520, 370)]

    def __init__(self):
        self.image = None
        self.broken = False
        self.egg_location = Egg.EggLocation(random.randint(0, len(Egg.EGG_POSITIONS) - 1))
        self.positions = Egg.EGG_POSITIONS[self.egg_location.value]
        self.position_index = 0

    def update(self):
        super().update()
        self.position_index += 1

    def should_be_caught(self):
        return self.position_index == 3

    def make_broken(self):
        self.broken = True

    def gone(self):
        return (self.position_index == 5) or (self.broken and self.position_index == 4)

    def draw(self, screen):
        def load_image(filename, resize):
            sprite.Sprite.__init__(self)
            self.image = image.load(filename)
            if resize:
                self.image = pygame.transform.smoothscale(self.image, (40, 60))

        if not self.broken:
            if self.position_index == 0:
                load_image('data/newEgg.png', False)
            elif self.position_index == 3:
                load_image('data/ChickenArrival.png', True)
            elif self.position_index == 4:
                if self.egg_location in [Egg.EggLocation.LEFT_UP, Egg.EggLocation.LEFT_DOWN]:
                    load_image('data/ChickenLeft.png', True)
                else:
                    load_image('data/ChickenRight.png', True)
        else:
            load_image('data/ChickenBoom.png', True)
        screen.blit(self.image, self.positions[self.position_index])


def main():
    class GameParameters:
        """ Синглтон, хранящий параметры игры """

        @classmethod
        def reset(cls, is_first_start=None):
            cls.RESOLUTION = (600, 450)
            cls.PLAYER_POSITION = (200, 100)
            cls.TIME_PER_STEP = 1500
            cls.Time = 0
            cls.Score = 0
            cls.Running = True
            cls.Paused = False
            cls.Lives = 3
            cls.HareWatching = False

            if is_first_start is not None:
                if is_first_start:
                    intro_text = ["Ну погоди!", "Игра всех времен и народов"]
                    fon = pygame.transform.smoothscale(image.load('data/GameBegin.jpg'), cls.RESOLUTION)
                else:
                    intro_text = ["Вы проиграли!", ]
                    fon = pygame.transform.smoothscale(image.load('data/GameOver.png'), cls.RESOLUTION)
                screen.blit(fon, (0, 0))
                font = pygame.font.Font(None, 40)
                if is_first_start:
                    top, left = 100, 100
                else:
                    top, left = 180, 180
                for line in intro_text:
                    string_rendered = font.render(line, 1, pygame.Color('red'))
                    intro_rect = string_rendered.get_rect()
                    intro_rect.top, intro_rect.left = top, left
                    screen.blit(string_rendered, intro_rect)
                    top += 50

                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise SystemExit("QUIT")
                        elif event.type in [KEYDOWN, MOUSEBUTTONDOWN]:
                            return
                    pygame.display.flip()

    def blit_text(text, pos):
        rendered_text = l_font.render(text, Color("#ff0000"))
        screen.blit(rendered_text[0], pos)

    GameParameters.reset()
    random.seed(None)
    pygame.init()
    l_font = pygame.freetype.Font(None, 20)
    screen = pygame.display.set_mode(GameParameters.RESOLUTION)
    pygame.display.set_caption("Ну, погоди!")
    bg = image.load("data/BackgroundScreen.png")
    chickens = image.load("data/chickens.png")
    hare = pygame.transform.smoothscale(image.load("data/Hare.png"), (100, 80))
    wolf = Wolf(GameParameters.PLAYER_POSITION)
    eggs = []
    timer = pygame.time.Clock()

    GameParameters.reset(True)
    # Главный цикл
    while True:
        # Обработка событий
        for e in pygame.event.get():
            if e.type == QUIT:
                raise SystemExit("QUIT")
            elif e.type == KEYDOWN:
                if e.key in [K_ESCAPE, K_PAUSE, K_p]:
                    GameParameters.Paused = not GameParameters.Paused
                if not GameParameters.Paused:
                    if e.key == K_LEFT:
                        wolf.BodyIsLeft = True
                    if e.key == K_RIGHT:
                        wolf.BodyIsLeft = False
                    if e.key == K_UP:
                        wolf.ArmsAreUp = True
                    if e.key == K_DOWN:
                        wolf.ArmsAreUp = False

        # Логика игры
        if GameParameters.Running:
            # Эволюция состояния игры (по сути, зайца и яиц) по времени
            if not GameParameters.Paused:
                GameParameters.Time += timer.get_time()
                if GameParameters.Time > GameParameters.TIME_PER_STEP / math.log(6 + GameParameters.Score, 6):
                    GameParameters.Time = 0
                    # Состояние зайца
                    if not GameParameters.HareWatching:
                        if random.random() < 1 / 3:
                            GameParameters.HareWatching = True
                    else:
                        if random.random() < 1 / 2:
                            GameParameters.HareWatching = False
                    # Состояние яиц
                    for egg in eggs.copy():
                        egg.update()
                        if egg.should_be_caught():  # Только один раз за итерацию главного цикла - максимум
                            if wolf.try_catch_egg(egg):
                                GameParameters.Score += 1
                                eggs.remove(egg)
                            else:
                                if GameParameters.HareWatching:
                                    GameParameters.Lives -= 0.5
                                else:
                                    GameParameters.Lives -= 1
                                    if not GameParameters.HareWatching:
                                        egg.make_broken()
                                GameParameters.Running = GameParameters.Lives > 0
                        if egg.gone():
                            eggs.remove(egg)
                    eggs.append(Egg())

            # Отрисовка фона, зайца, куриц, волка и яиц
            screen.blit(bg, (0, 0))
            screen.blit(chickens, (0, 0))
            if GameParameters.HareWatching:
                screen.blit(hare, (350, 100))
            wolf.draw(screen)
            for egg in eggs:
                egg.draw(screen)
            # Отрисовка счёта, количества жизней, сообщения о паузе, сообщения о конце игры
            blit_text("Счёт: {}".format(GameParameters.Score), (50, 20))
            blit_text("Жизней: {}".format(max(GameParameters.Lives, 0)), (450, 20))
            if GameParameters.Paused:
                blit_text("ПАУЗА", (270, 20))
            if not GameParameters.Running:
                GameParameters.reset(False)
                eggs = []

            pygame.display.update()
            timer.tick(50)


if __name__ == "__main__":
    main()
