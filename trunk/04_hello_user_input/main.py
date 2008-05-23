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
      
class SearchPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""
      <html>
        <body>
          <form action="/" method="post">
            <div><input type="text" name="content" /></div>
            <div><input type="submit" value="Search YouTube"></div>
          </form>
        </body>
      </html>""")
      
  def post(self):
    search_term = cgi.escape(self.request.get('content'))
    
    self.response.out.write("""
      <html>
        <body>
          <form action="/" method="post">
            <div><input type="text" name="content" value=%s /></div>
            <div><input type="submit" value="Search YouTube"></div>
          </form>""" % search_term)

    client = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    
    query.vq = search_term
    query.max_results = '5'
    feed = client.YouTubeQuery(query)
    
    for entry in feed.entry:
      swf_url = entry.GetSwfUrl()
      self.response.out.write('<p>Title: %s </p>' % entry.title.text)
      self.response.out.write("""<p><object width="425" height="355"><param name="movie" value="%s">
           </param><param name="wmode" value="transparent"></param>
           <embed src="%s" 
           type="application/x-shockwave-flash" wmode="transparent" 
           width="425" height="355"></embed></object></p>""" % (swf_url, swf_url))
      self.response.out.write('<p>Description: %s </p>' % entry.title.text)

    self.response.out.write('</body></html>')

    
def main():
  application = webapp.WSGIApplication(
                                       [('/', SearchPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()