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
# uv run example3.py
# and will serve a web page at localhost:8000

"""This example generates two plots, with the second
   plot containing two lines of measurements.
   The y axis limits are not set on the second plot, to
   illustrate the automatic axis scaling"""


import asyncio, time, random

from webliveplot import Page, Plot

async def plot1measurements(page):
    """Create data for plot1 every ten seconds.
       This first plot can be obtained as page[0]"""
    plot1 = page[0]
    while True:
        t = time.time()
        value = random.uniform(10, 70)
        plot1.description = f"Latest value = {value:.1f}"
        plot1.putpoint(t, value)
        await asyncio.sleep(10) # pause 10 seconds between updates


async def plot2measurements(page):
    """Create data for the two lines of plot2 every five seconds,
       and update the page"""
    plot2 = page[1]
    while True:
        t = time.time()
        value1 = random.uniform(40, 70)
        value2 = random.uniform(5, 30)
        if value1 >= 60:
            # Flag an alarm when line1 value is greater than 60
            # by setting the line and the grid red
            plot2.set_line(color="red", label="line1", lineindex=0)
            plot2.gridcol="red"
        else:
            plot2.set_line(color="green", label="line1", lineindex=0)
            plot2.gridcol="white"
        plot2.description = f"values are {value1:.1f} and {value2:.1f}"
        plot2.putpoint(t, value1, lineindex=0)
        plot2.putpoint(t, value2, lineindex=1)
        # and update the web page after changes
        page.update()
        await asyncio.sleep(5) # pause 5 seconds between updates


async def runcharts(page):
    """Create tasks, one runs the web server, at the given host and port
                     one runs 'plot1measurements' gathering data for plot1
                     one runs 'plot2measurements' gathering data for plot2
    """
    async with asyncio.TaskGroup() as tg:
        tg.create_task( page.serve(host='localhost', port=8000) )
        tg.create_task( plot1measurements(page) )
        tg.create_task( plot2measurements(page) )
        print("Now serving at localhost:8000")


if __name__ == "__main__":

    # Create Plot objects
    plot1 =  Plot(hours=2, title="Plot 1")
    # y axis limits set to cover measurement values
    plot1.set_y_axis(ymin=0.0, ymax=80.0, yintervals=4, yformat=".1f")

    plot2 = Plot(hours=1, title="Plot 2")
    # For this example y axis limits of plot2 are not set, so is on auto
    plot2.set_colors(backcol="yellow", gridcol="white", axiscol="black", chartbackcol="grey")
    # Add a second line to plot2
    plot2.add_line(color="blue", label="line2")

    # insert the two plots into the page
    page = Page([plot1, plot2])
    page.title = "Page title"

    # Run the loop and serve the web page
    asyncio.run(runcharts(page))

