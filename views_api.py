from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, Query
from loguru import logger
from lnbits.core.crud import get_wallet
from lnbits.core.services import pay_invoice
from lnbits.decorators import require_admin_key, require_invoice_key
from lnbits.settings import settings

from . import chapsmart_ext as chapsmart_api_router
from .crud import create_cashout, get_cashout, get_cashouts, update_cashout
from .models import CreateCashout


def _get_settings():
    """Get ChapSmart settings from LNbits admin config."""
    return {
        "api_key": getattr(settings, "chapsmart_api_key", ""),
        "api_secret": getattr(settings, "chapsmart_api_secret", ""),
        "account_number": getattr(settings, "chapsmart_account_number", ""),
        "api_url": getattr(settings, "chapsmart_api_url", "https://backend.chapsmart.com"),
    }


def _get_headers(s: dict) -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": s["api_key"],
        "X-API-Secret": s["api_secret"],
    }


# ──────────────────────────────────────────────
# GET /api/v1/quote — get a fresh quote
# ──────────────────────────────────────────────
@chapsmart_api_router.post("/api/v1/quote")
async def api_quote(
    phone_number: str = Query(...),
    recipient_name: str = Query(...),
    amount_tzs: int = Query(...),
    wallet=Depends(require_invoice_key),
):
    s = _get_settings()
    if not s["api_key"] or not s["api_secret"]:
        return {"error": "ChapSmart is not configured. Ask the admin to set API credentials."}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{s['api_url']}/api/v1/invoices/quote",
            headers=_get_headers(s),
            json={
                "metadata": {
                    "amountTZS": amount_tzs,
                    "phoneNumber": phone_number,
                    "recipientName": recipient_name,
                    "accountNumber": s["account_number"],
                }
            },
        )

    if resp.status_code != 200:
        logger.warning(f"[ChapSmart] Quote error: {resp.status_code} - {resp.text}")
        return {"error": resp.json().get("error", "Quote failed")}

    data = resp.json()
    if not data.get("success"):
        return {"error": data.get("error", "Quote failed")}

    return {
        "quote_id": data["quoteId"],
        "amount_tzs": amount_tzs,
        "amount_sats": data["youPay"]["sats"],
        "fee_sats": data["youPay"]["feeSats"],
        "fee_percent": data["youPay"]["feePercent"],
        "phone_number": phone_number,
        "recipient_name": recipient_name,
    }


# ──────────────────────────────────────────────
# POST /api/v1/poll — refresh quote price
# ──────────────────────────────────────────────
@chapsmart_api_router.get("/api/v1/poll/{quote_id}")
async def api_poll_quote(quote_id: str, wallet=Depends(require_invoice_key)):
    s = _get_settings()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{s['api_url']}/api/v1/invoices/quote/{quote_id}",
            headers=_get_headers(s),
        )

    if resp.status_code != 200:
        return {"error": "Failed to poll quote"}

    data = resp.json()
    return {
        "quote_id": quote_id,
        "amount_sats": data.get("youPay", {}).get("sats", 0),
        "fee_sats": data.get("youPay", {}).get("feeSats", 0),
        "fee_percent": data.get("youPay", {}).get("feePercent", 0),
    }


