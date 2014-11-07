'''
Created on Oct 29, 2014

to use, must install google API:
    pip install --upgrade google-api-python-client

@author: admiracle
'''

# This is for enabling logging of events
import logging
import httplib2
import argparse
from os.path import exists, expanduser

from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets, AccessTokenRefreshError

import gdata.spreadsheet.service
import gdata.spreadsheets.client
import gdata.calendar.client
from gdata.client import GDClient
from gdata.gauth import OAuth2TokenFromCredentials

# URL to use for authenticating via OAuth 2.0 protocol. Can only access via SSL. HTTP requests are ignored
# These are not used but put here for convenience if you want to implement authentication differently in the future
# The following can also be accessed at oauth2client.GOOGLE_AUTH_URI , oauth2client.GOOGLE_TOKEN_URI
oauth_url = "https://accounts.google.com/o/oauth2/auth"
token_endpoint = "/o/oauth2/token"

# URLs for google spreadsheet and google drive purely for convenience
SHEET = "https://spreadsheets.google.com/feed"
DRIVE = "https://www.googleapis.com/auth/drive.file "

class GooglePermission(object):
    '''
    Get a permission object for a Google API service. This uses the OAuth 2.0 methodology
    '''


    def __init__(self, service_endpoints, app_credentials = None, log_level = None):
        '''
        Initialize a GetPermission object for the given service endpoints (urls, space separated).
        
        service_endpoints: Find the endpoint or "scope" that your application needs to access from the individual google API docs
        app_credentials: Second parameter is an app_credentials file (json) that you may optionally pass (object or path)
        logging: value from the logging library. They can be CRITICAL (or FATAL), ERROR, WARNING (or WARN), INFO, DEBUG, NOTSET
                Example. logging.DEBUG. Refer to the logging package for more info.
        
        '''
        # TODO. Accept a string and regex it trying to find the api at https://www.googleapis.com/discovery/v1/apis/
        # The JSON description of the API can be found at the above url + {API}/{Version}/Rest
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
        # TODO: Add the logging info to the objects that need logging
        log = logging.getLogger()
        if log_level is None or log_level not in logging._levelNames:
            log.setLevel(logging.INFO)
            raise Warning, "logging value specified invalid (set to INFO). Set argument to one in logging._levelNames"
        else:
            log.setLevel(log_level)
        
        # Empty storage to put keys in. This should be internal and subject to change
        # TODO: Enhance it for multiple key storage
        self._storage = Storage(None)
        # key is the object that stores the authorization code for accessing APIs. It has the token stored in _storage
        self.key = None
        
    def _check_storage(self):
        """ Check if storage exists """
        return exists(self._storage._filename)
    
    def get_permission(self, storage = None):
        """ Go through a flow of grabbing the authorize object/token required for making API calls to google services.
        
        If no storage provided, a browser will open to attempt to get authorization keys/tokens.
        Storage can be either a path to an existing file, a path to a file you wish to store keys,
        or a Storage object
        
        Should returns an OAuth2Credentials object if successful
        """
        
        # Get a flow object from the application credentials file we have
        # redirect_uri can also be localhost and localhost will be used later behind the scenes
        # TODO: Handle all errors
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
        # TODO: Delete after if we don't want to store the credentials/tokens????
        else:
            home_folder = expanduser("~")
            self._storage = Storage(home_folder + "\creds.dat")
        try:
            # Get the key object from the storage file
            key = self._storage.get()
            # If it still valid use this authorization key
            if key and not key.access_token_expired:
                self.key = key
            # The key exists, but it is expired. Use the refresh token to obtain new one
            elif key:
                try:
                    # Need to pass a http object to serve the request
                    key.refresh(httplib2.Http())
                except AccessTokenRefreshError:
                    print "Could not refresh current token. let's get a new one!"
                    #TODO: Reinitiate flow?
                finally:
                    # The process was successful
                    self.key = key
            # No key found. Go throught the whole flow and ask the user for authentication
            else:
                # get a default Argument Parser object from the tools package of oauth2client package
                parser = argparse.ArgumentParser(parents = [tools.argparser])
                # from this parser, get the default flags to be used in calling an HTTP request through a browser
                flags = parser.parse_args()
                # Run the helper command that will open the default browser and manage the HTTP session
                # It will return a credentials object
                credentials = tools.run_flow(flow, self._storage, flags)
                if credentials:
                    self.key = credentials
                else:
                    print "Failed authenticating!"
        except:
            print "Some error occured in getting permissions??"
        
        return self.key
                                
    def get_key(self):
        """ Return the key of the authorization or raise an error if key is empty """
        if self.key:
            return self.key
        else:
            raise ValueError, "key not found. Use get_permission to grab it again!"    
        
        
    def refresh(self):
        """ Refresh the authorization token from a refresh token that is presumably already saved in the storage object"""
        key = self._storage.get()
        try:
            # Need to pass a http object to serve the request
            key.refresh(httplib2.Http())
        except AccessTokenRefreshError:
            print "Could not refresh current token. let's get a new one!"
            #TODO: Reinitiate flow?
        finally:
            self.key = key
        
        return key

    def is_alive(self):
        """ Check for validity of a given authorization object """
        
        if self._check_storage():
            return self._storage.get().access_token_expired
        else:
            raise ValueError, "I could not find my storage file!"

