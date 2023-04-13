from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor, Item
from components.consumable import HealingConsumable
from components.inventory import Inventory


player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=50, defense=2, power=5),
    inventory=Inventory(capacity=26),
)

Troll = Actor(
    char="T",
    color=(75, 0, 130),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
)

BigTroll = Actor(
    char="B",
    color=(0, 0, 139),
    name="BigTroll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=0, power=4),
    inventory=Inventory(capacity=0),
)

Flask = Item(
    char="0",
    color=(119, 221, 119),
    name="Flask",
    consumable=HealingConsumable(amount=4),
)
