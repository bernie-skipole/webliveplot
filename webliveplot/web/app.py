

import asyncio

from os import listdir, remove
from os.path import isfile, join

from pathlib import Path

from collections.abc import AsyncGenerator

from asyncio.exceptions import TimeoutError

from litestar import Litestar, get, post, Request
from litestar.plugins.htmx import HTMXPlugin, HTMXTemplate, ClientRedirect, ClientRefresh
from litestar.contrib.mako import MakoTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.response import Template, Redirect, File
from litestar.static_files import create_static_files_router

from litestar.connection import ASGIConnection
from litestar.exceptions import NotFoundException

from litestar.response import ServerSentEvent, ServerSentEventMessage


# location of static files, for CSS and javascript
STATICFILES = Path(__file__).parent.resolve() / "static"

# location of template files
TEMPLATEFILES = Path(__file__).parent.resolve() / "templates"


# Dictionary of Global variables
PARAMETERS = {}


class CheckChange:
    """Iterate whenever a page update is requested."""

    def __aiter__(self):
        return self

    async def __anext__(self):
        """Whenever there is an update requested, return a ServerSentEventMessage
           or send one every thirty seconds regardless"""
        global PARAMETERS
        page = PARAMETERS.get('page')
        while True:
            if page:
                try:
                    await asyncio.wait_for(page.chart_event.wait(), timeout=30.0)
                except TimeoutError:
                    pass
            else:
                await asyncio.sleep(30)
            # a chart_event has occurred
            return ServerSentEventMessage(event="update")


# SSE Handler
@get(path="/check", sync_to_thread=False)
def check() -> ServerSentEvent:
    return ServerSentEvent(CheckChange())


def gotonotfound_error_handler(request: Request, exc: Exception) -> ClientRedirect|Redirect:
    """If a NotFoundException is raised, this handles it, and redirects
       the caller to the not found page"""
    global PARAMETERS
    basepath = PARAMETERS.get("basepath")
    if basepath:
        redirectpath = basepath + "notfound"
    else:
        redirectpath = "/notfound"
    if request.htmx:
        return ClientRedirect(redirectpath)
    return Redirect(redirectpath)


@get("/notfound")
async def notfound(request: Request) -> Template:
    "This is the not found page of your site"
    return Template("notfound.html")


@get("/")
async def publicroot(request: Request) -> ClientRedirect|Redirect:
    "This is the public root folder of your site"
    global PARAMETERS
    basepath = PARAMETERS.get("basepath")
    if basepath:
        redirectpath = basepath + "chartpage.html"
    else:
        redirectpath = "/chartpage.html"
    if request.htmx:
        return ClientRedirect(redirectpath)
    return Redirect(redirectpath)


@get("/chartpage.html" )
async def chartpage(request: Request) -> Template:
    "This is the chart page of your site"
    global PARAMETERS
    page = PARAMETERS.get('page')
    if page is None:
        return Template("chartpage.html", context={"plotlist":[], "pagetitle":"Not Ready"})
    elif not page:
        return Template("chartpage.html", context={"plotlist":[], "pagetitle":page.title})
    plotlist = []
    for plot in page:
        if not plot.plotstring:
            continue
        else:
            plotlist.append(plot.plotstring)
    return Template("chartpage.html", context={"plotlist":plotlist, "pagetitle":page.title})


@get("/getchart" )
async def getchart(request: Request) -> Template:
    "This is just the list of charts, updating the page"
    global PARAMETERS
    page = PARAMETERS.get('page')
    if not page:
        return HTMXTemplate(template_name = "charts.html", context={"plotlist":[]})
    plotlist = []
    for plot in page:
        if not plot.plotstring:
            continue
        else:
            plotlist.append(plot.plotstring)
    return HTMXTemplate(template_name = "charts.html", context={"plotlist":plotlist})



def make_app(basepath, page):
    # Initialize the Litestar app with a Mako template engine and register the routes
    global PARAMETERS, STATICFILES, TEMPLATEFILES
    PARAMETERS['basepath'] = basepath
    PARAMETERS['page'] = page
     
    app = Litestar( path = basepath,
        route_handlers=[publicroot,
                        notfound,
                        chartpage,
                        check,
                        getchart,
                        create_static_files_router(path="/static", directories=[STATICFILES]),
                       ],
        exception_handlers={ NotFoundException: gotonotfound_error_handler},
        plugins=[HTMXPlugin()],
        template_config=TemplateConfig(directory=TEMPLATEFILES,
                                       engine=MakoTemplateEngine
                                      ),
        openapi_config=None
        )
    return app
