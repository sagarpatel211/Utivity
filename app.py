# Authors: Saurin Patel, Sagar Patel
# Program Name: Utivity Productivity app
# Program Description: The file to run the app, where other files connect to in order to function
# Last Revision Date: 2021 - 1 - 30
# ICS 4U1
# Mr. Moore 

from pyfladesk import init_gui #imports module from pyfladesk.py for desktop app support
from routes import app #import databases, routes, and functions from routes.py
from config import *

if __name__ == '__main__':
     #if app.py is run (main file of program), then display a desktop app with these specifications
    init_gui(app, width=1200, height=675, window_title="Utivity", icon="static/img/appicon.png")
