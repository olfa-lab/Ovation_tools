'''
Created on Dec 9, 2014

@author: Admir Resulaj
'''

import argparse
import sys
import getpass
import re
from threading import Thread
from dateutil import parser as time_parser
from datetime import datetime
from os import path, walk, listdir

# GUI modules
from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QApplication, \
                        QLineEdit, QLabel, QSizePolicy, QFrame
from PyQt4.QtCore import SIGNAL, SLOT, QRegExp
from PyQt4.QtCore import Qt

# import the new_data_context function to use for establishing a
# connection with the Ovation server
from ovation.connection import new_data_context
from ovation.web import WebApiException

# class OvationMeasurementInsert(object, Thread):
#     """ Process for inserting a measurement into an Ovation database """
#     
#     def run(self):
#         pass

def check_ovation_credetials(username, password):
    """ Check if we can connect to the Ovation service via given credentials."""
    
    # Make connection to Ovation database with the given credentials
    try:
        connection = new_data_context(str(username), str(password))
    except WebApiException, e:
        raise ValueError(e)

    # Return the connection if successful and authenticated. Else return None
    return connection if connection.isAuthenticated() else None
    

class GetOvationCredentials(QDialog):
    """ Get credentials dialog for an Ovation connection."""
    
    def __validate(self):
        """ Validate user name and password. """
        
        if  self.password.text().isEmpty() or self.username.text().isEmpty():
            raise ValueError("At least one of the required fields is missing!")
        # validate username if there is a regex for it
        if self.username_regex is not None:
            name_regex = QRegExp(self.username_regex)
            # Ignore case.
            name_regex.setCaseSensitivity(Qt.CaseInsensitive)
            if not name_regex.exactMatch(self.username.text()):
                raise ValueError, "Invalid username!"
        
    
    def get_connection(self):
        """ Try to establish connection with the Ovation service. """
        
        # Display status of this step.
        self.status.setTextFormat(Qt.RichText)
        self.status.setText("<b><font color=purple>Checking Ovation" + 
                            " Credentials...</font></b>")
        self.status.repaint()
        # Validate fields.
        try:
            self.__validate()
        except ValueError, e:
            self.status.setText("<b><font color=crimson> Input credentials" +
                                " are invalid format:<br>" + str(e))
            return
        # Try connecting.
        try:
            self.connection = check_ovation_credetials(
                                                       self.username.text(),
                                                       self.password.text())
        except ValueError, e:
            self.status.setText("<b><font color=crimson> Failed Connecting!" +
                                "<br>" + str(e))
            return
           
        if self.connection is None:
            self.status.setText("<b><font color=crimson> Failed Connecting!" +
                                "<br>Unknown Error!")
            return
        else:
            # Raise the accept signal, which closes dialog.
            self.accept()

    def __init__(self, parent=None, username=None,
                 password=None, username_is_email=True):
        """ Initialize a simple two field form."""
        super(GetOvationCredentials, self).__init__(parent)
        # Add the line edit boxes
        self.username = QLineEdit("Enter Ovation username")
        if username:
            self.username.setText(username)
        self.password = QLineEdit(password)
        # Set password echo property so that the typing characters are
        # only visible as they are entered
        self.password.setEchoMode(QLineEdit.Password)
        self.status = QLabel("Try out your credentials\n" +
                             "for the Ovation service")
        self.status.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status.setSizePolicy(QSizePolicy(QSizePolicy.Expanding))
        # Add buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
                                     QDialogButtonBox.Cancel)
        # Set layout of widgets
        layout = QVBoxLayout()
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(buttonBox)
        layout.addWidget(self.status)
        self.setLayout(layout)
        # Focus on the username field first
        self.username.selectAll()
        self.username.setFocus()
        # Assume email username 
        if username_is_email:
            self.username_regex = "[A-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,4}"
        else:
            self.username_regex = None           
        self.password.setPlaceholderText("Enter password")
        # Connection object
        self.connection = None
        # Add signals
        self.connect(buttonBox, SIGNAL("accepted()"),
                     self.get_connection)
        self.connect(buttonBox, SIGNAL("rejected()"),
                     self, SLOT("reject()"))
        self.setWindowTitle("Ovation credentials")
        
        # connection object
        self.connection = None

