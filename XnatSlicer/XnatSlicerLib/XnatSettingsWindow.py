from __main__ import vtk, qt, ctk, slicer


import os
import glob
import sys


from XnatHostEditor import *



comment = """
  XnatSettingsWindow is the window for user-inputted XNAT settings, 
  such as host names and default users.

  TODO:
"""






class XnatSettingsWindow:
    """ Popup window for managing user-inputted XnatSettings, 
        such as host names and default users.
    """


    
    def __init__(self, browser):  
        """ Descriptor
        """      
        self.browser = browser
        self.spacer = qt.QLabel("\n\n\n")




        
    def setupWindow(self):
        """ Creates the window via the qt.
        """ 
        self.windowLayout = qt.QFormLayout()
        self.window = qt.QWidget()
        self.window.setFixedWidth(500)
        self.window.setWindowModality(2)
        self.window.setLayout(self.windowLayout)
        self.window.hide()




        
    def showWindow(self, position = True):
        """ Creates a new window, adjusts aesthetics, then shows.
        """ 

        
        # Create new window
        self.setupWindow()

        
        # Create a host manager (communicates to XnatSettings)
        self.hostEditor = XnatHostEditor(self.browser, parent = self)
        
        
        # Aesthetics
        self.windowLayout.addRow(self.hostEditor.frame)
        self.windowLayout.addRow(self.spacer)
        self.windowLayout.addRow(self.spacer)
        self.windowLayout.addRow(self.spacer)
        self.windowLayout.addRow(self.spacer)


        # Buttons
        self.doneButton = qt.QPushButton("Done")
        self.windowLayout.addRow(self.doneButton)#, 5, 5)
        self.doneButton.connect('clicked()', self.donePressed)


        # qt show
        self.window.show()

        
        # Reposition if argument is true
        if position:
            self.window.show()
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.window.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.window.height/2
            self.window.move(qt.QPoint(x,y))
        
        self.window.raise_()
        




        
    def donePressed(self):
        self.setupWindow()
        self.window.hide()
