﻿from __future__ import annotations

import exceptions
from typing import TYPE_CHECKING
from tcod.console import Console
from message_log import MessageLog
from input_handlers import MainGameEventHandler
from render_function import render_bar
from tcod.map import compute_fov

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler

class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Игнорировать исключения невозможных действий от ИИ

    def update_fov(self) -> None:  # A область видимости
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=20,
        )
        # A если плитка исследована то тогда она не будет в ШРАУДЕ
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=26, y=45, width=50, height=30)

        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=15,
        )

        # render_names_at_mouse_location(console=console, x=21, y=44, engine=self)


'''Мы импортировали GameMap класс и теперь передаем его экземпляр в Engine инициализаторе класса. 
    После этого мы используем его двумя способами:
    В handle_events мы используем его, чтобы проверить, является ли плитка “проходимой”, и только после этого перемещаем проигрыватель.
    В render мы вызываем метод GameMap’s render, чтобы отобразить его на экране. '''