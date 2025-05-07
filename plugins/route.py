from aiohttp import web
from info import *
import pytz

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("kya dekh raha hai tu 🤔😁🤔😁🤔😁🤔\n😁🤔🤔🤔😁😁😁😁😁😁😁🤔😁🤔😁🤔🤔😁🤔😁😙😘🤣😚😅😙😅😚😅😚😅😙😅😚😂😚😂😙😋😬😍😌🤩😌😘")

