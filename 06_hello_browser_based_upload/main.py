# Copyright (C) 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = ('api.jscudder (Jeffrey Scudder), '
              'api.jhartmann@gmail.com (Jochen Hartmann)')


import wsgiref.handlers
import urllib
import cgi
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
import gdata.service
import gdata.youtube
import gdata.youtube.service
import gdata.media
import gdata.geo
import gdata.urlfetch

gdata.service.http_request_handler = gdata.urlfetch


class StoredToken(db.Model):
  user_email = db.StringProperty(required=True)
  session_token = db.StringProperty(required=True)
  target_url = db.StringProperty(required=True)
  developer_key = db.StringProperty()


class AuthSub(webapp.RequestHandler):

  def __init__(self):
    self.current_user = None
    self.token_scope = None
    self.client = None
    self.token = None
    self.feed_url = 'http://gdata.youtube.com/feeds/api/users/default/uploads'
    self.youtube_scope = 'http://gdata.youtube.com'
    self.developer_key = None

  def get(self):
    self.client = gdata.youtube.service.YouTubeService()
    self.my_app_domain = 'http://' + self.request._environ['HTTP_HOST']
    self.response.out.write("""<html><head><title>
        hello_browser_based_upload: Browser based video upload demo</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        """)
    # Get the current user
    self.current_user = users.GetCurrentUser()
    self.response.out.write('</head><body>')
    # Allow the user to sign in or sign out

    

    for param in self.request.query.split('&'):
      if param.startswith('token_scope'):
        self.token_scope = urllib.unquote_plus(param.split('=')[1])
      elif param.startswith('token'):
        self.token = param.split('=')[1]
      elif param.startswith('feed_url'):
        self.feed_url = urllib.unquote_plus(param.split('=')[1])

    if self.token and self.feed_url and not self.token_scope:
      self.token_scope = self.feed_url


    if self.current_user:
      self.response.out.write('<a href="%s">Sign Out</a><br /><br />' % (
          users.CreateLogoutURL(self.request.uri)))
      if self.LookupToken():
        self.response.out.write('<div id="video_listing">')
        self.FetchFeed()
        if self.LookupDevKey():
          self.DisplayUploadForm()
          self.DisplayChangeDevKeyForm()

        else:
          self.DisplayDevKeyForm()
        self.response.out.write('</div>')

      # not authenticated...
      else:  
        if self.token:
          self.UpgradeAndStoreToken()
        else:
          # request a one-time token
          self.response.out.write('<div id="sidebar"> '
              '<div id="scopes"><h4>Request a token</h4><ul>')
          self.response.out.write('<li><a href="%s">YouTube API</a></li>' % (
              self.client.GenerateAuthSubURL(
              self.my_app_domain + '/' + '?token_scope=' + self.youtube_scope, 
              self.youtube_scope, secure=False, session=True))
              )
    else:
      self.response.out.write('<a href="%s">Sign In</a><br />' % (
          users.CreateLoginURL(self.request.uri)))

    

  def FetchFeed(self):
    # Attempt to fetch the feed.
    if not self.client:
      self.client = gdata.youtube.service.YouTubeService()

    try:
      feed = self.client.GetYouTubeVideoFeed(self.feed_url)

      self.response.out.write(
          '<span class="listing_title">My Videos</span><br /><br />')
      self.response.out.write(
          '<table border="0" cellpadding="2" cellspacing="0">')

      for entry in feed.entry:
        self.response.out.write('<tr><td class="thumbnail">')
        if len(entry.media.thumbnail) > 0:
          self.response.out.write(
              '<img src="%s"></p>' % entry.media.thumbnail[0].url)
        else:
          self.response.out.write('&nbsp;')
        self.response.out.write('</td>')

        self.response.out.write('<td valign="top">')
        self.response.out.write(
            '<span class="video_title">%s </span><br />' % entry.title.text)
        self.response.out.write(
            '<span class="video_description">%s </span><br />' % 
            entry.media.description)
        self.response.out.write(
            '<span class="video_category"><strong>%s</strong></span>' % 
            entry.media.category)
        self.response.out.write('<span class="video_published"> | published '
            'on %s</span><br />' % (entry.published.text.split('T')[0] + ' at ' +
            entry.published.text.split('T')[1][:5] + ' PST'))
        self.response.out.write('<span class="video_keywords"><strong>Keywords:'
            '</strong> %s </span><br />' % entry.media.keywords)


        self.response.out.write('</td></tr>')
        self.response.out.write(
          '<tr><td height="20" colspan="2"><hr class="slight"/></tr>')
      
      self.response.out.write('</table><br />')

    except gdata.service.RequestError, request_error:
      # If fetching fails, then tell the user that they need to login to
      # authorize this app by logging in at the following URL.
      if request_error[0]['status'] == 401:
        self.response.out.write(
            '<div id="sidebar"><div id="scopes"><h4>Request a token</h4><ul>')
        self.response.out.write(
            '<li><a href="%s">YouTube API</a></li>' % (
            self.client.GenerateAuthSubURL(
            self.my_app_domain + '/' + '?token_scope=' + self.youtube_scope, 
            self.youtube_scope, secure=False, session=True))
        )
      else:
        self.response.out.write(
            'Something else went wrong, here is the error object: %s ' % (
                str(request_error[0])))

  def post(self):
    self.response.out.write("""<html><head><title>
        hello_authsub: Authenticate to the YouTube API</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        </head><body>""")

    self.current_user = users.GetCurrentUser()
    developer_key = cgi.escape(self.request.get('developer_key'))
    self.response.out.write("<p>Storing developer key: %s" % developer_key)
    # look up token
    stored_tokens = StoredToken.gql('WHERE user_email = :1',
        self.current_user.email())
    for token in stored_tokens:
        new_token = StoredToken(user_email=token.user_email, 
            session_token=token.session_token, target_url=token.target_url, 
            developer_key=developer_key)
        token.delete()
    new_token.put()
    self.response.out.write("<br /><br /><a href="">Go back to main page</a>")

  def UpgradeAndStoreToken(self):
    self.client.auth_token = self.token
    self.client.UpgradeToSessionToken()
    if self.current_user:
      new_token = StoredToken(user_email=self.current_user.email(), 
          session_token=self.client.GetAuthSubToken(), 
          target_url=self.token_scope)
      new_token.put()

  def LookupToken(self):
    if self.feed_url and self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        if self.feed_url.startswith(token.target_url):
          self.client.auth_token = token.session_token
          return True

  def LookupDevKey(self):
    if self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        if token.developer_key:
          self.client.developer_key = token.developer_key
          return True

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
    
  def DisplayDevKeyForm(self):
    self.response.out.write("""<br /><div id="dev_key_form">
    <form action="/" method="post" >
      Enter your developer key <input type="text" name="developer_key" />
      <input type="submit" value="Go"/>
    </form></div>
    """)

  def DisplayChangeDevKeyForm(self):
    self.response.out.write("""<br /><hr class="slight"><br />
    <div id="dev_key_form">
    Current Developer Key stored:<br />
    <form action="/" method="post" >
      <input type="text" name="developer_key" value="%s" size="90"/><br />
      <input type="submit" value="Update"/>
    </form></div>""" % 
    self.client.additional_headers['X-GData-Key'].split('=')[1])
    
def main():
  application = webapp.WSGIApplication([('/.*', AuthSub),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
