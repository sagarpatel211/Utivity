# Authors: Saurin Patel, Sagar Patel
# Program Name: Utivity Productivity app
# Program Description: File dedicated to
# Last Revision Date: 2021 - 1 - 30
# ICS 4U1
# Mr. Moore

#imports system, socket, and PyQt5 to initialize a desktop window
import sys
import socket
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

# function to set up the ports, thread for the application, and the application itself
class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()  #instance of the application
        self.application = application  #instance of the application
        self.port = port #instance of the port

    # Dunder method to wait for the application thread to load
    def __del__(self):
        self.wait()

    # Method to run the application with threadded as true and the selected port
    def run(self):
        self.application.run(port=self.port, threaded=True) #Sets up application with correct port and thread

class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__() # Dunder method to inherit webpage
        self.root_url = root_url

    # Home function toe create the root url
    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url: 
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)

# Main function where all the specifications for the desktop app with be put into
def init_gui(application, port=0, width=800, height=600,
             window_title="PyFladesk", icon="appicon.png", argv=None):
    if argv is None: # If there are no argument values
        argv = sys.argv # Use the system default for creating the app structure

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close() 

    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = QtWidgets.QMainWindow() # Sets up the main window for our app and gets the widgets below ready
    window.setFixedSize (width, height) # Selects the width hand height for app
    window.setWindowTitle(window_title) # Selects the title for our app
    window.setWindowIcon(QtGui.QIcon(icon)) # Select the topbar icon for the app

    # WebView Level
    webView = QtWebEngineWidgets.QWebEngineView(window)
    window.setCentralWidget(webView)

    # WebPage Level
    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webView.setPage(page)
    window.show()
    return qtapp.exec_()