# TODO: add state parameter when sending an authorization request. This state is round-triped back
# and aids in increasing security (cross-site-request-forgery) or pointing to the correct state the app needs to get back

if __name__ == "__main__":
    
    # Testing with a spreadsheet access
    # You need to provide your own json secrets if using some other application or project in the google console
    permission = GooglePermission(SHEET,
                                     'C:\git\Ovation_tools\import tools\ovation_secret.json',
                                      logging.DEBUG)
    # For even more details of traffic, can do the following if constructing your own http server
    # httplib2.debuglevel = 4

    storage = Storage('C:\git\Ovation_tools\import tools\credentials.dat')
    key = permission.get_permission(storage)
    
    # Check to see if the key authorization token is still valid and has not expired
    print "Is key alive? ", not key.access_token_expired
    # How to look at the key fields
    json_key = key.to_json()
    for item in json_key.split(","):
        print item
        
    # Now get a spreadsheet object as an example of using the authorization key

    # get a OAuth2Token object to pass to the spreadsheet client library. Our key is stored in a Credentials object
    # that was obtained from oauth2client flows. This process is used for discovery-based protocols as described in 
    # https://developers.google.com/discovery/v1/getting_started#background. Spreadsheet API is not using that format but
    # we can still use the same underlying authentication and make sure refreshes of the authorization tokens happen on both
    # service connection types. Also, we keep the key stored in the same storage object for either type of connection.
    auth_token = OAuth2TokenFromCredentials(key)
        
    # The gdata.spreadsheets.service package contains a SpreadsheetService class, but that one does not play as nicely
    # with the OAuth 2.0 authentication objects. Instead we use a SpreadsheetsClient object to handle the service requests
    
    """The following commented out block does not work...The OAuth2Token object does not play nicely with this service class -- which supports all older
     authentication methods. But those methods are deprecated. Bottom line: Avoid using this altogether. Provided here as an
     example of how not to build the service calls with a OAuth 2.0 authentication flow.
     
         sheet_service = gdata.spreadsheet.service.SpreadsheetsService()
         sheet_service = auth_token.authorize(sheet_service)
     
      -- The following method would actually set the key to OAuth 1.0 token type and fail when the service is used as the implementation is different
          Confusing as they have same names. But are different methodologies underneath...
      sheet_service.SetOAuthToken(sheet_service.auth_token)
      
      This fails when using oauth 2.0 tokens. While it is possible to sublcass and override the implementation, the methods used
      in SpreadSheetsService class have deprecated decorators. Avoid using this service and use the client service (see below)
         feed = sheet_service.GetSpreadsheetsFeed() """

    # Better and updated client library to use
    sheet_client = gdata.spreadsheets.client.SpreadsheetsClient()
    auth_token.authorize(sheet_client)
    # Or instead of the above we can do this after if authorization key changes: sheet_client.auth_token = auth_token
    sheets = sheet_client.get_spreadsheets()
    # iterate through spreadsheets and print the title. Note that the tile is the XML entry title for each Spreadsheet object
    for ssheet in sheets.entry:
        print ssheet.title
        
    # Query for a specific spreadsheet. Search by name. The name does not have to be exact
    my_query = gdata.spreadsheets.client.SpreadsheetQuery(title="Chemicals", title_exact=False)
    feed = sheet_client.get_spreadsheets(query = my_query)
    # From the returned feed, get the titles of the spreadsheets found, if any are found
    if feed.entry:
        for sheet in feed.entry:
            print sheet.title
    
    # Another example: Calendar service
    #calendar = gdata.calendar.client.CalendarClient()
    #auth_token.authorize(calendar)
    #feed = calendar.GetCalendarEventFeed()
    