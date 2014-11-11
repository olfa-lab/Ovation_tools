'''
Created on Nov 10, 2014

@author: admiracle

This script shows how to insert an experiment in a project you own.
'''

# import the new_data_context function to use for establishing a connection with the Ovation server
from ovation.connection import new_data_context
from ovation.conversion import asclass
from ovation.core import date_time

# pytz gives us access to a timezone list which we can use for building datetime objects to pass to Ovation API
import pytz
import datetime

# Connect to the Ovation service with provided credentials
# This will ask for your password in the console/terminal from which this script is run
con = None
def do_connect():
    return new_data_context('Admir.Resulaj@nyumc.org')
con = do_connect()    
# Some objects like datetime objects need to be converted so that the underlying JAVA library can understand them
from ovation.conversion import datetime as ovation_datetime

# Example of how to get project named "Surprise laser probe" by searching for its name
projects = con.getProjects()
project_uri = None
print "fetching projects..."
for project in projects:
    if project.getName() == "Surprise laser probe":
        print "Found project!"
        project_uri = project.getURI().toString()
        break
print "done fetching!"

# Now grab the project by URI. Note that URI needs to be known for this to work.
# Ideally, you would only iterate once and save the URIs of the projects locally
if project_uri is not None:
    project = asclass('Project', con.getObjectWithURI(project_uri))
    print project.getName()
else:
    raise ValueError, "could not find project"

# Now lets insert an experiment names "session_001"
# First make sure experiment does not exist so we don't insert double sessions
experiments = project.getExperiments()
for experiment in experiments:
    if experiment.getPurpose() == "session_008":
        date = experiment.getStart().toString()
        raise ValueError, "Experiment already exists and has date of " + date

# Grab the local current time with the argument being the EST time zone
#current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))
experiment_time = datetime.datetime(2014, 8, 18, tzinfo = pytz.timezone("US/Eastern"))

#experiment = project.insertExperiment("session_001", ovation_datetime(current_time))
experiment = project.insertExperiment("session_008", ovation_datetime(experiment_time))

if experiment:
    print experiment.getPurpose(), "was inserted!"
    print experiment.getStart().toString()
else:
    raise ValueError, "Could not insert experiment"
# Changing date of experiment example. Note that timezone will default to -4
# experiment.setStart(date_time(2014, 05, 02))
con.getCoordinator().logout()

