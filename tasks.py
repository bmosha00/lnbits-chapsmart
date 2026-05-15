import asyncio

from loguru import logger


async def wait_for_paid_invoices():
    """Background task placeholder for future status polling."""
    # Future: poll pending cashouts and update their status
    # For now, status is checked on-demand via the /status endpoint
    while True:
        await asyncio.sleep(60)