def get_file_resources(file_paths=None, gui=None, **kwargs):
    """ Find and validate a collection of file resources. """
    
    # TODO: add filter for excluding files
    # List of file paths to process.
    path_list = []
    # If paths are not provided, request manual input
    if file_paths is None:
        # TODO: populate
        pass
    else:
        # Validate paths. Coerce into the file_paths into a list first
        for file_path in list(file_paths):
            # Remove non existant paths
            # TODO add to logger
            if not path.exists(file_path):
                continue
            # If a directory was given as an argument, add all files.
            if path.isdir(file_path):
                # If recursive option, get all the files from subdirectories.
                # TODO: option of options in argparse?
                if 'recursive' in kwargs and kwargs['recursive']:
                    for (directory, directory_names, file_names) in \
                                walk(file_path):
                        for file_name in file_names:
                            # Make sure there are no duplicates.
                            abs_file_name_path = path.join(directory, file_name)
                            if abs_file_name_path not in path_list:
                                # Add the file path to the list.
                                path_list.append(abs_file_name_path)
                # Only add the files under current directory.
                else:
                    # Avoid duplicates.
                    for resource_name in listdir(file_path):
                        if path.isfile(path.join(file_path,
                                                 resource_name)):
                            abs_file_name_path = path.join(file_path,
                                                           resource_name)
                            if abs_file_name_path not in path_list:
                                path_list.append(abs_file_name_path)
            # File resource.
            elif path.isfile(file_path):
                if file_path not in path_list:
                    path_list.append(file_path)
                    
    return path_list

def get_ovation_connection(username = None,
                           password = None,
                           gui=False,
                           **kwargs
                           ):
    return 1
    """ Get user credentials for an Ovation account.
    If gui is True, a dialog box shows up for an interactive authentication.
    """
    # Show dialog to obtain credentials
    if gui:
        app = QApplication(sys.argv)
        dialog = GetOvationCredentials(username=username, password=password)
        # Show dialog modally
        if dialog.exec_():
            return dialog.connection
        else:
            # TODO: log this
            return None
        
    # get credentials via command line interface
    else:
        # Process username first if not passed.
        validate_username = None
        username_is_email = None
        # Email validation regular expression
        if "username_is_email" in kwargs:
            username_is_email = kwargs["username_is_email"]
            if username_is_email:
                validate_username = re.compile(
                        "[A-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,4}",
                        re.IGNORECASE)
        # Keep asking for valid input until given or exit command input.
        while username is "" or username is None or \
                  (not validate_username.match(username) if validate_username
                   else False):
            username = raw_input("Enter valid Ovation user name (or exit): ")
            if username_is_email and not validate_username.match(username):
                    print("User name must be an email!")
            if username == "exit":
                # TODO: Log?
                return None
        # Process password
        if password is None or password == "":
            password = getpass.getpass("Enter Ovation password: ")
        try:
            connection = check_ovation_credetials(username, password)
        except Exception, e:
            print "Failed connecting. Exception:"
            print e
            # Try again until user quits
            connection = get_ovation_connection(None, None, gui=False,
                                   username_is_email=username_is_email)
        return connection

