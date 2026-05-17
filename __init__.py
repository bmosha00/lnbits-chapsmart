from fastapi import APIRouter
from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_chapsmart")

chapsmart_static_files = []

chapsmart_ext: APIRouter = APIRouter(prefix="/chapsmart", tags=["ChapSmart"])


def chapsmart_renderer():
    return template_renderer(["chapsmart/templates"])


from .views import *  # noqa: F401,F403,E402
from .views_api import *  # noqa: F401,F403,E402
