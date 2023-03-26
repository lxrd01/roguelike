﻿from typing import Tuple

import numpy

#  dtype создает тип данных, который может использовать Numpy, который ведет себя аналогично struct на таком языке, как C. Наш тип данных состоит из трех частей
graphic_dt = numpy.dtype(
    [
        ("ch", numpy.int32), #  ch: Символ, представленный в целочисленном формате. Мы переведем ее из целого числа в Юникод.
        ("fg", "3B"), #  fg: Цвет переднего плана. “3B” означает 3 байта без знака, которые могут использоваться для цветовых кодов RGB.
        ("bg", "3B"), #  bg: Цвет фона. Похоже на fg
    ]
)


#  Это еще одно dtype, которое мы будем использовать в самой фактической плитке. Он также состоит из трех частей:
tile_dt = numpy.dtype(
    [
        ("walkable", bool), #  walkable: Логическое значение, описывающее, может ли игрок пройти по этой плитке.
        ("transparent", bool), #  transparent: Логическое значение, описывающее, блокирует ли эта плитка поле зрения или нет.
        ("dark", graphic_dt), #  dark: Здесь используется наш ранее определенный dtype, который содержит символ для печати, цвет переднего плана и цвет фона.
                               #    Назвали dark, т.к позже мы захотим различать плитки, которые находятся в поле зрения, и которых нет.
                                #    dark будут представлять фрагменты, которых нет в текущем поле зрения.  '''
    ]
)

'''  Это вспомогательная функция, которую мы будем использовать для определения типа наших плиток.
Она принимает параметры walkable, transparent и dark, которые должны выглядеть знакомо, поскольку это те же типы данных, которые мы использовали выше в tile_dt.
Она создает массив Numpy, содержащий только один элемент tile_dt и возвращает его.  '''

def new_tile(*, walkable: int, transparent: int, dark: Tuple[int, Tuple[int,int,int], Tuple[int,int,int]]) -> numpy.ndarray:
    return numpy.array((walkable, transparent, dark), dtype = tile_dt)


floor = new_tile(
    walkable=True, transparent=True, dark=(ord(" "), (255, 255, 255), (97, 101, 0)),
                                     #  dark атрибут состоит из символа пробела и определяет цвет переднего плана как белый 
                                     #  (не имеет значения, поскольку это пустое пространство) и цвет фона.
)
wall = new_tile(
    walkable=False, transparent=False, dark=(ord(" "), (255, 255, 255), (0, 0, 0)),
)