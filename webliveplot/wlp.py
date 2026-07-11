
import asyncio, collections, copy

import uvicorn

import minilineplot

from .web.app import make_app


class Page(collections.UserList):

    """This object is a list of Plot objects plus extra methods:
       serve - a co-routine method to serve the web site
       update - called to request connected browsers to update
       the plots.
       and attribute:
       title - which is used as the web page title
    """

    def __init__(self, initlist=None):
        super().__init__()
        if initlist is not None:
            if isinstance(initlist, Plot):
                super().append(initlist)
            else:
                try:
                    iter(initlist)
                except TypeError:
                    raise TypeError("Only a Plot object, or a list of Plot objects is allowed")
                for item in initlist:
                    self._validate(item)
                    super().append(item)

        # this event is triggered when update is called
        self.chart_event = asyncio.Event()

        # This attribute sets the web page title
        self.title = "WebLivePlot"


    def _validate(self, item):
        "Ensure items are all Plot objects"
        if not isinstance(item, Plot):
            raise TypeError(f"Only Plot objects allowed, got {type(item).__name__}")

    def append(self, item):
        "Override append to enforce type check"
        self._validate(item)
        super().append(item)

    def __setitem__(self, index, item):
        "Override __setitem__ to enforce type check"
        self._validate(item)
        super().__setitem__(index, item)

    def insert(self, index, item):
        "Override insert to enforce type check"
        self._validate(item)
        super().insert(index, item)

    async def serve(self, basepath=None, host='localhost', port=8000):
        "Await this to serve the page at /basepath/, if basepath is None, serve at /"
        if basepath:
            basepath = basepath.strip("/. ")
        if basepath:
            basepath = f"/{basepath}/"
        else:
            basepath = None
        app = make_app(basepath, self)
        config = uvicorn.Config(app=app, host=host, port=port, log_level="error")
        await uvicorn.Server(config).serve()

    def update(self):
        "Update the page by flagging an async event"
        self.chart_event.set()
        self.chart_event.clear()



class Plot:

    def __init__(self, hours=4, height=600, width=800, title="", description=""):
        "Create the Plot"
        self.hours = hours
        self.height = height
        self.width = width
        self.title = title
        self.description=description
        self.backcol = "white"
        self.gridcol = "grey"
        self.axiscol = "black"
        self.chartbackcol = "white"
        self.linelist = [minilineplot.Line(values=[], color = "blue")]
        self.plotstring = ""

        self.ymin = None
        self.ymax = None
        self.yintervals = None
        self.yformat = None

        self.localtime = True


    def putpoint(self, t, v, lineindex=0):
        "Generates the chart when a new point added"
        # points of the chart are held in the 'values' attribute of Line object self.linelist[0]
        points = self.linelist[lineindex].values
        points.append((t,v))
        if len(points)<2:
            return
        first_t = points[0][0]
        plotted_span = self.hours * 3600
        while first_t < t - plotted_span:
            points.pop(0)
            if len(points)<2:
                return
            first_t = points[0][0]
        if len(points)<2:
            return
        self.make_chart()


    def make_chart(self):
        "Called by putpoint to generate a minilineplot chart"
        chart = minilineplot.Axis( lines=self.linelist,
                                   imagewidth=self.width,
                                   imageheight=self.height,
                                   title = self.title,
                                   description = self.description,
                                   gridcol = self.gridcol,
                                   axiscol = self.axiscol,
                                   chartbackcol = self.chartbackcol,
                                   backcol = self.backcol)

        # get list of all y values
        ally = []
        for line in self.linelist:
            # line.values is a list of tuples
            for valtuple in line.values:
                ally.append(valtuple[1])
        if not ally:
            return
        ymax = max(ally)
        ymin = min(ally)

        if self.ymin is None or self.ymax is None or self.yformat is None or self.yintervals is None :
            chart.auto_y()
        elif ymin<self.ymin or ymax>self.ymax:
            chart.auto_y()
        else:
            chart.ymax = self.ymax
            chart.ymin = self.ymin
            chart.yintervals = self.yintervals
            chart.yformat = self.yformat
        chart.auto_time_x(hourspan = self.hours, localtime = self.localtime)
        try:
            # create an svg string of the chart
            self.plotstring = chart.to_string()
        except:
            self.plotstring = ""


    def set_colors(self,
                   backcol = "white",      # The background colour of the whole image
                   gridcol = "grey",       # Color of the chart grid
                   axiscol = "black",      # Color of axis, title and description
                   chartbackcol = "white"  # Background colour of the chart
                   ):
        "Sets the chart colours"
        self.backcol = backcol
        self.gridcol = gridcol
        self.axiscol = axiscol
        self.chartbackcol = chartbackcol


    def set_line(self, color="blue", label="", lineindex=0):
        "Sets a color and optional label for the line"
        self.linelist[lineindex].color = color
        self.linelist[lineindex].label = label


    def add_line(self, color="blue", label=""):
        "Sets a color and optional label for the new line"
        newline = minilineplot.Line(values=[], color = color, label=label)
        self.linelist.append(newline)


    def set_y_axis(self, ymin, ymax, yintervals, yformat):
        """If this is not called, an automatic y scaling will be used.
           If it is called, then these values will be set, however if any y point
           exceeds the values, then the chart will revert to auto-scaling.
           If you wish to revert to autoscaling, call this with None values."""
        self.ymin = ymin
        self.ymax = ymax
        self.yintervals = yintervals
        self.yformat = yformat


    def set_localtime(self, tflag=True):
        """If tflag is True,the time values on the x axis will show local time (local time of the server).
           If tflag is False, the time values will be UTC."""
        if tflag:
            self.localtime = True
        else:
            self.localtime = False







 


