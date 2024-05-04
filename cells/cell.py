from typing import Tuple

from pydantic import BaseModel

from constants.colors import Color


class Cell(BaseModel):
    loc_x: int
    loc_y: int
    color: Tuple[int, int, int] = Color.WHITE.value
