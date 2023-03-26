from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        ''' В случае MovementAction мы дважды проверяем, что перемещение происходит “в границах” и на “проходимой” плитке, и если любое из них верно, 
        мы возвращаемся, ничего не делая. Если ни один из этих случаев не подтвердится, тогда мы перемещаем сущность, как и раньше. '''

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination is blocked by a tile.

        entity.move(self.dx, self.dy)
