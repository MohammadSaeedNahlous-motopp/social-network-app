from math import ceil
from typing import Generic, TypeVar
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Query


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_query(cls, query: Query, page: int, page_size: int):
        page = page if page > 0 else 1
        page_size = page_size if page_size > 0 else 0
        total = query.count()

        if page_size > 0:
            total_pages = calculate_total_pages(total=total, page_size=page_size)
            items = paginate(query=query, page=page, page_size=page_size).all()
        else:
            total_pages = 1 if total > 0 else 0
            items = query.all()

        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )



def paginate(
    query: Query,
    page: int,
    page_size: int,
) -> Query:
    offset = (page - 1) * page_size

    return query.offset(offset).limit(page_size)


def calculate_total_pages(
    total: int,
    page_size: int,
) -> int:
    results = ceil(total / page_size) if total > 0 else 0
    return results
