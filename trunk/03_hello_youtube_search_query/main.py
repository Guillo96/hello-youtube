#!/usr/bin/env python

import cgi
import wsgiref.handlers
import os
import urllib

import gdata.urlfetch
import gdata.service
import gdata.youtube
import gdata.youtube.service

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

gdata.service.http_request_handler = gdata.urlfetch

class MainPage(webapp.RequestHandler):
  def get(self):
    client = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    
    query.vq = 'bicycle'
    query.orderby = 'viewCount'
    query.max_results = '5'

    feed = client.YouTubeQuery(query)

    self.response.out.write('<html><body>')

    for entry in feed.entry:
      self.response.out.write('<p>Title: %s </p>' % entry.title.text)
      self.response.out.write('<p>Description: %s </p>' % entry.title.text)
      self.response.out.write('<p><img src="%s"></p>' % entry.media.thumbnail[0].url)

    self.response.out.write('</body></html>')

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()