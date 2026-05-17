from typing import Optional
from .models import Cashout, CreateCashout
from . import db
import uuid
import time


async def create_cashout(data: CreateCashout) -> Cashout:
    cashout_id = uuid.uuid4().hex[:12]
    now = int(time.time())
    await db.execute(
        """
        INSERT INTO chapsmart.cashouts
        (id, wallet, phone_number, recipient_name, amount_tzs, status, created_at, updated_at)
        VALUES (:id, :wallet, :phone_number, :recipient_name, :amount_tzs, :status, :created_at, :updated_at)
        """,
        {
            "id": cashout_id,
            "wallet": data.wallet,
            "phone_number": data.phone_number,
            "recipient_name": data.recipient_name,
            "amount_tzs": data.amount_tzs,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        },
    )
    return await get_cashout(cashout_id)


async def get_cashout(cashout_id: str) -> Optional[Cashout]:
    row = await db.fetchone(
        "SELECT * FROM chapsmart.cashouts WHERE id = :id",
        {"id": cashout_id},
    )
    if not row:
        return None
    return Cashout(**row)


async def get_cashouts(wallet_id: str) -> list[Cashout]:
    rows = await db.fetchall(
        "SELECT * FROM chapsmart.cashouts WHERE wallet = :wallet ORDER BY created_at DESC LIMIT 50",
        {"wallet": wallet_id},
    )
    return [Cashout(**row) for row in rows]


async def update_cashout(cashout_id: str, **kwargs) -> Optional[Cashout]:
    set_clause = ", ".join([f"{k} = :{k}" for k in kwargs.keys()])
    values = dict(kwargs)
    values["updated_at"] = int(time.time())
    values["cashout_id"] = cashout_id
    await db.execute(
        f"UPDATE chapsmart.cashouts SET {set_clause}, updated_at = :updated_at WHERE id = :cashout_id",
        values,
    )
    return await get_cashout(cashout_id)
