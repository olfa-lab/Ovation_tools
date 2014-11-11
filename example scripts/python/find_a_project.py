'''
Created on Nov 10, 2014

@author: admiracle

This script shows how to find an object by name in the database
Refer to http://javadoc.ovation.io/ for complete API calls
'''

# import the new_data_context function to use for establishing a connection with the Ovation server
from ovation.connection import new_data_context

# Connect to the Ovation service with provided credentials
# This will ask for your password in the console/terminal from which this script is run
con = new_data_context('Admir.Resulaj@nyumc.org',)

#TODO: how to query? Currently the query method of a Datacontext object requires a class?