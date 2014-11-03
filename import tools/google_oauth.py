'''
Created on Oct 29, 2014

to use, must install google API:
    pip install --upgrade google-api-python-client

@author: admiracle
'''

# This is for enabling logging of events
import logging
import httplib2
import urllib2
from urlparse import urlparse
import argparse
from os.path import exists, expanduser

from oauth2client import tools, gce
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets, OAuth2WebServerFlow
import oauth2client

# URL to use for authenticating via OAuth 2.0 protocol. Can only access via SSL. HTTP requests are ignored
# These are not used but put here for convenience if you want to implement authentication differently in the future
# The following can also be accessed at oauth2client.GOOGLE_AUTH_URI , oauth2client.GOOGLE_TOKEN_URI
oauth_url = "https://accounts.google.com/o/oauth2/auth"
token_endpoint = "/o/oauth2/token"

class GooglePermission(object):
    '''
    Get a permission object for a Google API service
    '''


    def __init__(self, service_endpoints, app_credentials = None, log_level = None):
        '''
        Initialize a GetPermission object for the given service endpoints (urls, space separated).
        
        service_endpoints: Find the endpoint or "scope" that your application needs to access from the individual google API docs
        app_credentials: Second parameter is an app_credentials file (json) that you may optionally pass (object or path)
        logging: value from the logging library. They can be CRITICAL (or FATAL), ERROR, WARNING (or WARN), INFO, DEBUG, NOTSET
                Example. logging.DEBUG. Refer to the logging package for more info.
        
        '''
        # TODO: validate scope
        self.scopes = service_endpoints
        # TODO: add options for app_credentials selection (browse file system)
        if not app_credentials:
            pass
        elif not exists(app_credentials):
            raise ValueError, "Application credential file not found!"
        else:
            self.credentials = app_credentials
        # For debugging purposes set amount of logging you want. Messages go to Standard Output (console)
        # Since there are many server calls to get a permission and many things can go wrong, logging is advised to see where things may break
        log = logging.getLogger()
        if log_level is None or log_level not in logging._levelNames:
            log.setLevel(logging.INFO)
            raise Warning, "logging value specified invalid (set to INFO). Set argument to one in logging._levelNames"
        else:
            log.setLevel(log_level)
        
        # Empty storage to put keys in. This should be internal and subject to change
        # TODO: Enhance it for multiple key storage
        self._storage = Storage(None)
        # key is the object that stores the authorization code for accessing APIs. It is the token stored in _storage
        self.key = None  
        
    
    def get_permission(self, storage = None):
        """ Go through a flow of grabbing the authorize object/token required for making API calls to google services.
        
        If no storage provided, a browser will open to attempt to get authorization keys/tokens.
        Storage can be either a path to an existing file, a path to a file you wish to store keys,
        or a Storage object
        """
        
        # Get a flow object from the application credentials file we have
        # redirect_uri can also be localhost and localhost will be used later behind the scenes
        # TODO: Handle errors
        flow = flow_from_clientsecrets(self.credentials,
                                   scope=self.scopes,
                                   redirect_uri="urn:ietf:wg:oauth:2.0:oob")
        # if storage parameter is provided to the method, update internal storage
        if isinstance(storage, Storage):
            self._storage = storage
        # Assume otherwise this is a path for file where we want to store keys
        elif storage is not None:
            self._storage = Storage(storage)
        # Create a storage object in user home folder
        # TODO: Delete after???
        else:
            home_folder = expanduser("~")
            self._storage = Storage(home_folder + "\creds.dat")
        try:
            key = self._storage.get()
            if key:
                self.key = key
            else:
                # No key found. Go fetch it!
                # get a default Argument Parser object from the tools package of oauth2client package
                parser = argparse.ArgumentParser(parents = [tools.argparser])
                # from this parser, get the default flags to be used in calling an HTTP request through a browser
                flags = parser.parse_args()
                # Run the helper command that will open the default browser and manage the HTTP session
                # It will return a credentials object
                credentials = tools.run_flow(flow, self._storage, flags)
                print credentials
                if credentials:
                    self.key = credentials
        except:
            print "Some error occured???"
        
        return self.key
                                
    def get_key(self):
        """ Return the key of the authorization or raise an error if key is empty """
        if self.key:
            return self.key
        else:
            raise ValueError, "key not found. Use get_permission to grab it again"    
        
        
    def refresh(self):
        """ If access is denied, refresh the token """
        pass
    
    def is_alive(self, authorization_object):
        """ Check for validity of a given authorization object """
        pass
       



# If adding sheets also need drive api scope https://www.googleapis.com/auth/drive.file    
spreadsheet_scope = "https://spreadsheets.google.com/feeds"
uri = urlparse(oauth_url)
# TODO: add state parameter when sending an authorization request. This state is round-triped back
# and aids in increasing security (cross-site-request-forgery) or pointing to the correct state the app needs to get back
# TODO: use a local host port as redirected flow   redirect_uri=http://localhost:9004& Firewall might block?
# or change run_flow flags to automatically close the window?


if __name__ == "__main__":
    # Testing with a spreadsheet access
    
    permission = GooglePermission(spreadsheet_scope,
                                     'C:\git\Ovation_tools\import tools\ovation_secret.json',
                                      logging.DEBUG)
    # For even more details of traffic, can do the following
    # httplib2.debuglevel = 4

    storage = Storage('C:\git\Ovation_tools\import tools\credentials.dat')
    key = permission.get_permission(storage)
    
    import json
    # introspect
    print key
    
    # Now get a spreadsheet object:
    


    
