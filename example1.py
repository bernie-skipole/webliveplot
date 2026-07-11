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
# uv run example1.py
# and will serve a web page at localhost:8000

"""This example generates and serves a plot over a one hour
   period. The y values are just randomly generated numbers.
   As the values are generated every ten seconds, any connected
   browser will see the plot updated. This should occur seamlessly
   without full page refreshes.
"""


import asyncio, time, random

from webliveplot import Page, Plot

async def measurements(page):
    """Create data and plot it using plot.putpoint(),
       update the web page using page.update()"""
    # In this case there is only one plot to update
    plot = page[0]

    while True:
        value = random.uniform(30, 70)   # random values used here
        # set a new description before putpoint, as putpoint generates a new plot
        plot.description = f"Latest value = {value:.1f}"
        plot.putpoint(time.time(), value)
        # update the web page
        page.update()
        await asyncio.sleep(10) # pause 10 seconds between readings


async def runcharts(page):
    "Create two tasks, one runs the web server, one runs 'measurements' gathering data for the plot"
    async with asyncio.TaskGroup() as tg:
        tg.create_task( page.serve(host='localhost', port=8000) )
        tg.create_task( measurements(page) )
        print("Now serving at localhost:8000")


if __name__ == "__main__":

    # Create Plot object
    plot =  Plot(hours=1, title="Chart title")
    plot.set_y_axis(ymin=0.0, ymax=80.0, yintervals=4, yformat=".1f")

    # insert it into a web page    
    page = Page(plot)
    page.title = "Page title"
    # page acts as a list of plots, multiple plots can be inserted
    # with append or using Page([plot1, plot2,..]). A Page object has list
    # indexing with methods append, insert and can be iterated over.
    # It has further methods 'serve' to serve the web page, 'update' to
    # request connected browsers to update the page, and attribute 'title'
    # to set the page title. 

    # Run the loop and serve the web page
    asyncio.run(runcharts(page))

