from typing import Tuple, List

from pydantic import BaseModel

from cells.cell import Cell
from constants.colors import Color


class BodyCell(Cell):
    color: Tuple[int, int, int] = Color.GREEN.value


class Head(BodyCell):
    pass


class Body(BaseModel):
    cells: List[BodyCell]
