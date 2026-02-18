from src.schemas import PaginationParams
from fastapi import Query
from datetime import datetime, timezone


def get_pagination(
        page: int = Query(1, ge=1, description="Page number (starting from 1)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)")
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)

def calculate_total_price(start_time: datetime, end_time: datetime, price_per_hour: float) -> float:
    duration = end_time - start_time
    hours = duration.total_seconds() / 3600
    return round(hours * price_per_hour, 2)
