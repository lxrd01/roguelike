import tcod

from engine import Engine
from input_handlers import EventHandler
from entity import Entity
from roomGen import generate_dungeon


def main() -> None:
    SCREEN_WIDTH = 150
    SCREEN_HEIGHT = 80

    MAP_WIDTH = 150
    MAP_HEIGHT = 80

    tileset = tcod.tileset.load_tilesheet("arial12x12.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    event_handler = EventHandler()
    
    player = Entity(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2), "@", (1,121,254))
    npc = Entity(int(SCREEN_WIDTH / 2 - 5), int(SCREEN_HEIGHT / 2), "T", (254,75,0))
    entities = {npc, player}

    game_map = generate_dungeon(MAP_WIDTH, MAP_HEIGHT)

    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

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


