from game_map import GameMap
import tile_types

import random
from typing import Iterator, Tuple

import tcod


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):  # __init__ Функция принимает координаты x и y верхнего левого угла и вычисляет нижний правый угол                                                                   
        self.x1 = x                                               #  на основе параметров w и h (ширина и высота).
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:           #  center это “свойство”, которое по сути действует как переменная, доступная только для чтения для                                                    
        center_x = int((self.x1+self.x2) / 2)      #  нашего RectangularRoom класса. В нем описываются координаты “x“ и ”y" центра комнаты.
        center_y = int((self.y1+self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:                                #  inner Свойство возвращает два “среза”, которые представляют внутреннюю часть нашей комнаты.
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)    #  Это часть, которую мы будем “выкапывать” для нашей комнаты в нашем генераторе подземелий.


def tunnel_between(                               # Функция принимает два аргумента, оба кортежа, состоящие из двух целых чисел.
    start: Tuple[int, int], end: Tuple[int, int]  # Он должен возвращать итератор кортежа из двух целых чисел. Все кортежи будут иметь координаты “x“ и ”y" на карте.  
) -> Iterator[Tuple[int, int]]:
    x1, y1 = start # берем координаты из кортежей.
    x2, y2 = end
    '''Мы случайным образом выбираем между двумя вариантами: перемещение по горизонтали, затем по вертикали или наоборот. 
    Основываясь на том, что выбрано, мы установим значения corner_x и corner_y в разные точки. '''
    if random.random() < 0.5: # шанс 50%.
        # Двигаемся горизонтально, затем вертикально.
        corner_x, corner_y = x2, y1
    else:
        # Двигаемся вертикально, затем горизонтально.
        corner_x, corner_y = x1, y2

    ''' tcod включает в свой модуль прямой видимости функцию для рисования линий Брезенхема. 
        Хотя в данном случае мы не работаем с прямой видимостью, функция все еще оказывается полезной для получения линии из одной точки в другую. 
        В этом случае мы получаем одну линию, затем другую, чтобы создать туннель в форме буквы “L”.
        .tolist() преобразует точки в линии в список.
        Выражения Yield - интересная часть Python, которая позволяет возвращать “генератор”. 
        По сути, вместо того, чтобы возвращать значения и вообще выходить из функции, мы возвращаем значения, но сохраняем локальное состояние. 
        Это позволяет функции продолжить с того места, на котором она остановилась, при повторном вызове, вместо того, чтобы начинать с начала, 
        как это делает большинство функций. '''

    # Сгенерируем координаты для туннеля. 
    for x, y in tcod.los.bresenham((x1,y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x,corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(MAP_WIDTH, MAP_HEIGHT) -> GameMap:
    dungeon = GameMap(MAP_WIDTH, MAP_HEIGHT)

    room_1 = RectangularRoom(x = 20, y = 15, width = 10, height = 15)
    room_2 = RectangularRoom(x = 35, y = 15, width = 10, height = 15)

    dungeon.tiles[room_1.inner] = tile_types.floor
    dungeon.tiles[room_2.inner] = tile_types.floor

    for x, y in tunnel_between(room_2.center, room_1.center):
        dungeon.tiles[x, y] = tile_types.floor

    return dungeon