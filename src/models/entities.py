"""Модуль сущностей модели игры «Астероид»."""

from dataclasses import dataclass, field
import math
import random


@dataclass
class Ship:
    """Представляет корабль игрока в двумерном пространстве."""

    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    angle_rad: float = -math.pi / 2  # 0 — вправо, -pi/2 — вверх по экрану.
    radius: float = 16.0
    invulnerable_timer: float = 0.0

    def apply_thrust(self, thrust_accel: float, dt: float, max_speed: float) -> None:
        """Ускоряет корабль вдоль текущего направления носа.

        Args:
            thrust_accel: Ускорение тяги в пикселях за секунду в квадрате.
            dt: Шаг времени в секундах.
            max_speed: Максимально допустимая скорость корабля.
        """
        # Единичный вектор направления: (cos(theta), sin(theta)).
        dir_x = math.cos(self.angle_rad)
        dir_y = math.sin(self.angle_rad)

        self.vx += dir_x * thrust_accel * dt
        self.vy += dir_y * thrust_accel * dt

        # Ограничиваем модуль вектора скорости: |v| = sqrt(vx^2 + vy^2).
        speed = math.hypot(self.vx, self.vy)
        if speed > max_speed:
            scale = max_speed / speed
            self.vx *= scale
            self.vy *= scale

    def rotate(self, angular_speed: float, dt: float) -> None:
        """Поворачивает корабль на угол angular_speed * dt радиан."""
        self.angle_rad += angular_speed * dt

    def update(self, dt: float, damping: float, width: int, height: int) -> None:
        """Обновляет позицию корабля, инерцию и обёртку за края экрана."""
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Экспоненциальное затухание скорости для плавного скольжения в космосе.
        damping_factor = max(0.0, 1.0 - damping * dt)
        self.vx *= damping_factor
        self.vy *= damping_factor

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        self.x %= width
        self.y %= height

    def nose_position(self) -> tuple[float, float]:
        """Возвращает координаты носовой части корабля."""
        return (
            self.x + math.cos(self.angle_rad) * self.radius,
            self.y + math.sin(self.angle_rad) * self.radius,
        )


@dataclass
class Asteroid:
    """Представляет астероид единого размера с неровным многоугольным контуром."""

    x: float
    y: float
    vx: float
    vy: float
    radius: float = 30.0
    rotation_angle: float = 0.0
    rotation_speed: float = 0.0
    vertices: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Генерирует локальные вершины многоугольника вокруг центра."""
        if not self.vertices:
            num_vertices = random.randint(8, 12)
            self.vertices = []
            for i in range(num_vertices):
                # Равномерно распределяем углы по окружности [0, 2*pi).
                base_angle = (2.0 * math.pi * i) / num_vertices
                jitter = random.uniform(0.75, 1.22)
                r = self.radius * jitter
                self.vertices.append(
                    (math.cos(base_angle) * r, math.sin(base_angle) * r)
                )

    def update(self, dt: float, width: int, height: int) -> None:
        """Перемещает астероид, вращает контур и заворачивает за границы."""
        self.x = (self.x + self.vx * dt) % width
        self.y = (self.y + self.vy * dt) % height
        self.rotation_angle += self.rotation_speed * dt


@dataclass
class Bullet:
    """Представляет снаряд, выпущенный кораблём."""

    x: float
    y: float
    vx: float
    vy: float
    ttl: float = 1.1  # Время жизни в секундах.
    radius: float = 3.0

    def update(self, dt: float, width: int, height: int) -> bool:
        """Обновляет положение снаряда. Возвращает False, если снаряд исчез."""
        self.ttl -= dt
        if self.ttl <= 0.0:
            return False

        self.x = (self.x + self.vx * dt) % width
        self.y = (self.y + self.vy * dt) % height
        return True
