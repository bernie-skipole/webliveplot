# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "litestar[mako]",
#     "uvicorn",
#     "minilineplot",
#     "webliveplot"
# ]
# ///

# Note, if you use uv this script can be run with
# uv run example2.py
# and will serve a web page at localhost:8000

"""This example generates two plots, and shows how
   iterating over the page gets a reference to each plot in turn.
   The two plots have different time spans, the first over one hour
   and the second over two hours. The second plot is set with
   different colours just to show how this is done."""


import asyncio, time, random

from webliveplot import Page, Plot


async def measurements(page):
    "Create data for each plot every ten seconds"
    while True:
        for plot in page:
            value = random.uniform(10, 70)  # random values used here
            # set a new description before putpoint, as putpoint generates a new chart
            plot.description = f"Latest value = {value:.1f}"
            plot.putpoint(time.time(), value)
        # and update the web page after changes
        page.update()
        await asyncio.sleep(10) # pause 10 seconds between updates


async def runcharts(page):
    """Create tasks, one runs the web server, at the given host and port
                     one runs 'measurements' gathering data for the plots
    """
    async with asyncio.TaskGroup() as tg:
        tg.create_task( page.serve(host='localhost', port=8000) )
        tg.create_task( measurements(page) )
        print("Now serving at localhost:8000")


if __name__ == "__main__":

    # Create Plot objects
    plot1 =  Plot(hours=1, title="Plot 1")
    plot1.set_y_axis(ymin=0.0, ymax=80.0, yintervals=4, yformat=".1f")

    plot2 =  Plot(hours=2, title="Plot 2")
    plot2.set_y_axis(ymin=0.0, ymax=80.0, yintervals=4, yformat=".1f")
    plot2.set_colors(backcol="white", gridcol="white", axiscol="black", chartbackcol="grey")
    plot2.set_line(color="yellow")

    # insert plots into the page
    page = Page([plot1, plot2])
    page.title = "Page title"

    # Run the loop and serve the web page
    asyncio.run(runcharts(page))

