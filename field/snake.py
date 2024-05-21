from pydantic import BaseModel

from field.cells import Head, Body


class Snake(BaseModel):
    head: Head
    body: Body
