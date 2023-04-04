from typing import Iterable, Any
from tcod.context import Context
from tcod.console import Console

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler
from tcod.map import compute_fov

class Engine:
    def __init__(self, event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f'The {entity.name} wonders when it will get to take a real turn.')


    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)
            self.handle_enemy_turns()
            self.update_fov() #A обновляет фов перед сл действием игрока

    def update_fov(self) -> None:   #A область видимости
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        #A если плитка исследована то тогда она не будет в ШРАУДЕ
        self.game_map.explored |= self.game_map.visible



    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        context.present(console)
        console.clear()


'''Мы импортировали GameMap класс и теперь передаем его экземпляр в Engine инициализаторе класса. 
    После этого мы используем его двумя способами:
    В handle_events мы используем его, чтобы проверить, является ли плитка “проходимой”, и только после этого перемещаем проигрыватель.
    В render мы вызываем метод GameMap’s render, чтобы отобразить его на экране. '''