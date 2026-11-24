"""Модуль модели состояния и физики игры «Астероид»."""

from enum import Enum
import math
import random

from src.models.entities import Asteroid, Bullet, Ship


class GameState(str, Enum):
    """Возможные состояния игрового процесса."""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameModel:
    """Хранит состояние игры и вычисляет физику, движение и столкновения."""

    SIZE_RADII: dict[int, float] = {
        3: 44.0,
        2: 26.0,
        1: 14.0,
    }
    SIZE_POINTS: dict[int, int] = {
        3: 20,
        2: 50,
        1: 100,
    }

    def __init__(self, width: int, height: int) -> None:
        """Инициализирует модель мира для заданных размеров экрана.

        Args:
            width: Ширина игрового поля.
            height: Высота игрового поля.
        """
        self.width = width
        self.height = height

        self.thrust_accel = 320.0
        self.turn_speed = 3.6
        self.max_ship_speed = 420.0
        self.ship_damping = 0.85
        self.bullet_speed = 560.0
        self.fire_cooldown = 0.22

        self.state = GameState.MENU
        self.score = 0
        self.lives = 3
        self.wave = 1
        self._fire_timer = 0.0

        self.ship = Ship(x=width / 2.0, y=height / 2.0)
        self.asteroids: list[Asteroid] = []
        self.bullets: list[Bullet] = []

        self._spawn_wave(count=4)

    def start_new_game(self) -> None:
        """Сбрасывает прогресс и запускает новую игру."""
        self.score = 0
        self.lives = 3
        self.wave = 1
        self._fire_timer = 0.0
        self.bullets.clear()
        self.asteroids.clear()
        self._reset_ship(invulnerable_time=2.0)
        self._spawn_wave(count=4)
        self.state = GameState.PLAYING

    def toggle_pause(self) -> None:
        """Переключает паузу во время активного раунда."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def _reset_ship(self, invulnerable_time: float = 2.0) -> None:
        """Возвращает корабль в центр экрана с обнулённой скоростью."""
        self.ship = Ship(
            x=self.width / 2.0,
            y=self.height / 2.0,
            invulnerable_timer=invulnerable_time,
        )

    def _spawn_wave(self, count: int) -> None:
        """Создаёт волну крупных астероидов вдали от центра с кораблём."""
        safe_zone_radius = 130.0
        center_x = self.width / 2.0
        center_y = self.height / 2.0

        for _ in range(count):
            while True:
                x = random.uniform(0.0, float(self.width))
                y = random.uniform(0.0, float(self.height))
                # Евклидово расстояние до центра: d = sqrt((x - cx)^2 + (y - cy)^2).
                if math.hypot(x - center_x, y - center_y) >= safe_zone_radius:
                    break

            angle = random.uniform(0.0, 2.0 * math.pi)
            speed = random.uniform(55.0, 130.0)
            self.asteroids.append(
                Asteroid(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    radius=self.SIZE_RADII[3],
                    size_level=3,
                    rotation_speed=random.uniform(-1.6, 1.6),
                )
            )

    def try_fire(self) -> None:
        """Выпускает снаряд из носа корабля, если прошёл кулдаун."""
        if self.state != GameState.PLAYING or self._fire_timer > 0.0:
            return

        nose_x, nose_y = self.ship.nose_position()
        dir_x = math.cos(self.ship.angle_rad)
        dir_y = math.sin(self.ship.angle_rad)

        # Добавляем скорость корабля к скорости снаряда (инерция в космосе).
        bullet = Bullet(
            x=nose_x,
            y=nose_y,
            vx=self.ship.vx + dir_x * self.bullet_speed,
            vy=self.ship.vy + dir_y * self.bullet_speed,
        )
        self.bullets.append(bullet)
        self._fire_timer = self.fire_cooldown

    def step(
        self,
        dt: float,
        turn_left: bool = False,
        turn_right: bool = False,
        thrust: bool = False,
        fire: bool = False,
    ) -> None:
        """Выполняет один шаг симуляции модели."""
        if self.state != GameState.PLAYING:
            # В меню или паузе астероиды могут лениво дрейфовать только в меню.
            if self.state == GameState.MENU:
                for asteroid in self.asteroids:
                    asteroid.update(dt * 0.35, self.width, self.height)
            return

        if self._fire_timer > 0.0:
            self._fire_timer = max(0.0, self._fire_timer - dt)

        turn_dir = (1.0 if turn_right else 0.0) - (1.0 if turn_left else 0.0)
        if turn_dir != 0.0:
            self.ship.rotate(turn_dir * self.turn_speed, dt)

        if thrust:
            self.ship.apply_thrust(self.thrust_accel, dt, self.max_ship_speed)

        if fire:
            self.try_fire()

        self.ship.update(dt, self.ship_damping, self.width, self.height)

        for asteroid in self.asteroids:
            asteroid.update(dt, self.width, self.height)

        self.bullets = [
            b for b in self.bullets if b.update(dt, self.width, self.height)
        ]

        self._handle_collisions()

        if not self.asteroids:
            self.wave += 1
            self._spawn_wave(count=min(10, 3 + self.wave))

    @staticmethod
    def _circles_collide(
        x1: float, y1: float, r1: float, x2: float, y2: float, r2: float
    ) -> bool:
        """Проверяет пересечение двух окружностей по сумме радиусов."""
        # Сравниваем квадраты расстояний, чтобы избежать лишнего извлечения корня.
        dx = x1 - x2
        dy = y1 - y2
        radius_sum = r1 + r2
        return (dx * dx + dy * dy) <= (radius_sum * radius_sum)

    def _split_asteroid(self, asteroid: Asteroid) -> None:
        """Начисляет очки и дробит астероид на два меньших при наличии уровня."""
        self.score += self.SIZE_POINTS.get(asteroid.size_level, 20)
        next_level = asteroid.size_level - 1
        if next_level < 1:
            return

        next_radius = self.SIZE_RADII[next_level]
        for sign in (-1.0, 1.0):
            # Отклоняем вектор скорости под углом +-25..45 градусов при расколе.
            deflection = sign * random.uniform(0.45, 0.8)
            base_angle = math.atan2(asteroid.vy, asteroid.vx) + deflection
            speed = math.hypot(asteroid.vx, asteroid.vy) * random.uniform(1.1, 1.35)
            speed = max(70.0, min(240.0, speed))
            self.asteroids.append(
                Asteroid(
                    x=asteroid.x,
                    y=asteroid.y,
                    vx=math.cos(base_angle) * speed,
                    vy=math.sin(base_angle) * speed,
                    radius=next_radius,
                    size_level=next_level,
                    rotation_speed=random.uniform(-2.2, 2.2),
                )
            )

    def _handle_collisions(self) -> None:
        """Обрабатывает попадания снарядов по астероидам и столкновения с кораблём."""
        surviving_bullets: list[Bullet] = []
        destroyed_asteroid_indices: set[int] = set()

        for bullet in self.bullets:
            hit = False
            for idx, asteroid in enumerate(self.asteroids):
                if idx in destroyed_asteroid_indices:
                    continue
                if self._circles_collide(
                    bullet.x,
                    bullet.y,
                    bullet.radius,
                    asteroid.x,
                    asteroid.y,
                    asteroid.radius,
                ):
                    destroyed_asteroid_indices.add(idx)
                    hit = True
                    break
            if not hit:
                surviving_bullets.append(bullet)

        self.bullets = surviving_bullets

        if destroyed_asteroid_indices:
            new_asteroids: list[Asteroid] = []
            for idx, asteroid in enumerate(self.asteroids):
                if idx in destroyed_asteroid_indices:
                    self._split_asteroid(asteroid)
                else:
                    new_asteroids.append(asteroid)
            self.asteroids = new_asteroids

        if self.ship.invulnerable_timer <= 0.0:
            for asteroid in self.asteroids:
                if self._circles_collide(
                    self.ship.x,
                    self.ship.y,
                    self.ship.radius * 0.85,
                    asteroid.x,
                    asteroid.y,
                    asteroid.radius * 0.9,
                ):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                    else:
                        self._reset_ship(invulnerable_time=2.2)
                    break
