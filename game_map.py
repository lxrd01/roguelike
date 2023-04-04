from __future__ import annotations
import numpy
import numpy as np
from tcod.console import Console

from typing import Iterable, Optional, TYPE_CHECKING
import tile_types

if TYPE_CHECKING:
    from entity import Entity


class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = numpy.full((width, height), fill_value = tile_types.wall, order = "F") #  По сути, мы создаем 2D-массив, заполненный теми же значениями, 
                                                                                        #  которые в данном случае являются tile_types.wall, 
                                                                                        #  которые мы создали ранее. Это будет заполнено self.tiles плитками стен
        self.visible = np.full((width,height), fill_value=False, order="F") #A плитки которые игрок может увидеть
        self.explored = np.full((width,height), fill_value=False, order="F") #A плитки которые игрок видел раньше

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]: #A функция выполняет итерацию по всем существам
        for entity in self.entities:                                                                #A если обнаружено что оба занимают заданные координаты
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:      #А то она возвращает этот объект
                return entity
        return None


    def in_bounds(self, x: int, y: int) -> bool:            #  Как указано в строке, этот метод возвращает True, 
        return 0 <= x < self.width and 0 <= y < self.height #  если заданные значения x и y находятся в пределах границ карты. 
                                                            #  Мы можем использовать это, чтобы гарантировать, что игрок не выйдет за пределы карты, в пустоту.

    def render(self, console: Console) -> None:                             #  Используя метод Console класса tiles_rgb, мы можем быстро отобразить всю карту.
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(         #  Этот метод оказывается намного быстрее, чем использование console.print метода,
            condlist=[self.visible, self.explored],                          #  который мы используем для отдельных объектов.
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD               #A np.select позволяет нам условно рисовать нужные плитки на основе того, что указано в condlist.
        )
        for entity in self.entities: #A принтуем только те объекты которые в фове
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
