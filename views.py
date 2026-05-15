from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists

from . import chapsmart_ext, chapsmart_renderer


@chapsmart_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return chapsmart_renderer().TemplateResponse(
        "chapsmart/index.html",
        {"request": request, "user": user.json()},
    )
