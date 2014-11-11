'''
Created on Nov 7, 2014

@author: admiracle

This script has the few steps required for making a connection to your Ovation database through Python
Refer to http://javadoc.ovation.io/ for complete API calls

'''

# import the new_data_context function to use for establishing a connection with the Ovation server
from ovation.connection import new_data_context

# example of how to print usage of function
print new_data_context.__name__, "\n", new_data_context.__doc__

# pass your Ovation user name as the argument 
# This will prompt for your password in the System out stream (The terminal/console if you invoked the
# the function through an interactive python session).
# If there is an updated API, upon successful authentication of your credentials, the function will
# automatically download the new API library (Java jar files)
# Warning! If this is run through Eclipse's console, the password will be visible. Some terminals may not
# support password hiding.
connection = new_data_context('Admir.Resulaj@nyumc.org')
# Alternatively, you may pass the password to the function too. Of course, your password will be visible in this case
# either in the console or script.
# connection = new_data_context('username', 'password')

# This should display your name and verify that you are indeed authenticated and can use the service
print connection.getAuthenticatedUser().getUsername()

# Test to see if we are Authenticated
is_authenticated = connection.isAuthenticated()
print "Are we connected?", is_authenticated
if is_authenticated:
    print "logging out...."
    connection.getCoordinator().logout()
    print "Are we connected?", connection.isAuthenticated()