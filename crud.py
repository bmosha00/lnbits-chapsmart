from typing import Optional
from lnbits.db import Database
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cashout_id,
            data.wallet,
            data.phone_number,
            data.recipient_name,
            data.amount_tzs,
            "pending",
            now,
            now,
        ),
    )
    return await get_cashout(cashout_id)


async def get_cashout(cashout_id: str) -> Optional[Cashout]:
    row = await db.fetchone(
        "SELECT * FROM chapsmart.cashouts WHERE id = ?", (cashout_id,)
    )
    if not row:
        return None
    return Cashout(**row)


async def get_cashouts(wallet_id: str) -> list[Cashout]:
    rows = await db.fetchall(
        "SELECT * FROM chapsmart.cashouts WHERE wallet = ? ORDER BY created_at DESC LIMIT 50",
        (wallet_id,),
    )
    return [Cashout(**row) for row in rows]


async def update_cashout(cashout_id: str, **kwargs) -> Optional[Cashout]:
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(int(time.time()))
    values.append(cashout_id)
    await db.execute(
        f"UPDATE chapsmart.cashouts SET {set_clause}, updated_at = ? WHERE id = ?",
        tuple(values),
    )
    return await get_cashout(cashout_id)