def insert_measurement(username=None, password=None, file_paths=None,
                       project_name=None, experiment_name=None,
                       epoch_start=None, epoch_end=None, silent=False,
                       gui = False, **kwargs):
    """ Insert the given measurement into the Ovation database."""
    #TODO: start a separate thread and do the actual work there?
    
    # TODO: for silent runs (i.e unsupervised) check completeness of arguments
    # first and log error if invalid, followed by graceful return.

    # Get Ovation credentials. This will validate credential parameters too.
    # If one of the credential fields is not given, manual user input happens.
    # connection is an Ovation "DataContext" connection interface object.
    connection = get_ovation_connection(username=username,
                                        password=password,
                                        gui=gui,
                                        **kwargs)
    if connection is None:
        if silent:
            # TODO: Log this event!
            return None
        else:
            raise ValueError("Could not connect to the Ovation service")
    
    # Get a list of measurement paths to upload to the database.    
    measurements = get_file_resources(file_paths=file_paths,
                                      gui=gui,
                                      **kwargs)
    print "Getting measurements..."
    for measurement in measurements:
        print measurement
    return

    if file_paths is None:
        # Display UI for file/folder choosing
        pass
    
    # Get Projects and check if project in which we want to insert our
    # measurement exists.
    projects = connection.getProjects()
    for project in projects:
        if project.getName() == project_name:
            # we found the project
            print "Found project: ", project.getName()
            break
    else:
        # Project name not found, create one
        pass
    
    if experiment_name is None:
        # TODO: Create experiment from file name?
        pass
    
    # Get Experiments in project and check to see if one already exists.
    # If so, insert measurement there, otherwise create the experiment.    
    experiments = project.getExperiments()
    for experiment in experiments:
        if experiment.getPurpose() == experiment_name:
            # We found the experiment
            print "Found Experiment: ", experiment.getPurpose()
            break
    else:
        # Experiment did not exist, create one
        pass
    
    # Find or create epoch in none exist.
    epochs = experiment.getEpochs()
    
    for epoch in epochs:
        start_time_str = epoch.getStart().toString()
        # create datetime python object from string
        start_time = time_parser.parse(start_time_str)
        print start_time
        print epoch_start
        # TODO: compare times and pick smaller? Get times from measurements?
        if start_time == epoch_start:
            print "Times MATCH!"
            print "file paths: ", file_paths
            filepath = path.abspath(file_paths)
            print "absolute path: ", filepath
            #epoch.insertMeasurement(
            #                        )
        measurements = epoch.getMeasurements()
        if measurements is None:
            print "empty measurement?"
        else:
            for measurement in measurements:
                print measurement.getName()
    
    # TODO: delete. Useful  while debugging.
    if connection is not None:
            print "Are we connected?", connection.isAuthenticated()
            connection.getCoordinator().logout()
            print "Are we connected?", connection.isAuthenticated()    
    return

    # Add each file resource as a measurement in the Epoch
    if file_paths:
        for file_path in file_paths:
            # Add each file resource as a measurement
            pass
    print experiment.getPurpose()
    is_authenticated = connection.isAuthenticated()
    if is_authenticated:
        print "logging out...."
        connection.getCoordinator().logout()
        print "Are we connected?", connection.isAuthenticated()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='insert_measurement',
                    description='Ovation upload of a given measurement source',
                    epilog='let''s do it!', prefix_chars="-")
    parser.add_argument('--username', help='Ovation user name', nargs='?')
    parser.add_argument('--password', help='Ovation user password', nargs='?')
    parser.add_argument('--file_paths',
                        help='Paths to measurement file resources.',
                        nargs='+'
                        )
    parser.add_argument('--project_name',
                        help='Ovation project for the measurement(s).',
                        type = str
                        )
    parser.add_argument('--experiment_name',
                        help='Ovation experiment for the measurement(s).',
                        type = str
                        )
    parser.add_argument('--start',
                        help='Start time of the measurement in ISO 8601 format',
                        nargs = "+",
                        type = str)
    parser.add_argument('--version', '-v',
                        action='version', version="%(prog)s 1.0")
    
    args = parser.parse_args()
    # TODO: parse time appropriately
    #epoch_start = None
    if args.start:
        epoch_start = time_parser.parse(args.start[0])
        print epoch_start, type(epoch_start)
        print "file path", args.file_paths

    try:
        insert_measurement("Admir.Resulaj@nyumc.org",#args.username
                           password="cupcake123",
                           #args.password,
                           file_paths=args.file_paths,
                           project_name="Surprise laser probe",#args.project_name,
                           experiment_name="session_003",#args.experiment_name,
                           epoch_start=epoch_start,
                           gui=False,
                           username_is_email=True,
                           recursive=False)
    except ValueError, e:#Exception, e:
        sys.stderr.write("Error occured when inserting measurements:\n")
        sys.stderr.write(str(e))
    print args
'''
    dTypesToBeArchived = args.typeOfData
    if 'raw' in dTypesToBeArchived:
        #check if raw folder directory exists
        if not os.path.exists(rawfolder):
            stderr.write("Could not find raw_data folder...")
        else:
            if '*' in args.animalID:
                print "Archiving provided sessions of ALL animals..."
                # find all sessions and append animal IDs to the animalID argument list
                folderList = os.path.walk(rawfolder,parse_folders,None)
            
            for animal in args.animalID:         #For all mice folders, archive the required sessions
                #validate folder for animal
                # TODO: Search for folder if it fails...
                animalFolder = None
                animal = zfill(animal,ANIMALNUMBERWIDTH)
                animalFolderID = "mouse_"+animal
                tryPath = os.path.join(rawfolder,animalFolderID)
                if not os.path.exists(tryPath):
                    #exception or error?
                    #raise Exception(str("Could not find animal folder: "+tryPath))
                    stderr.write(str("Could not find animal folder: "+tryPath+"\n"))
                else:
                    animalFolder = tryPath
                if animalFolder:
                    for session in args.sessionID:
                        sourceFolder = None
                        #validate session folder
                        #TODO: invoke a find routine for finding the animal folder
                        session = zfill(session,SESSIONNUMBERWIDTH)
                        sessionFolderID = "sess_"+session
                        tryPath = os.path.join(animalFolder,sessionFolderID)
                        if os.path.exists(tryPath):
                            sourceFolder = tryPath
                        if sourceFolder:
                            command = "7z a "+animal+"_"+session+"_raw"+".7z"+" "+sourceFolder
                            print command
                            os.system(command)
                        else:
                            stderr.write(str("Could not find session folder: "+tryPath+"\n"))

'''
