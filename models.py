from typing import Optional
from pydantic import BaseModel


class CreateCashout(BaseModel):
    wallet: str
    phone_number: str
    recipient_name: str
    amount_tzs: int


class Cashout(BaseModel):
    id: str
    wallet: str
    phone_number: str
    recipient_name: str
    amount_tzs: int
    amount_sats: int = 0
    fee_sats: int = 0
    fee_percent: float = 0.0
    quote_id: Optional[str] = None
    invoice_id: Optional[str] = None
    bolt11: Optional[str] = None
    payment_hash: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
