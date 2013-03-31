import webapp2
from dp.handlers import *

app = webapp2.WSGIApplication([
        ('/jsonnewsection', JsonNewSection),
        ('/jsonupdatesection', JsonUpdateSection),
        ('/jsongetsections', JsonGetSections),
        ('/ajaxloadsections', AjaxLoadSections),
        ('/ajaxloadpublicsections', AjaxLoadPublicSections),        
        ('/home', HomePage),
        ('/settings', SettingsPage),
        ('/logincheck', LoginCheck),
        ('/maintain', Maintain),
        ('/d/(.*)/(.*)', UserPage),
        ('/d/(.*)', UserPage), 
        ('/d', UserPage),
        ('/', MainHandler),
        ('.*', MainHandler),
], debug=True)
