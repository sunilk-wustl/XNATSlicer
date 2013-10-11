from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import shutil
import csv
import urllib2

from XnatUtils import *



comment = """
XnatAddProjEditor is used for creating new projects/folders within a given
Xnat host.  It manages talking to a given XnatCommunicator and its associated
string inputs. 

TODO : 
"""



class XnatAddProjEditor(object):
    """ Described above.
    """
    
    def __init__(self, browser = None):
        """ Init function.
        """
        
        #--------------------
        # Public vars.
        #--------------------        
        self.browser = browser

        

        #--------------------
        # Make 'project' dropdown
        #--------------------        
        self.projLabel = qt.QLabel("Project")
        self.projDD = qt.QComboBox()
        self.projDD.addItems(self.browser.XnatCommunicator.getFolderContents('/projects'))       
        self.projDD.connect("currentIndexChanged(const QString&)", self.populateSubjectDD)


        
        #--------------------
        # Make project lineEdit for foldername entry
        #-------------------- 
        self.projLE = qt.QLineEdit()
        self.projLE.connect("textEdited(const QString&)", self.projLineEdited)
        self.projError = qt.QLabel()
        self.projError.setTextFormat(1)


        
        #--------------------
        # Make subject dropdown
        #--------------------         
        self.subjLabel = qt.QLabel("Subject")
        self.subjDD = qt.QComboBox()


        
        #--------------------
        # Make subject lineEdit for foldername entry
        #--------------------  
        self.subjLE = qt.QLineEdit()
        self.subjLE.connect("textEdited(const QString&)", self.subjLineEdited)


        
        #--------------------
        # Make subject errorLabel
        #--------------------          
        self.subjError = qt.QLabel()
        self.subjError.setTextFormat(1)



        #--------------------
        # Make experiment label, lineEdit and Error
        #--------------------   
        self.exptLabel = qt.QLabel("Experiment")
        self.exptLE = qt.QLineEdit()
        self.exptError = qt.QLabel()
        self.exptError.setTextFormat(1)



        #--------------------
        # Use the currently selected View item to 
        # derive the project dropdowns.
        #--------------------           
        p = None
        s = None
        proj = ""
        if (self.browser.XnatView.viewWidget.currentItem() != None):
            p = self.browser.XnatView.getParentItemByCategory(self.browser.XnatView.viewWidget.currentItem(), "projects")
            s = self.browser.XnatView.getParentItemByCategory(self.browser.XnatView.viewWidget.currentItem(), "subjects")
            proj = p.text(self.browser.XnatView.column_name)
            self.projDD.setCurrentIndex(self.projDD.findText(proj))
        else:
            proj = self.projDD.currentText 
           

        
        #--------------------
        # Populate the subject dropdown and set 
        # the index on the subject dropdown accordingly.
        #--------------------
        self.populateSubjectDD(proj) 
        if s:
            self.subjDD.setCurrentIndex(self.subjDD.findText(s.text(self.browser.XnatView.column_name)))



            
    def populateSubjectDD(self, proj):
        """ Utilizes 'XnatCommunicator' to query for the subjects within a given
            project, provided by the argument.
        """

        #--------------------
        # Get the raw subjects
        #--------------------
        subjs_raw = self.browser.XnatCommunicator.getFolderContents('/projects/' + proj + '/subjects')
        subjs_name = []



        #--------------------
        # Add subjects to dropdown
        #--------------------
        for r in subjs_raw:
            subjs_name.append(self.browser.XnatCommunicator.getItemValue('/projects/' + proj + '/subjects/' + str(urllib2.quote(r)), 'label'))
        self.subjDD.clear()
        self.subjDD.addItems(subjs_name)


        
    def show(self):
        """ Shows the modal that allows the user
            to add folders to a given XNAT host.
        """

        #--------------------
        # Construct the layout for the modal
        #--------------------
        l = qt.QGridLayout()
        self.addProjWindow = qt.QWidget()
        self.addProjWindow.setFixedWidth(700)
        mainWindow = slicer.util.mainWindow()



        #--------------------
        # Position modal to center.
        #--------------------
        screenMainPos = mainWindow.pos
        x = screenMainPos.x() + mainWindow.width/2 - self.addProjWindow.width/2
        y = screenMainPos.y() + mainWindow.height/2 - self.addProjWindow.height/2
        existingCol = qt.QLabel("Existing")
        newCol = qt.QLabel("New")



        #--------------------
        # Add all of the widgets.
        #--------------------
        l.addWidget(existingCol, 0, 1)
        l.addWidget(newCol, 0, 2)
        l.addWidget(self.projLabel, 1, 0)
        l.addWidget(self.projDD, 1, 1)
        l.addWidget(self.projLE, 1, 2)
        l.addWidget(self.projError, 2, 2)
        l.addWidget(self.subjLabel, 3, 0)
        l.addWidget(self.subjDD, 3, 1)
        l.addWidget(self.subjLE, 3, 2)
        l.addWidget(self.subjError, 4, 2)
        l.addWidget(self.exptLabel, 5, 0)
        l.addWidget(self.exptLE, 5, 2)
        l.addWidget(self.exptError, 6, 2)



        
        #--------------------
        # Create the necessary buttons.
        #--------------------
        createButton = qt.QPushButton()
        createButton.setText("Create")
        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(createButton, 0)
        buttonRow.addButton(cancelButton, 2)
        buttonRow.connect('clicked(QAbstractButton*)', self.onCreateButtonClicked)
        l.addWidget(buttonRow, 7, 2)
        self.addProjWindow.setLayout(l)
        self.addProjWindow.move(qt.QPoint(x,y))
        self.addProjWindow.setWindowTitle("Add Folder to Xnat")
        self.addProjWindow.show()




    def onCreateButtonClicked(self,button):
        """ Callback if the create button is clicked. Communicates with
            XNAT to create a folder. Details below.  
        """
        
        #--------------------
        # If OK is clicked....
        #--------------------
        if 'create' in button.text.lower():

            #--------------------
            # Clear errors
            #--------------------
            self.exptError.setText("")
            self.subjError.setText("")
            self.projError.setText("")

            

            #--------------------
            # Construct URI based on XNAT rules.
            #--------------------
            xnatUri = "/projects/"
            if len(self.projLE.text)>0:
                xnatUri += self.projLE.text
                if len(self.subjLE.text)>0:
                    xnatUri += "/subjects/" + self.subjLE.text
                    if len(self.exptLE.text)>0:
                        xnatUri += "/experiments/" + self.exptLE.text
            else:
                xnatUri += self.projDD.currentText
                if len(self.subjLE.text)>0:
                    xnatUri += "/subjects/" + self.subjLE.text
                    if len(self.exptLE.text)>0:
                        xnatUri += "/experiments/" + self.exptLE.text
                else:
                    xnatUri += "/subjects/" + self.subjDD.currentText
                    if len(self.exptLE.text)>0:
                        xnatUri += "/experiments/" + self.exptLE.text


                        
            #--------------------
            # If the the folder already exists, kick back
            # the relevant error based on whether it was a project
            # subject or experiment...
            #--------------------
            if (self.browser.XnatCommunicator.fileExists(xnatUri)):
                print ("%s %s ALREADY EXISTS!"%(self.browser.utils.lf(), xnatUri))
                projStr = xnatUri.split("/subjects")[0]
                subjStr = None
                exptStr = None
                if "/subjects" in xnatUri:
                    subjStr = xnatUri.split("/experiments")[0]
                if "/experiments" in xnatUri:
                    exptStr =  xnatUri
                if (exptStr and self.browser.XnatCommunicator.fileExists(exptStr)):
                    self.exptError.setText("<font color=\"red\">*Experiment already exists.</font>")
                elif (subjStr and self.browser.XnatCommunicator.fileExists(subjStr)):
                    self.subjError.setText("<font color=\"red\">*Subject already exists.</font>")
                elif (projStr and self.browser.XnatCommunicator.fileExists(projStr)):
                    self.projError.setText("<font color=\"red\">*Project already exists.</font>")



            #--------------------
            # Otherwise make the folder and close the modal.
            #--------------------
            else:
                self.browser.XnatCommunicator.makeDir(xnatUri)
                slicer.app.processEvents()
                self.browser.XnatView.selectItem_byPath(xnatUri)
                print ("%s creating %s "%(self.browser.utils.lf(), xnatUri))
                self.addProjWindow.close()


                
        elif 'cancel' in button.text.lower():
            self.addProjWindow.close()



            
    def projLineEdited(self, str):
        """ Removes whitespaces from project line and
            enables/disables accordingly.
        """
        if (len(str.strip(" ")) > 0):
            self.projDD.setEnabled(False)
            self.subjDD.setEnabled(False)
        else:
            self.projDD.setEnabled(True)



            
    def subjLineEdited(self, str):
        """ Removes whitepsaces from experiment line
            and enables/disables accordingly.
        """
        if (len(str.strip(" ")) > 0):
            self.subjDD.setEnabled(False)
        else:
            self.subjDD.setEnabled(True)