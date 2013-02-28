import webapp2
from dp.handlers import *

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