# ──────────────────────────────────────────────
# POST /api/v1/send — generate invoice, pay it, track status
# ──────────────────────────────────────────────
@chapsmart_api_router.post("/api/v1/send")
async def api_send(data: CreateCashout, wallet=Depends(require_admin_key)):
    s = _get_settings()
    if not s["api_key"] or not s["api_secret"]:
        return {"error": "ChapSmart is not configured. Ask the admin to set API credentials."}

    # Step 1: Create quote
    logger.info(f"[ChapSmart] Creating quote: {data.amount_tzs} TZS to {data.phone_number}")

    async with httpx.AsyncClient(timeout=30) as client:
        quote_resp = await client.post(
            f"{s['api_url']}/api/v1/invoices/quote",
            headers=_get_headers(s),
            json={
                "metadata": {
                    "amountTZS": data.amount_tzs,
                    "phoneNumber": data.phone_number,
                    "recipientName": data.recipient_name,
                    "accountNumber": s["account_number"],
                }
            },
        )

    if quote_resp.status_code != 200:
        logger.warning(f"[ChapSmart] Quote error: {quote_resp.text}")
        return {"error": quote_resp.json().get("error", "Quote failed")}

    quote_data = quote_resp.json()
    if not quote_data.get("success"):
        return {"error": quote_data.get("error", "Quote failed")}

    quote_id = quote_data["quoteId"]
    amount_sats = quote_data["youPay"]["sats"]
    fee_sats = quote_data["youPay"]["feeSats"]
    fee_percent = quote_data["youPay"]["feePercent"]

    # Step 2: Generate invoice
    logger.info(f"[ChapSmart] Generating invoice for quote {quote_id}")

    async with httpx.AsyncClient(timeout=30) as client:
        gen_resp = await client.post(
            f"{s['api_url']}/api/v1/invoices/generate",
            headers=_get_headers(s),
            json={"quoteId": quote_id},
        )

    if gen_resp.status_code != 200:
        logger.warning(f"[ChapSmart] Generate error: {gen_resp.text}")
        return {"error": gen_resp.json().get("error", "Invoice generation failed")}

    gen_data = gen_resp.json()
    if not gen_data.get("success"):
        return {"error": gen_data.get("error", "Invoice generation failed")}

    bolt11 = gen_data["bolt11"]
    invoice_id = gen_data["invoiceId"]

    # Step 3: Save cashout record
    cashout = await create_cashout(data)
    await update_cashout(
        cashout.id,
        quote_id=quote_id,
        invoice_id=invoice_id,
        bolt11=bolt11,
        amount_sats=amount_sats,
        fee_sats=fee_sats,
        fee_percent=fee_percent,
        status="paying",
    )

    # Step 4: Pay the bolt11 from user's wallet
    logger.info(f"[ChapSmart] Paying bolt11: {amount_sats} sats for cashout {cashout.id}")

    try:
        payment_hash = await pay_invoice(
            wallet_id=data.wallet,
            payment_request=bolt11,
            extra={"tag": "chapsmart", "cashout_id": cashout.id},
        )
        await update_cashout(
            cashout.id,
            payment_hash=payment_hash,
            status="paid",
        )
        logger.info(f"[ChapSmart] ✅ Lightning paid: {amount_sats} sats. Invoice: {invoice_id}")
    except Exception as e:
        logger.warning(f"[ChapSmart] ❌ Lightning payment failed: {e}")
        await update_cashout(cashout.id, status="failed", error=str(e))
        return {"error": f"Lightning payment failed: {e}"}

    return {
        "cashout_id": cashout.id,
        "invoice_id": invoice_id,
        "amount_tzs": data.amount_tzs,
        "amount_sats": amount_sats,
        "fee_sats": fee_sats,
        "status": "paid",
        "message": "Payment sent! M-Pesa is being processed.",
    }


# ──────────────────────────────────────────────
# GET /api/v1/status/{cashout_id} — check M-Pesa status
# ──────────────────────────────────────────────
@chapsmart_api_router.get("/api/v1/status/{cashout_id}")
async def api_status(cashout_id: str, wallet=Depends(require_invoice_key)):
    cashout = await get_cashout(cashout_id)
    if not cashout:
        return {"error": "Cashout not found"}

    # If already completed or failed, return cached status
    if cashout.status in ("completed", "failed"):
        return {
            "cashout_id": cashout.id,
            "status": cashout.status,
            "amount_tzs": cashout.amount_tzs,
            "amount_sats": cashout.amount_sats,
            "error": cashout.error,
        }

    # Poll ChapSmart backend for live status
    if cashout.invoice_id:
        s = _get_settings()
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{s['api_url']}/api/v1/invoices/status/{cashout.invoice_id}",
                    headers=_get_headers(s),
                )
            if resp.status_code == 200:
                status_data = resp.json()
                backend_status = status_data.get("status", "")

                if backend_status == "completed":
                    await update_cashout(cashout.id, status="completed")
                elif backend_status == "failed":
                    payout_error = status_data.get("payout", {}).get("payoutError", "Unknown error")
                    await update_cashout(cashout.id, status="failed", error=payout_error)
                elif backend_status == "settled":
                    await update_cashout(cashout.id, status="settled")

                return {
                    "cashout_id": cashout.id,
                    "status": backend_status,
                    "amount_tzs": cashout.amount_tzs,
                    "amount_sats": cashout.amount_sats,
                    "backend_message": status_data.get("message", ""),
                }
        except Exception as e:
            logger.warning(f"[ChapSmart] Status poll error: {e}")

    return {
        "cashout_id": cashout.id,
        "status": cashout.status,
        "amount_tzs": cashout.amount_tzs,
        "amount_sats": cashout.amount_sats,
    }


# ──────────────────────────────────────────────
# GET /api/v1/cashouts — list user's cashout history
# ──────────────────────────────────────────────
@chapsmart_api_router.get("/api/v1/cashouts")
async def api_cashouts(wallet=Depends(require_invoice_key)):
    cashouts = await get_cashouts(wallet.wallet.id)
    return [c.dict() for c in cashouts]
