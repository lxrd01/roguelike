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

class ActionWithDirection(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
        if not target:
            return #A герою нечего атаковать

        print(f"You kick the {target.name}")


class MovementAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        ''' В случае MovementAction мы дважды проверяем, что перемещение происходит “в границах” и на “проходимой” плитке, и если любое из них верно, 
        мы возвращаемся, ничего не делая. Если ни один из этих случаев не подтвердится, тогда мы перемещаем сущность, как и раньше. '''

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination is blocked by a tile.
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y): #A проверяем не занят ли пункт назначения сущностью
            return
        entity.move(self.dx, self.dy)

class BumpAction(ActionWithDirection):                              #A этот класс принимает решение о том какой класс , между MeleeAction и MovementAction возвращать.
    def perform(self, engine: Engine, entity: Entity) -> None:      #A  BumpAction просто определяет, какой из них подходит для вызова,
        dest_x = entity.x + self.dx                                 #A в зависимости от того, есть ли блокирующая сущность в данном пункте назначения или нет
        dest_y = entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)

        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)