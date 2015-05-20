# Introduction #

This codelab will take you through the basics of using the Google Data Python Client Library with App Engine. It will go from fetching feeds, to authentication, to uploading a video to YouTube. All code samples in this codelab can be found [here](http://code.google.com/p/hello-youtube/source/browse).

# Before We Start #

Here are the things you'll need starting the first hour:

  * Knowledge of [Python](http://python.org)
  * [Python 2.5](http://python.org/download/) on your local machine
  * [App Engine SDK](http://code.google.com/appengine/downloads.html)

Things you'll need starting the second hour:

  * YouTube [Developer Key](http://code.google.com/apis/youtube/dashboard/)
  * YouTube [Account](http://youtube.com/signup) (preferably a test account with a private video uploaded to test authenticated feeds)

After the session:

  * Sign up for an [App Engine Account](http://appengine.google.com) if you haven't already to deploy your awesome app to production!

Please also hop into our IRC channel if you feel so inclined:

  * irc.freenode.net port 6667
  * #youtubecodelab

If you don't have a IRC client installed, there are web-based clients:
  * http://www.mibbit.com

Finally, documentation. We're not going over everything, so go through the docs when you get a chance.

  * [YouTube API Reference Guide](http://code.google.com/apis/youtube/reference.html)
  * [YouTube API Protocol Guide](http://code.google.com/apis/youtube/developers_guide_protocol)
  * [App Engine docs](http://code.google.com/appengine/docs/)

# Hello App Engine #

Here's a crash course in App Engine. For more detailed documentation, refer to the [App Engine docs](http://code.google.com/appengine). We're assuming all of your project files are in a folder named `Codelab`.

  * Create a file named `app.yaml`, your app's configuration file

```
application: codelab
version: 1
runtime: python
api_version: 1

handlers:
- url: /.*
  script: main.py
```

  * Now create `main.py` that you just referenced

```
import wsgiref.handlers

from google.appengine.ext import webapp

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Hello, App Engine!')

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
```

  * Assuming you've downloaded and installed the SDK, start up your development webserver: `dev_appserver.py /path_to_project/Codelab/`
  * Go to http://localhost:8080 to check it out.

All the source files can be browsed [here](http://code.google.com/p/hello-youtube/source/browse) under [01\_hello\_app\_engine](http://code.google.com/p/hello-youtube/source/browse/trunk/01_hello_app_engine/). Or, download the zip files [here](http://hello-youtube.googlecode.com/files/01_hello_app_engine.zip).

## Note about deploying on a Mac ##
You can use the App Engine Launcher instead of the command line

  1. Drag your project folder into the Launcher to add it
  1. Click "Run"

# Hello YouTube #

Let's fiddle around with fetching feeds on the command line. Download the client library source files [here](http://hello-youtube.googlecode.com/files/youtube_extensions_source.zip). Place the `atom` and `gdata` folders into your `Codelab` folder. Navigate to `Codelab` and start up your Python interpreter.

Imports

```
>>> import gdata.youtube
>>> import gdata.youtube.service
```

Creating a service object

```
>>> client = gdata.youtube.service.YouTubeService()
```

Getting a video feed with that service object

```
>>> feed = client.GetMostViewedVideoFeed()
```

Feed now contains a list of video entries. Let's look at the structure. We'll import pretty print so we can see the structure more clearly.

```
>>> from pprint import pprint as px
>>> px(feed.__dict__)
>>> px(feed.entry[0].__dict__)
```

Accessing metadata. Most of the metadata can be found in the media group element. (When in doubt, use dict to look at the objects.)

```
>>> px(feed.entry[0].media.__dict__)
>>> px(feed.entry[0].media.category.__dict__)
```

# YouTube + App Engine #

To use the Google Data Python Client Library with your Google App Engine application, simply place the library source files in your application's directory. The `atom/` and `gdata/` source files are available [here](TODO.md). The only other step is to set the `gdata.service.http_request_handler` to use `gdata.urlfetch`.

Let's take what we just learned about using the client library with the API, and put it into a running App Engine app. Add these calls into the `get` method.

```
import wsgiref.handlers

import gdata.urlfetch
import gdata.service
import gdata.youtube
import gdata.youtube.service

from google.appengine.ext import webapp	

class MainPage(webapp.RequestHandler):
  def get(self):
    client = gdata.youtube.service.YouTubeService()
    feed = client.GetMostViewedVideoFeed()

    self.response.out.write('<html><body>')

    for entry in feed.entry:
      self.response.out.write('<p>Title: %s </p>' % entry.title.text)
      self.response.out.write('<p>Description: %s </p>' % entry.media.description.text)
      self.response.out.write('<p><img src="%s"></p>' % entry.media.thumbnail[0].url)

    self.response.out.write('</body></html>')

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
```

## Assignment #1 ##

Make a page that retrieves and prints out the title, description, and first thumbnail from the [Most Viewed](http://code.google.com/apis/youtube/reference.html#Standard_feeds) standard feed.

HINT:
  * Check out the YouTube [service class](http://code.google.com/p/hello-youtube/source/browse/trunk/02_hello_python_client_library/gdata/youtube/service.py#245)


Solution can be found [here](http://code.google.com/p/hello-youtube/source/browse/trunk/02_hello_python_client_library/main.py)

## Assignment #2 ##

Do a parameterized query to the search feed. Restrict the results to 5 videos with the term 'bicycle dalmation' in the metadata. Order the results by view count.

HINTS:
  * Create a new `YouTubeVideoQuery()` object
  * All the [parameters](http://code.google.com/apis/youtube/reference.html#Query_parameter_definitions) can be set as attributes on this object -- a max\_result, a vq (a video query/search term), an orderby.
  * Once you have the query object built, run `YouTubeQuery(query)` on the service object to send the request


Solution can be found [here](http://code.google.com/p/hello-youtube/source/browse/trunk/03_hello_youtube_search_query/main.py).

## Assignment #3 ##

Take text input from the user and do a search query. Print out the results and embed the video.

HINTS:
  * [Form handling](http://code.google.com/appengine/docs/gettingstarted/handlingforms.html) in App Engine
  * To can use the standard embed code found on every YouTube watch page. All you need to replace is the SWF URL for the video. This can be accessed with a helper function in the [YouTubeVideoEntry](http://code.google.com/p/hello-youtube/source/browse/trunk/02_hello_python_client_library/gdata/youtube/__init__.py#339) data class.


Solution can be found [here](http://code.google.com/p/hello-youtube/source/browse/trunk/04_hello_user_input/main.py).

# AuthSub #

Now we'll walk through an example implementation using [AuthSub](http://code.google.com/apis/accounts/docs/AuthForWebApps.html) authentication. The application will authenticate the user and then print out the user's uploaded videos, including private videos.

Working source can be browsed [here](http://code.google.com/p/hello-youtube/source/browse/trunk/05_hello_authsub/). Or downloaded [here](http://hello-youtube.googlecode.com/files/05_hello_authsub.zip).

### Using the App Engine Users API ###

We want to authenticate our current App Engine user to YouTube, so we have to store their user name and then associate it with a YouTube token.

Import the users module:

```
from google.appengine.ext import users
```

Get the current user if they're logged into Google Accounts, otherwise, direct them to log in. Make the "Sign In" and "Sign Out" links.

```
    self.current_user = users.GetCurrentUser()

    self.response.out.write('<body>')
    if self.current_user:
      self.response.out.write('<a href="%s">Sign Out</a><br>' % (
          users.CreateLogoutURL(self.request.uri)))
    else:
      self.response.out.write('<a href="%s">Sign In</a><br>' % (
          users.CreateLoginURL(self.request.uri)))

```

### Generating the AuthSub Link ###

These variables are added in the init() constructor:

```
    self.youtube_scope = 'http://gdata.youtube.com'
    self.my_app_domain = None # This will be set to the current app domain when a get() request
```

Print out the URL for the user to click on using the current domain and the YouTube scope.

```
          self.my_app_domain = 'http://' + self.request._environ['HTTP_HOST']
          
          self.response.out.write('<div id="sidebar"> '
              '<div id="scopes"><h4>Request a token</h4><ul>')
          self.response.out.write('<li><a href="%s">YouTube API</a></li>' % (
              self.client.GenerateAuthSubURL(
              self.my_app_domain, self.youtube_scope, secure=False, session=True))
              )
```

### Retrieving and Updating a Token ###

```
  def __init__(self):
    self.current_user = None
    self.token_scope = None
    self.client = gdata.youtube.service.YouTubeService()
    self.token = None
    self.feed_url = 'http://gdata.youtube.com/feeds/api/users/default/uploads'
    self.youtube_scope = 'http://gdata.youtube.com'

```

Parsing the one-time use token out of the return URL.

```

    for param in self.request.query.split('&'):
      if param.startswith('token_scope'):
        self.token_scope = urllib.unquote_plus(param.split('=')[1])
      elif param.startswith('token'):
        self.token = param.split('=')[1]

    if self.token and self.current_user:
      self.client.auth_token = self.token
      self.client.UpgradeToSessionToken()

    
```

### Storing a Session Token ###

Now we're going to use the App Engine [Datastore](http://code.google.com/appengine/docs/datastore/) to store the token and the user's email.

```
from google.appengine.ext import db
```

Creating the data structure to store the token:

```
class StoredToken(db.Model):
  user_email = db.StringProperty(required=True)
  session_token = db.StringProperty(required=True)
```

Write a helper function to upgrade the one-time use token and store the session token.

```
  def UpgradeAndStoreToken(self):
    self.client.auth_token = self.token
    self.client.UpgradeToSessionToken()
    if self.current_user:
      new_token = StoredToken(user_email=self.current_user.email(), 
          session_token=self.client.GetAuthSubToken())
      new_token.put()
```

### Note about App Engine Admin Console ###

We'll be storing the session token using the App Engine Datastore, so now's a good time to bring up the admin console.
  * http://localhost:8080/_ah/admin/

Here you can view the content of the Datastore.
  * http://localhost:8080/_ah/admin/datastore
  * Enter the name of the data structure that you created in the app to view contents
    * In the case of our example, "StoredToken"


### Using a Stored Token ###


```
      if self.LookupToken():
        self.response.out.write('<div id="video_listing">')
        self.FetchFeed()
        self.response.out.write('</div>')
```

```
  def LookupToken(self):
    if self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        self.client.auth_token = token.session_token
        return True
```

Client is already authenticated, so we can grab the authenticated user's upload feed. Remember to enclose the request in a `try` `except` block.

```
  def FetchFeed(self):
    try:
      feed = self.client.GetYouTubeVideoFeed(self.feed_url)
    # ... iterate through feed, etc. 

```

# Browser-Based Upload #

We'll now make a small app that uploads a video to YouTube using the browser-based upload method.

Working source can be browsed [here](http://code.google.com/p/hello-youtube/source/browse/trunk/06_hello_browser_based_upload/). Or downloaded [here](http://hello-youtube.googlecode.com/files/06_hello_browser_based_upload.zip).

Create a new variable to store the developer key.

```
    self.developer_key = None
```

In the`post()` method, we can store it.

```

    developer_key = cgi.escape(self.request.get('developer_key'))
```

Now display a video metadata form - the form action will post to `/upload`.

```
  def DisplayUploadForm(self):
    self.response.out.write("""<br /><div id="upload_form">
      <strong>Upload a new Video</strong><br /><br />
      <form action="/upload" method="post" >
      Video Title<br /><input type="text" name="video_title" /><br /><br />
      Video Description<br /><textarea cols="50" name="video_description">
      </textarea><br /><br />
      Select a Category <select name="video_category">
        <option value="Autos">Autos &amp; Vehicles</option>
        <option value="Music">Music</option>
        <option value="Animals">Pets &amp; Animals</option>
        <option value="Sports">Sports</option>
        <option value="Travel">Travel &amp; Events</option>
        <option value="Games">Gadgets &amp; Games</option>
        <option value="Comedy">Comedy</option>
        <option value="People">People &amp; Blogs</option>
        <option value="News">News &amp; Politics</option>
        <option value="Entertainment">Entertainment</option>
        <option value="Education">Education</option>
        <option value="Howto">Howto &amp; Style</option>
        <option value="Nonprofit">Nonprofit &amp; Activism</option>
        <option value="Tech">Science &amp; Technology</option>',
      </select><br /><br />
      Enter some tags to describe your video <em>(separated by spaces)</em>
      <br /><br />
      <input type="text" name="video_tags" />
      <input type="submit" value="Go"/>
    </form></div>
    """)
```

## Upload.py ##

In the `post()` method, we construct the `YouTubeVideoEntry`:

```
    if self.LookupToken() and self.LookupDevKey():
      video_title = cgi.escape(self.request.get('video_title'))
      video_description = cgi.escape(self.request.get('video_description'))
      video_category = cgi.escape(self.request.get('video_category'))
      video_tags = cgi.escape(self.request.get('video_tags'))
      
      my_media_group = gdata.media.Group(
        title = gdata.media.Title(text=video_title),
        description = gdata.media.Description(description_type='plain',
                                            text=video_description),
        keywords = gdata.media.Keywords(text=video_tags),
        category = gdata.media.Category(
          text=video_category,
          scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
          label=video_category),
      player=None
      )
      
      video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
```

Post the metadata and get the token back:

```
      self.server_response = self.client.GetFormUploadToken(video_entry)

      post_url = self.server_response[0]
      youtube_token = self.server_response[1]
```

Create the form for the users to include the video file:

```
      self.response.out.write("""<div id="file_upload">Upload your video file
          <br /><br />
          <form action="%s?nexturl=%s" method="post" 
          enctype="multipart/form-data">
          <input name="file" type="file" size="50"/>
          <input name="token" type="hidden" value="%s"/>
          <br /><input value="Go" type="submit" />
          </form></div>""" % (post_url, self.my_app_domain, youtube_token))
```