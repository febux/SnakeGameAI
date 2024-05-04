from typing import Tuple

from cells.cell import Cell
from constants.colors import Color


class Food(Cell):
    color: Tuple[int, int, int] = Color.BLUE.value
