import webapp2
from dp.handlers import *

app = webapp2.WSGIApplication([
        ('/jsonnewsection', JsonNewSection),
        ('/jsonupdatesection', JsonUpdateSection),
        ('/jsongetsections', JsonGetSections),
        ('/ajaxloadsections', AjaxLoadSections),
        ('/home', HomePage),
        ('/maintain', Maintain),
        ('/', MainHandler)
], debug=True)
