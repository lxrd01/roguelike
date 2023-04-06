from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(
    char = "@",
    color = (255, 255, 255),
    name = "Player",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp=30, defense=2, power=5),
)

Troll = Actor(
    char = "T",
    color = (75, 0, 130),
    name = "Troll",
    ai_cls = HostileEnemy,
    fighter = Fighter(hp=10, defense=0, power=3),
)

BigTroll = Actor(
    char="B",
    color=(0, 0, 139),
    name="BigTroll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)