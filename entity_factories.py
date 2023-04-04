from entity import Entity

player = Entity(char="@", color=(255, 255, 255), name="Player", blocks_movement=True)

orc = Entity(char="o", color=(75, 0, 130), name="Orc", blocks_movement=True)
boss = Entity(char="T", color=(0, 0, 139), name="Boss", blocks_movement=True)