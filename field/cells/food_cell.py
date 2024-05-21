from typing import Tuple

from field.cells.cell import Cell
from constants.colors import Color


class Food(Cell):
    color: Tuple[int, int, int] = Color.BLUE.value
