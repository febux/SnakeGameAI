from typing import List
import numpy as np

from pydantic import BaseModel

from field.cells import Food
from field.snake import Snake


class Field(BaseModel):
    snake: Snake
    food: List[Food]
    field_width: int
    field_height: int
    block_size: int

    def get_matrix(self):
        field_array = np.zeros((self.field_height, self.field_width), dtype=int)

        field_array[self.snake.head.loc_x // self.block_size, self.snake.head.loc_y // self.block_size] = 1
        for cell in self.snake.body.cells:
            field_array[cell.loc_x // self.block_size, cell.loc_y // self.block_size] = 1
        for food in self.food:
            field_array[food.loc_x // self.block_size, food.loc_y // self.block_size] = 2
        return field_array
