'''
Created on Nov 7, 2014

@author: admiracle

This script shows how to create a project, search for it by name, rename it and delete it
Refer to http://javadoc.ovation.io/ for complete API calls

'''

# pytz gives us access to a timezone list which we can use for building datetime objects to pass to Ovation API
import pytz
import datetime

# import the new_data_context function to use for establishing a connection with the Ovation server
from ovation.connection import new_data_context
# Some objects like datetime objects need to be converted so that the underlying JAVA library can understand them
from ovation.conversion import datetime as ovation_datetime

# Connect to the Ovation service with provided credentials
# This will ask for your password in the console/terminal from which this script is run
con = new_data_context('Admir.Resulaj@nyumc.org')

# Grab the local current time with the argument being the EST time zone
current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))

# Insert a new project. Note that you can insert many project with identical names. They have underlying different object IDs
con.insertProject('Testing...testing', 'Hello?', ovation_datetime(current_time))

# Test to see if this worked. Get all projects and iterate through the iterable
# stopping at the project we created in the previous step
projects = con.getProjects()
for project in projects:
    if project.getName() == 'Testing...testing':
        print "It worked!"
        print "Project name:", project.getName()
        print "Project Purpose:", project.getPurpose()
        print "Project Owner: ", project.getOwner().getUsername()
        break

# rename the project
if project.getName() == 'Testing...testing':
    print "Setting new name"
    project.setName('Testing done!')
else:
    print "Project not found!"
# One final check that the renaming occured
print "Project name: %s" % project.getName()

# delete project. The argument is None to indicate that this entity is the one being trashed
# project.trash(None)
con.getCoordinator().logout()