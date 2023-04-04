import copy
import tcod
from engine import Engine
import entity_factories
from input_handlers import EventHandler
from roomGen import generate_dungeon


def main() -> None:
    SCREEN_WIDTH = 150
    SCREEN_HEIGHT = 80

    MAP_WIDTH = 150
    MAP_HEIGHT = 80

    room_max_size = 15
    room_min_size = 10
    max_rooms = 42
    max_monsters_per_room = 1

    tileset = tcod.tileset.load_tilesheet("arial12x12.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    event_handler = EventHandler()
    
    player = copy.deepcopy(entity_factories.player)

    game_map = generate_dungeon(
        max_rooms = max_rooms,
        room_min_size = room_min_size,
        room_max_size = room_max_size,
        MAP_WIDTH = MAP_WIDTH,
        MAP_HEIGHT = MAP_HEIGHT,
        max_monsters_per_room=max_monsters_per_room,
        player = player
    )

    engine = Engine(event_handler=event_handler, game_map=game_map, player=player)

    with tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset = tileset,
        title = "Test game",
        vsync = True,
    ) as context:
        root_console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order = "F")
        while True:
            engine.render(console = root_console, context = context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__ == "__main__":
    main()


