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
    self.client = gdata.youtube.service.YouTubeService()

  def get(self):
    self.my_app_domain = 'http://' + self.request._environ['HTTP_HOST']
    self.response.out.write("""<html><head><title>
        hello_authsub: AuthSub demo</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        """)

    # Get the current user
    self.current_user = users.GetCurrentUser()
    self.response.out.write('</head><body>')

    # Split URL parameters if found
    for param in self.request.query.split('&'):
      if param.startswith('token_scope'):
        self.token_scope = urllib.unquote_plus(param.split('=')[1])
      elif param.startswith('token'):
        self.token = param.split('=')[1]
      elif param.startswith('feed_url'):
        self.feed_url = urllib.unquote_plus(param.split('=')[1])

    if self.current_user:
      self.response.out.write('<a href="%s">Sign Out</a><br /><br />' % (
          users.CreateLogoutURL(self.request.uri)))

      # See if we have a stored session token in the database
      if self.LookupToken():
        self.response.out.write('<div id="video_listing">')
        self.FetchFeed()
        self.response.out.write('</div>')

      # No saved token found
      else:
        # Check if we have a one-time use token in the URL parameters
        if self.token:
          self.UpgradeAndStoreToken()
          self.redirect('/')
        else:
          # No stored token found, no one-time use token set, but we have
          # a self.current_user, so present the option to get a token
          self.response.out.write('<div id="sidebar"> '
              '<div id="scopes"><h4>Request a token</h4><ul>')
          self.response.out.write('<li><a href="%s">YouTube API</a></li>' % (
              self.client.GenerateAuthSubURL(
              self.my_app_domain + '/' + '?token_scope=' + self.youtube_scope, 
              self.youtube_scope, secure=False, session=True))
              )
    else:
      # No self.current_user so build sign-in box
      self.response.out.write('<a href="%s">Sign In</a><br />' % (
          users.CreateLoginURL(self.request.uri)))

    

  def FetchFeed(self):
    # Get users video feed
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

  def UpgradeAndStoreToken(self):
    self.client.auth_token = self.token
    self.client.UpgradeToSessionToken()
    if self.current_user:
      new_token = StoredToken(user_email=self.current_user.email(), 
          session_token=self.client.GetAuthSubToken(), 
          target_url=self.token_scope)
      new_token.put()

  def LookupToken(self):
    if self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        if self.feed_url.startswith(token.target_url):
          self.client.auth_token = token.session_token
          return True

    
def main():
  application = webapp.WSGIApplication([('/.*', AuthSub),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
