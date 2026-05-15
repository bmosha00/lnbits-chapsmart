from fastapi import APIRouter
from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_chapsmart")

chapsmart_static_files = [
    {
        "path": "/chapsmart/static",
        "name": "chapsmart_static",
    }
]

chapsmart_ext: APIRouter = APIRouter(prefix="/chapsmart", tags=["ChapSmart"])
chapsmart_api_router: APIRouter = APIRouter(
    prefix="/chapsmart/api/v1", tags=["ChapSmart API"]
)


def chapsmart_renderer():
    return template_renderer(["chapsmart/templates"])
