from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
    def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.entities:
            console.print(entity.x, entity.y, entity.char, fg =  entity.color)

        context.present(console)

        console.clear()


'''Мы импортировали GameMap класс и теперь передаем его экземпляр в Engine инициализаторе класса. 
    После этого мы используем его двумя способами:
    В handle_events мы используем его, чтобы проверить, является ли плитка “проходимой”, и только после этого перемещаем проигрыватель.
    В render мы вызываем метод GameMap’s render, чтобы отобразить его на экране. '''