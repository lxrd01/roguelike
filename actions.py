from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item

import color
import exceptions


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine

    def perform(self) -> None:
        raise NotImplementedError()

class PickupAction(Action):
    """Возьмите предмет и добавьте его в инвентарь, если для него есть место."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Вернуть актера в этот пункт назначения действий."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Вызвать способность предметов, это действие будет предоставлено для предоставления контекста."""
        self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)

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


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.") #A герою нечего атаковать

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
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)  #A проверяем не занят ли пункт назначения сущностью


class BumpAction(ActionWithDirection):                              #A этот класс принимает решение о том какой класс , между MeleeAction и MovementAction возвращать.
    def perform(self) -> None:      #A  BumpAction просто определяет, какой из них подходит для вызова,
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
