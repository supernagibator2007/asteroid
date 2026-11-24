"""Точка входа в игру «Астероид»."""

from src.app import AsteroidApp


def main() -> None:
    """Создаёт и запускает приложение Pygame."""
    app = AsteroidApp(width=800, height=600, fps=60)
    app.run()


if __name__ == "__main__":
    main()
