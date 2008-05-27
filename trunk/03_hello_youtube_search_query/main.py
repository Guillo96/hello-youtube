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
    
    query.vq = 'bicycle dalmation'
    query.orderby = 'viewCount'
    query.max_results = '5'

    feed = client.YouTubeQuery(query)

    self.response.out.write("""<html><head><title>
        hello_youtube_search_query: Searching YouTube</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        </head><body><div id="video_listing">""")
    
    self.response.out.write('<span class="listing_title">Searching for "' +
        query.vq + 
        '"</span><br /><br />')

    self.response.out.write('<table border="0" cellpadding="2" '
        'cellspacing="0">')
    
    for entry in feed.entry:
      self.response.out.write('<tr><td class="thumbnail">')
      self.response.out.write(
          '<img src="%s" /><br /><br />' % entry.media.thumbnail[0].url)
      self.response.out.write(
          '<span class="video_rating">Rating: %s of 5 stars<br/>%s Votes '
          '</span>' % (entry.rating.average, entry.rating.num_raters))
      self.response.out.write('</td>')

      self.response.out.write('<td valign="top">')
      self.response.out.write(
          '<span class="video_title">%s</span><br />' % entry.title.text)
      self.response.out.write(
          '<span class="video_description">%s</span>'
          '<br /><br />' % entry.media.description)

    # uncomment this section to show the embeddable player
    # if entry.GetSwfUrl():
    #   self.response.out.write('<object width="425" height="350">'
    #      '<param name="movie" value="' + entry.GetSwfUrl() + '"></param>'
    #       '<embed src="' + entry.GetSwfUrl() + 
    #       '" type="application/x-shockwave-flash" '
    #       'width="425" height="350"></embed></object>')

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
    self.response.out.write('</table></div>')
    self.response.out.write('</body></html>')
def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
