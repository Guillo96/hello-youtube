import cgi
import wsgiref.handlers

import gdata.urlfetch
import gdata.service
import gdata.youtube
import gdata.youtube.service
import pprint

from google.appengine.ext import webapp
from google.appengine.ext import db

gdata.service.http_request_handler = gdata.urlfetch

class SearchPage(webapp.RequestHandler):
  
  def __init__(self):
    self.errors = {}
    self.form_code = """
      <div id="search_input">
      <span class="listing_title">Search YouTube</span><br />
      <form action="/" method="post">
        <table class="query_params" cellpadding="5" cellspacing="0" border="0">
          <tr>
            <td class="search_param"><strong>vq</strong></td>
            <td>Please enter a search term:<br/>
            <input type="text" name="content" size="60"/><br />
            <span class="note">YouTube will search all video metadata for 
            videos matching the term.<br />Video metadata includes titles, 
            keywords, descriptions, authors' usernames, and categories.</span>
            </td>
          </tr>
          <tr><td colspan="2"><hr class="slight"></td></tr>
          <tr>
            <td class="search_param"><strong>orderby</strong>
            <td>Pick the sort order of the results:<br />
              <select name="orderby">
                <option value="relevance" selected>relevance</option>
                <option value="published">published</option>
                <option value="viewCount">viewCount</option>
                <option value="rating">rating</option>
              </select>
            </td>
          </tr>
          <tr><td colspan="2"><hr class="slight"></td></tr>
          <tr>
              <td class="search_param"><strong>author</strong></td>
              <td>Optionally restrict your search to a specific author's videos:
              <br />
              <input type="text" name="author" size="60" value=""/></td>
            </tr>
            <tr><td colspan="2"><hr class="slight"></td></tr>
            <tr>
            <td class="search_param"><strong>format</strong></td>
            <td>Pick an output format that must be available:<br />
              <select name="format">
                <option value="1">1 (H.263 video for mobile)</option>
                <option value="5" selected>5 (flash video)</option>
                <option value="6">6 (MPEG-4 SP video for mobile)</option>
                </select>
                <br /><span class="note">Note that links to other formats will 
                also be shown but the query will not retrieve videos if the format 
                selected here is not found.</span>
              </td>
            </tr>
            <tr><td colspan="2"><hr class="slight"></td></tr>
            <tr>
              <td class="search_param"><strong>lr</strong></td>
              <td>Optionally restrict your keywords to a specific language:<br />
              <input type="text" name="lr" size="60" /><br />
              <span class="note">Valid values for this parameter are <a 
              href="http://www.loc.gov/standards/iso639-2/php/code_list.php" 
              target="_blank">ISO 639-1 two-letter language codes</a>.
              </td>
            </tr>
            <tr><td colspan="2"><hr class="slight"></td></tr>
            <tr>
            <td class="search_param"><strong>racy</strong></td>
            <td>Choose whether to include or exclude restricted content:<br />
              <select name="racy">
                <option value="exclude" selected>exclude</option>
                <option value="include">include</option>
                </select>
              </td>
            </tr>
            <tr><td colspan="2"><hr class="slight"></td></tr>
            <tr>
            <td class="search_param"><strong>restriction</strong></td>
              <td>Automatically filter out videos that are not playable from a 
              specific IP address. We recommend this is set to the current IP 
              address:<br >
              <input type="text" name="restriction" size="60" /><br />
              <span class="note">To request videos that are playable in a 
              specific country, include the restriction parameter in your request 
              and set the parameter value to the ISO 3166 two-letter country code 
              of the country where the videos will be played such as 'de' to show 
              only videos that are playable in Germany. You can also enter an IP 
              address of a machine located in the country that the video is to 
              be played.
              </span>
            </td>
            </tr>
            <tr><td colspan="2"><hr class="slight"></td></tr>
          </table>
        <input type="submit" value="Search YouTube">
      </form>
    </div>
    """
  
  def get(self):
    self.response.out.write("""
      <html><head><title>YouTube API - Searching for Videos</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        </head><body>%s
        </body>
      </html>""" % (self.form_code))
      
  def post(self):
    self.response.out.write("""<html><head><title>
        hello_youtube_search_query: Searching YouTube</title>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
        </head><body>""")
    
    search_term = cgi.escape(self.request.get('content')).encode('UTF-8')
    order_by = cgi.escape(self.request.get('orderby')).encode('UTF-8')
    author = cgi.escape(self.request.get('author')).encode('UTF-8')
    racy = cgi.escape(self.request.get('racy')).encode('UTF-8')
    format = cgi.escape(self.request.get('format')).encode('UTF-8')
    restriction = cgi.escape(self.request.get('restriction').lower()).encode('UTF-8')
    lr = cgi.escape(self.request.get('lr').lower()).encode('UTF-8')
    
    if len(search_term) < 1:
      self.errors['vq'] = 'You must enter a search term'
      self.response.out.write('<div id="errors"><span class="error_heading">Errors</span>:<br /><ul>')
      for item in self.errors.items():
        self.response.out.write('<li><strong>%s</strong> &mdash; %s</li>' % (item[0], item[1]))
      self.response.out.write('</ul></div>')
      self.response.out.write(self.form_code)
    else:
      self.response.out.write("""
        <div id="video_listing">
        <span class="listing_title">
        Searching for '%s'</span><br /><br />""" % search_term)

      client = gdata.youtube.service.YouTubeService()
      query = gdata.youtube.service.YouTubeVideoQuery()
      query.vq = search_term
      query.max_results = '5'
      query.racy = racy
      
      if len(lr) > 0:
        query.lr = lr
      query.format = format
      query.orderby = order_by
      
      if len(restriction) > 0:
        query.restriction = restriction
      if len(author) > 1:
        query.author = author
      
      feed = client.YouTubeQuery(query)

      self.response.out.write("""
          <table border="0" cellpadding="2" cellspacing="0"><tr>
            <td>
              <table class="query_params" border="0" cellpadding="2" 
              cellspacing="0">
                <tr>
                  <td colspan="2">
                    <strong>Query parameters sent:</strong></td></tr>""")

      for item in query.items():
        self.response.out.write("""<tr><td width="200">%s</td><td>%s</td></tr>
          <tr><td colspan="2"><hr class="slight"></td></tr>""" % (
          item[0], item[1]))
      
      self.response.out.write("""</table></td>
        <td class="code">
<pre><center>== code ==</center><br />
import gdata.youtube
import gdata.youtube.service

client = gdata.youtube.service.YouTubeService()
query = gdata.youtube.service.YouTubeVideoQuery()

query.vq = %s
query.max_results = '5'
query.racy = %s
query.format = %s
query.orderby = %s
""" % (search_term, racy, format, order_by))

      if len(lr):
        self.response.out.write('query.lr = %s' % lr)

      if len(restriction) > 0:
        self.response.out.write('query.restriction = %s' % restriction)

      if len(author) > 1:
        self.response.out.write('query.author = %s' % author)

      self.response.out.write("""
feed = client.YouTubeQuery(query)

for entry in feed.entry:
  print entry.title.text
  ...
</pre><br />
          <a href="/">Search again</a><br /><br /></td></tr>
          </table><br />
          Results:<br />
          <hr class="slight"><table border="0" cellpadding="2" 
          cellspacing="0">""")



      for entry in feed.entry:
        self.response.out.write('<tr><td class="thumbnail">')
        self.response.out.write(
            '<img src="%s" /><br /><br />' % entry.media.thumbnail[0].url)
        if entry.rating is not None:
          self.response.out.write(
              '<span class="video_rating">Rating: %s of 5 stars<br/>%s Votes '
              '<br /><br />Format: %s<br />' % (entry.rating.average, 
              entry.rating.num_raters, format))
        for item in entry.media.content:
          format_found = item.extension_attributes["{http://gdata.youtube.com/schemas/2007}format"]
          self.response.out.write("""
              <a target="_blank" href="%s">format %s link
              </a><br />""" % 
              (item.url, format_found))
        self.response.out.write('</td>')

        self.response.out.write('<td valign="top">')
        self.response.out.write(
            '<span class="video_title">%s</span><br />' % entry.title.text)
        self.response.out.write(
            '<span class="video_description">%s</span>'
            '<br /><br />' % entry.media.description)

        self.response.out.write(
            '<span class="video_category"><strong>%s</strong></span>' % 
            entry.media.category[0])
        self.response.out.write('<span class="video_published"> | published '
            'on %s</span><br />' % (entry.published.text.split('T')[0] + ' at ' +
            entry.published.text.split('T')[1][:5] + ' PST'))
        self.response.out.write('<span class="video_keywords"><strong>Keywords:'
            '</strong> %s </span><br />' % entry.media.keywords)
        self.response.out.write('<span class="video_keywords"><strong>Author:'
            '</strong> %s </span><br />' % entry.author[0].name)
        if entry.geo:
          self.response.out.write("""
              <span class="video_keywords"><strong>Geo Location:</strong> 
              %s </span><br />""" % entry.geo.Point.pos.text)

        self.response.out.write('</td></tr>')
        self.response.out.write(
            '<tr><td height="20" colspan="2"><hr class="slight"/></tr>')
      self.response.out.write("""
          </table><br />
          <a href="/">Search again</a><br /><br />
          </body></html>""")

    
def main():
  application = webapp.WSGIApplication(
                                       [('/', SearchPage)],
                                        debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
