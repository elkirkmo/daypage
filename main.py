import webapp2
from dp.handlers import *

app = webapp2.WSGIApplication([
        ('/jsonnewsection', JsonNewSection),
        ('/jsonupdatesection', JsonUpdateSection),        
        ('/', MainHandler)
], debug=True)
