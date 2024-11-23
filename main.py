"""
TODO:
[] Combos

[V] Show HUD
[V] As game advances, accelerate scrolling rate
[V] Control jump height by x axis speed / combo
[V] Always keep player at the middle of the screen
"""
from src.core.environment import Environment
from src.core.game_window import GameWindow

if __name__ == '__main__':
    e = Environment(70, 50, 1000)
    game_window = GameWindow(e)
    game_window.loop()
