import pygame


class AsteroidApp:
    """Управляет окном Pygame, событиями и главным игровым циклом."""

    def __init__(self, width: int = 800, height: int = 600, fps: int = 60) -> None:
        """Инициализирует Pygame, окно, часы и шрифт.

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

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24, bold=True)

    def run(self) -> None:
        """Запускает главный цикл обработки событий, обновления и отрисовки."""
        self.is_running = True

        while self.is_running:
            # Переводим миллисекунды в секунды для независимой от FPS физики.
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
        """Обрабатывает системные и пользовательские события Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def update(self, dt: float) -> None:
        """Обновляет состояние игры за прошедший интервал времени.

        Args:
            dt: Прошедшее время с предыдущего кадра в секундах.
        """
        # Игровая логика появится в следующем коммите.
        _ = dt

    def render(self) -> None:
        """Отрисовывает текущий кадр на экране."""
        self.screen.fill((11, 15, 25))

        text_surface = self.font.render(
            "АСТЕРОИД", True, (226, 232, 240)
        )
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)
