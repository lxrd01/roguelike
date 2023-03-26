import numpy
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = numpy.full((width, height), fill_value = tile_types.wall, order = "F") #  По сути, мы создаем 2D-массив, заполненный теми же значениями, 
                                                                                        #  которые в данном случае являются tile_types.wall, 
                                                                                        #  которые мы создали ранее. Это будет заполнено self.tiles плитками стен

    def in_bounds(self, x: int, y: int) -> bool:            #  Как указано в строке, этот метод возвращает True, 
        return 0 <= x < self.width and 0 <= y < self.height #  если заданные значения x и y находятся в пределах границ карты. 
                                                            #  Мы можем использовать это, чтобы гарантировать, что игрок не выйдет за пределы карты, в пустоту.

    def render(self, console: Console) -> None:                             #  Используя метод Console класса tiles_rgb, мы можем быстро отобразить всю карту.
        console.tiles_rgb[0:self.width, 0:self.height] = self.tiles["dark"] #  Этот метод оказывается намного быстрее, чем использование console.print метода,
                                                                            #  который мы используем для отдельных объектов.