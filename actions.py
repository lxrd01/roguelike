﻿from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

import entity

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor,Item

import color
from inventory import inv,pos_inv


class Action:
    def __init__(self, entity: Actor) -> None:
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


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class Take(ActionWithDirection):
    def take(self, item):
        if isinstance(item, Item):
            if pos_inv != 6:
                inv[pos_inv] = item.char
                pos_inv += 1
                item.char = "u"



class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return #A герою нечего атаковать

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        ''' В случае MovementAction мы дважды проверяем, что перемещение происходит “в границах” и на “проходимой” плитке, и если любое из них верно, 
             мы возвращаемся, ничего не делая. Если ни один из этих случаев не подтвердится, тогда мы перемещаем сущность, как и раньше. '''

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return

        self.entity.move(self.dx, self.dy)  #A проверяем не занят ли пункт назначения сущностью


class BumpAction(ActionWithDirection):                              #A этот класс принимает решение о том какой класс , между MeleeAction и MovementAction возвращать.
    def perform(self) -> None:      #A  BumpAction просто определяет, какой из них подходит для вызова,
        if self.target_actor:
            if isinstance(self.target_actor,entity.Actor):
                return MeleeAction(self.entity, self.dx, self.dy).perform()
            if isinstance(self.target_actor,entity.Item):
                return Take(self.entity).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
