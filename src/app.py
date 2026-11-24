"""Модуль главного окна и цикла приложения игры «Астероид» на Pygame."""

import pygame

from src.models.game_model import GameModel, GameState
from src.renderers.game_renderer import GameRenderer


class AsteroidApp:
    """Управляет окном Pygame, вводом с клавиатуры и главным циклом."""

    def __init__(self, width: int = 800, height: int = 600, fps: int = 60) -> None:
        """Инициализирует Pygame, модель игры и рендерер.

        Args:
            width: Ширина игрового окна в пикселях.
            height: Высота игрового окна в пикселях.
            fps: Целевая частота кадров в секунду.
        """
        pygame.init()
        pygame.display.set_caption("Астероид")

        self.width = width
        self.height = height
        self.fps = fps
        self.is_running = False
        self._is_thrusting = False

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        self.model = GameModel(width=self.width, height=self.height)
        self.renderer = GameRenderer(width=self.width, height=self.height)

    def run(self) -> None:
        """Запускает главный цикл обработки событий, обновления и отрисовки."""
        self.is_running = True

        while self.is_running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
            pygame.display.flip()

        self.stop()

    def stop(self) -> None:
        """Останавливает цикл и корректно завершает работу Pygame."""
        self.is_running = False
        pygame.quit()

    def handle_events(self) -> None:
        """Обрабатывает системные события и одиночные нажатия клавиш."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_p:
                    self.model.toggle_pause()
                elif event.key in (pygame.K_RETURN, pygame.K_r):
                    if self.model.state in (GameState.MENU, GameState.GAME_OVER):
                        self.model.start_new_game()

    def update(self, dt: float) -> None:
        """Считывает зажатые клавиши управления и обновляет модель игры.

        Args:
            dt: Прошедшее время с предыдущего кадра в секундах.
        """
        keys = pygame.key.get_pressed()
        turn_left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
        turn_right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
        thrust = bool(keys[pygame.K_UP] or keys[pygame.K_w])
        fire = bool(keys[pygame.K_SPACE])

        self._is_thrusting = thrust and self.model.state == GameState.PLAYING

        self.model.step(
            dt=dt,
            turn_left=turn_left,
            turn_right=turn_right,
            thrust=thrust,
            fire=fire,
        )

    def render(self) -> None:
        """Отрисовывает текущий кадр через рендерер."""
        self.renderer.render(
            surface=self.screen,
            model=self.model,
            is_thrusting=self._is_thrusting,
        )
