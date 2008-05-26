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
from pprint import pprint as px

gdata.service.http_request_handler = gdata.urlfetch


class StoredToken(db.Model):
  user_email = db.StringProperty(required=True)
  session_token = db.StringProperty(required=True)
  target_url = db.StringProperty(required=True)
  developer_key = db.StringProperty()


class Upload(webapp.RequestHandler):

  def __init__(self):
    self.current_user = None
    self.token_scope = None
    self.client = None
    self.token = None
    self.feed_url = 'http://gdata.youtube.com/feeds/api/users/default/uploads'
    self.youtube_scope = 'http://gdata.youtube.com'
    self.server_response = None

  def post(self):
    self.my_app_domain = 'http://' + self.request._environ['HTTP_HOST']
    self.response.out.write("""<html><head><title>
        hello_browser_based_upload: Browser based upload demo</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        </head>""")

    # Get the current user
    self.current_user = users.GetCurrentUser()
    self.client = gdata.youtube.service.YouTubeService()

    self.response.out.write('<body>')

    # logic
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
      
      try:
        self.server_response = self.client.GetFormUploadToken(video_entry)
      except gdata.service.RequestError, request_error:
        self.response.out.write('<div id="error">')
        self.response.out.write(request_error[0]['status'])
        self.response.out.write(request_error[0]['body'])
        if request_error[0]['reason']:
          self.response.out.write(request_error[0]['reason'])
        self.response.out.write(
            '<br /><a href="/" style="color: #000">'
            'click here to return</a></div>')
        return

      post_url = self.server_response[0]
      youtube_token = self.server_response[1]
      self.response.out.write("""<div id="file_upload">Upload your video file
          <br /><br />
          <form action="%s?nexturl=%s" method="post" 
          enctype="multipart/form-data">
          <input name="file" type="file" size="50"/>
          <input name="token" type="hidden" value="%s"/>
          <br /><input value="Go" type="submit" />
          </form></div>""" % (post_url, self.my_app_domain, youtube_token))
      
    else:  
      self.redirect("/")

  def LookupDevKey(self):
    if self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        if token.developer_key:
          self.client.developer_key = token.developer_key
          return True

  def LookupToken(self):
    if self.feed_url and self.current_user:
      stored_tokens = StoredToken.gql('WHERE user_email = :1',
          self.current_user.email())
      for token in stored_tokens:
        if self.feed_url.startswith(token.target_url):
          self.client.auth_token = token.session_token
          return True


def main():
  application = webapp.WSGIApplication([('/.*', Upload),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
