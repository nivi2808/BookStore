from enum import Enum


class CategoryEnum(str, Enum):
    LITERATURE = "LITERATURE"
    NONFICTION = "NONFICTION"
    ACTION = "ACTION"
    THRILLER = "THRILLER"
    TECHNOLOGY= "TECHNOLOGY"
    DRAMA = "DRAMA"
    POETRY = "POETRY"
    MEDIA = "MEDIA"
    OTHERS = "OTHERS"
