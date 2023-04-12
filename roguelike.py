import copy
import tcod
from engine import Engine
import entity_factories
from roomGen import generate_dungeon
import color


def main() -> None:
    SCREEN_WIDTH = 150
    SCREEN_HEIGHT = 80

    MAP_WIDTH = 150
    MAP_HEIGHT = 80

    room_max_size = 25
    room_min_size = 12
    max_rooms = 18
    max_monsters_per_room = 2
    max_items_per_room = 2

    tileset = tcod.tileset.load_tilesheet("arial12x12.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms = max_rooms,
        room_min_size = room_min_size,
        room_max_size = room_max_size,
        MAP_WIDTH = MAP_WIDTH,
        MAP_HEIGHT = MAP_HEIGHT,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine
    )

    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventure, to yet another dungeon!", color.welcome_text
    )

    with tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset = tileset,
        title = "Test game",
        vsync = True,
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order = "F")
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            engine.event_handler.handle_events(context)


if __name__ == "__main__":
    main()
