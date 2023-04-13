from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import tcod.event

import actions

from actions import (
    Action,
    BumpAction,
    PickupAction,
    WaitAction
)
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
    # Управление с помощью стрелок на клавиатуре
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1)
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> bool:
        """Обработка действий, возвращаемых методами событий.

         Возвращает True, если действие продвинет ход.
         """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True



    # def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
    #     if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
    #         self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    """Обрабатывает пользовательский ввод для действий, требующих специального ввода."""

    def handle_action(self, action: Optional[Action]) -> bool:
        """Возврат к основному обработчику событий после выполнения действительного действия."""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """По умолчанию любая клавиша выходит из этого обработчика ввода."""
        if event.sym in {  # Игнорировать клавиши-модификаторы.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """По умолчанию любой щелчок мыши приводит к выходу из этого обработчика ввода."""
        return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        """Вызывается, когда пользователь пытается выйти или отменить действие.
        По умолчанию это возвращается к основному обработчику событий.
         """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler):
    """Этот обработчик позволяет пользователю выбрать элемент.

     Что происходит затем, зависит от подкласса.
     """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Будет перемещаться в другую позицию в зависимости от того, где находится игрок, поэтому игрок всегда может видеть, где
         они есть.
         """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Вызывается, когда пользователь выбирает допустимый элемент."""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Обрабатывать с помощью предмета инвентаря."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Вернуть действие для выбранного элемента."""
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """Обработка сброса предмета инвентаря."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Бросить этот предмет."""
        return actions.DropItem(self.engine.player, item)


class MainGameEventHandler(EventHandler):

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.K_e:
            action = PickupAction(player)

        elif key == tcod.event.K_i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_q:
            self.engine.event_handler = InventoryDropHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super(). __init__(engine)
        self.log_length = len(engine.message_log.message)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        log_console = tcod.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "|Message history|", alignment=tcod.CENTER
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)
