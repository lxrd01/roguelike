from __future__ import annotations
import copy
from typing import Optional, Type, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    gamemap: GameMap


    def __init__(
            self,
            gamemap: Optional[GameMap] = None,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            blocks_movement: bool = False,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement  #A Blocks_movement описывает, можно ли переместить эту Сущность или нет.
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        #A заспавнить копию экземпляра на этом же месте
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"):
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)


    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        fighter: Fighter
    ):
        super().__init__(
            x = x,
            y = y,
            char = char,
            color = color,
            name = name,
            blocks_movement = True,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)

    '''Первое, что делает наш Actor класс в своей __init__() функции, это вызывает свой суперкласс __init__(), который в данном случае является Entity классом.
     Мы проходим blocks_movement как True каждый раз, потому что мы можем предположить, что все “действующие лица” будут блокировать движение. 
     Помимо вызова Entity.__init__(), мы также устанавливаем два компонента для Actor класса: ai и fighter. 
     Идея в том, что каждому действующему лицу для функционирования понадобятся две вещи: способность передвигаться и принимать решения, а также способность принимать
     (и получать) урон.'''