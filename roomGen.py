from __future__ import annotations


from game_map import GameMap
import tile_types


import random
from typing import Iterator, Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity

import tcod
import entity_factories

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):  # __init__ Функция принимает координаты x и y верхнего левого угла и вычисляет нижний правый угол                                                                   
        self.x1 = x                                               #  на основе параметров width и height (ширина и высота).
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

    def intersects(self, other: RectangularRoom) -> bool:
        """intersects проверяет, пересекаются ли комната и другая комната (other в аргументах) или нет. 
        Он возвращает True если они пересекаются или False если они этого не делают. Мы будем использовать это, чтобы определить, перекрываются ли две комнаты или нет."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def place_entities(
        room: RectangularRoom, dungeon: GameMap, maximmum_monsters: int,
) -> None:
    number_of_monsters = random.randint(0, maximmum_monsters)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):  #A мы проверяем рандомные координаты чтоб не стакнулись враги
            if random.random() < 0.7: #А с вероятностью 70% будет босс
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.boss.spawn(dungeon, x, y)




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


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    MAP_WIDTH: int,
    MAP_HEIGHT: int,
    max_monsters_per_room: int,
    player: Entity,
) -> GameMap:
    #  Создаём новое подземелье
    dungeon = GameMap(MAP_WIDTH, MAP_HEIGHT, entities=[player]) #A entities=[player] добавили чтоб сам игрок был виден в фове

    rooms: List[RectangularRoom] = [] # Мы создаём и ведём текущий список всех комнат.
    ''' Наш алгоритм может размещать или не размещать комнату в зависимости от того, пересекается ли она с другой, поэтому мы не будем знать, 
    сколько комнат у нас в итоге получится. Но, по крайней мере, мы будем знать, что это число не может превышать определенную сумму. '''
    for r in range(max_rooms):
        '''Здесь мы используем заданные минимальные и максимальные размеры комнаты, чтобы задать ширину и высоту комнаты. 
        Затем мы получаем случайную пару x и y координат, чтобы попытаться разместить комнату внизу. Координаты должны быть между 0 и шириной и высотой карты.
        Мы используем эти переменные, чтобы затем создать экземпляр нашего RectangularRoom.'''
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms): # Если наша комната пересекается с другой комнатой, то мы используем continue,
            continue                                                     # чтобы пропустить остальную часть цикла.

        dungeon.tiles[new_room.inner] = tile_types.floor # Здесь мы “выкапываем” комнату. То есть, присваиваем нашей комнате параметры floor

        if len(rooms) == 0:
            # Первая комната, где стартует игрок
            player.x, player.y = new_room.center
            '''Мы помещаем нашего игрока в центр первой созданной нами комнаты. Если эта комната не первая, мы переходим к else: '''
        else:
            # Копаем туннель между предыдущей и нынешней комнатой
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room)
        # Добавляем комнату в список.
        rooms.append(new_room)

    return dungeon