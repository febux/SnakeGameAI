from typing import List

from pydantic import BaseModel

from field.cells import Food
from field.snake import Snake


class Field(BaseModel):
    snakes: List[Snake]
    food: List[Food]

    def get_matrix(self):
        return
