"""Модуль отрисовки игрового мира, интерфейса и экранов состояния."""

import math
import random

import pygame

from src.models.entities import Asteroid, Ship
from src.models.game_model import GameModel, GameState


class GameRenderer:
    """Отвечает за визуализацию всех сущностей и HUD на поверхности Pygame."""

    BG_COLOR = (10, 14, 24)
    STAR_COLOR = (90, 105, 135)
    SHIP_COLOR = (241, 245, 249)
    THRUST_COLOR = (251, 146, 60)
    ASTEROID_COLOR = (148, 163, 184)
    BULLET_COLOR = (56, 189, 248)
    ACCENT_COLOR = (250, 204, 21)
    TEXT_COLOR = (226, 232, 240)
    SUBTEXT_COLOR = (148, 163, 184)

    def __init__(self, width: int, height: int) -> None:
        """Инициализирует шрифты и фоновое звёздное поле.

        Args:
            width: Ширина экрана в пикселях.
            height: Высота экрана в пикселях.
        """
        self.width = width
        self.height = height

        self.font_hud = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 46, bold=True)
        self.font_sub = pygame.font.SysFont("consolas", 20)

        rng = random.Random(42)
        self.stars: list[tuple[int, int, int]] = [
            (
                rng.randint(0, width - 1),
                rng.randint(0, height - 1),
                rng.choice([1, 1, 2]),
            )
            for _ in range(70)
        ]

    def render(
        self,
        surface: pygame.Surface,
        model: GameModel,
        is_thrusting: bool = False,
    ) -> None:
        """Отрисовывает полный кадр игры на заданной поверхности.

        Args:
            surface: Целевая поверхность экрана Pygame.
            model: Текущая модель состояния игры.
            is_thrusting: Включена ли тяга двигателя в текущем кадре.
        """
        surface.fill(self.BG_COLOR)
        self._draw_stars(surface)

        for asteroid in model.asteroids:
            self._draw_asteroid(surface, asteroid)

        for bullet in model.bullets:
            pygame.draw.circle(
                surface,
                self.BULLET_COLOR,
                (int(bullet.x), int(bullet.y)),
                int(bullet.radius),
            )

        if model.state in (GameState.PLAYING, GameState.PAUSED):
            self._draw_ship(surface, model.ship, is_thrusting)

        self._draw_hud(surface, model)

        if model.state == GameState.MENU:
            self._draw_center_overlay(
                surface,
                title="АСТЕРОИД",
                subtitle="Нажмите ENTER для старта  |  W/A/D или Стрелки, SPACE — огонь",
            )
        elif model.state == GameState.PAUSED:
            self._draw_center_overlay(
                surface,
                title="ПАУЗА",
                subtitle="Нажмите P для продолжения",
            )
        elif model.state == GameState.GAME_OVER:
            self._draw_center_overlay(
                surface,
                title="ИГРА ОКОНЧЕНА",
                subtitle=f"Итоговый счёт: {model.score}  |  ENTER или R — заново",
            )

    def _draw_stars(self, surface: pygame.Surface) -> None:
        """Рисует статичные фоновые звёзды."""
        for x, y, size in self.stars:
            pygame.draw.circle(surface, self.STAR_COLOR, (x, y), size)

    def _draw_ship(
        self, surface: pygame.Surface, ship: Ship, is_thrusting: bool
    ) -> None:
        """Рисует треугольный корпус корабля и факел двигателя."""
        # Мигание корабля во время временной неуязвимости после возрождения.
        if ship.invulnerable_timer > 0.0:
            if int(ship.invulnerable_timer * 12) % 2 == 0:
                return

        angle = ship.angle_rad
        r = ship.radius

        # Вершины корабля в полярных координатах относительно центра (ship.x, ship.y).
        nose = (ship.x + math.cos(angle) * r, ship.y + math.sin(angle) * r)
        left_wing = (
            ship.x + math.cos(angle + 2.45) * r,
            ship.y + math.sin(angle + 2.45) * r,
        )
        rear_notch = (
            ship.x + math.cos(angle + math.pi) * (r * 0.45),
            ship.y + math.sin(angle + math.pi) * (r * 0.45),
        )
        right_wing = (
            ship.x + math.cos(angle - 2.45) * r,
            ship.y + math.sin(angle - 2.45) * r,
        )

        pygame.draw.polygon(
            surface,
            self.SHIP_COLOR,
            [nose, left_wing, rear_notch, right_wing],
            width=2,
        )

        if is_thrusting:
            flame_len = r * random.uniform(0.95, 1.35)
            flame_tip = (
                ship.x + math.cos(angle + math.pi) * flame_len,
                ship.y + math.sin(angle + math.pi) * flame_len,
            )
            flame_left = (
                ship.x + math.cos(angle + 2.75) * (r * 0.65),
                ship.y + math.sin(angle + 2.75) * (r * 0.65),
            )
            flame_right = (
                ship.x + math.cos(angle - 2.75) * (r * 0.65),
                ship.y + math.sin(angle - 2.75) * (r * 0.65),
            )
            pygame.draw.polygon(
                surface, self.THRUST_COLOR, [flame_left, flame_tip, flame_right]
            )

    def _draw_asteroid(self, surface: pygame.Surface, asteroid: Asteroid) -> None:
        """Поворачивает локальные вершины астероида и рисует замкнутый полигон."""
        cos_a = math.cos(asteroid.rotation_angle)
        sin_a = math.sin(asteroid.rotation_angle)

        # Матрица поворота на угол alpha:
        # x' = x * cos(alpha) - y * sin(alpha), y' = x * sin(alpha) + y * cos(alpha).
        world_points: list[tuple[float, float]] = []
        for lx, ly in asteroid.vertices:
            wx = asteroid.x + (lx * cos_a - ly * sin_a)
            wy = asteroid.y + (lx * sin_a + ly * cos_a)
            world_points.append((wx, wy))

        if len(world_points) >= 3:
            pygame.draw.polygon(surface, self.ASTEROID_COLOR, world_points, width=2)

    def _draw_hud(self, surface: pygame.Surface, model: GameModel) -> None:
        """Отрисовывает счёт и оставшиеся жизни."""
        score_surf = self.font_hud.render(f"СЧЁТ: {model.score}", True, self.TEXT_COLOR)
        surface.blit(score_surf, (20, 16))

        # Мини-кораблики в правом верхнем углу как индикатор жизней.
        for i in range(max(0, model.lives)):
            cx = self.width - 28 - i * 26
            cy = 26
            pts = [(cx, cy - 10), (cx - 7, cy + 8), (cx, cy + 4), (cx + 7, cy + 8)]
            pygame.draw.polygon(surface, self.SHIP_COLOR, pts, width=2)

    def _draw_center_overlay(
        self, surface: pygame.Surface, title: str, subtitle: str
    ) -> None:
        """Рисует полупрозрачную плашку с заголовком и подсказкой по центру."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((6, 9, 16, 155))
        surface.blit(overlay, (0, 0))

        title_surf = self.font_title.render(title, True, self.TEXT_COLOR)
        sub_surf = self.font_sub.render(subtitle, True, self.SUBTEXT_COLOR)

        title_rect = title_surf.get_rect(
            center=(self.width // 2, self.height // 2 - 26)
        )
        sub_rect = sub_surf.get_rect(center=(self.width // 2, self.height // 2 + 24))

        surface.blit(title_surf, title_rect)
        surface.blit(sub_surf, sub_rect)
