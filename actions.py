from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine

    def perform(self) -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()

class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> None:
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return #A герою нечего атаковать

        print(f"You kick the {target.name}, much to its annoyance!")


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        ''' В случае MovementAction мы дважды проверяем, что перемещение происходит “в границах” и на “проходимой” плитке, и если любое из них верно, 
        мы возвращаемся, ничего не делая. Если ни один из этих случаев не подтвердится, тогда мы перемещаем сущность, как и раньше. '''

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination is blocked by a tile.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y): #A проверяем не занят ли пункт назначения сущностью
            return

        self.entity.move(self.dx,self.dy)

class BumpAction(ActionWithDirection):                              #A этот класс принимает решение о том какой класс , между MeleeAction и MovementAction возвращать.
    def perform(self) -> None:                                    #A  BumpAction просто определяет, какой из них подходит для вызова,
        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()