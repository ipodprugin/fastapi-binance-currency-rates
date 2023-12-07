import json

from datetime import datetime
from dataclasses import dataclass

from fastapi import (
    APIRouter, 
    Depends, 
    Query,
    status, 
)

from app.api import models
from app.database.session import get_db_session
from app.database.helpers import db_get_pair_rates, db_get_pair_last_rate
from app.redis_client import redis_client

router = APIRouter(prefix="/v1", tags=["v1"])


@dataclass
class GetRatesAgrs:
    pairs: list[str] = Query(...)
    date_from: datetime | None = None
    date_to: datetime | None = None


@router.get("/rate/{pair}", status_code=status.HTTP_200_OK)
async def get_pair_last_rate(pair: str) -> models.CurrencyRatePayload | None:
    """ 
    Возвращает последний курс валютной пары. 

    `:param pair:` Пара валют.
    """
    async with redis_client.client() as conn:
        cached_pair = await conn.get(pair)
        if cached_pair :
            return models.CurrencyRatePayload.model_validate(json.loads(cached_pair))
    async with get_db_session() as session:
        return await db_get_pair_last_rate(session, pair.upper())


@router.get("/rates", status_code=status.HTTP_200_OK)
async def get_pairs_rates(
    args: GetRatesAgrs = Depends(),
) -> dict[str, list[models.CurrencyRatePayload]] | None:
    """ 
    Возвращает курсы валют.

    `:param pairs:` Список пар валют.  
    `:param date_from:` Дата начала периода.  
    `:param date_to:` Дата окончания периода.  

    `:return:` Курсы валют. Если не указаны временные рамки - возвращает курсы за всё время.
    """
    rates_resp = {}
    async with get_db_session() as session:
        for pair in args.pairs:
            rates = await db_get_pair_rates(session, pair.upper(), args.date_from, args.date_to)
            if rates:
                rates_resp[pair] = rates
    return rates_resp
