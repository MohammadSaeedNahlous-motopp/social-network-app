from math import ceil
from typing import Generic, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Query


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def paginate(
    query: Query,
    page: int,
    page_size: int,
) -> Query:
    offset = (page - 1) * page_size

    return query.offset(offset).limit(page_size)


def paginate_list(
    query: list,
    page: int,
    page_size: int,
) -> list:
    start = (page - 1) * page_size
    end = start + page_size

    return query[start:end]


def calculate_total_pages(
    total: int,
    page_size: int,
) -> int:
    results = ceil(total / page_size) if total > 0 else 0
    return results
