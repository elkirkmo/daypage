import os, webapp2, json, datetime
from models import *
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db

providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id',
    'Yahoo'    : 'yahoo.com',
    'MySpace'  : 'myspace.com',
    'AOL'      : 'aol.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}

#render(self, 'account.html', values)
def render(self, t, values):
    if values["user"]:  # signed in already
        values["logout"] = users.create_logout_url(self.request.uri)
    else:     # let user choose authenticator
        values["logins"] = []
        for name, uri in providers.items():
            url = users.create_login_url(federated_identity=uri)
            temp = {"name": name, "url": url }
            values["logins"].append(temp)
    try: values['referer'] = self.request.headers['Referer']
    except: values['referer'] = "/"
    if users.is_current_user_admin():
        values['admin'] = True
    templatefile = '_templates/' + t
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), templatefile)
    self.response.out.write(template.render(path, values))

def renderjson(self, values):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(values))

######################## HANDLERS

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = "home.html"
        else:
            template = "landing.html"
        values = {
            "user": user,
            }
        render(self, template, values)

class AjaxLoadSections(webapp2.RequestHandler):
    '''datestring, mm/dd/yyyy'''
    def post(self):
        user = users.get_current_user()
        month, day, year = self.request.get("datestring").split("/")
        thisday = datetime.date(int(year), int(month), int(day))
        sections = Section.all().filter("date =", thisday).order("order").run()
        values = {
            "response": 1,
            "sections": sections,
            "user": user,
            }
        render(self, "_loadsections.html", values)

class JsonNewSection(webapp2.RequestHandler):
    ''' content, year, month, day '''
    def post(self):
        user = users.get_current_user()
        content = self.request.get("content")
        if content == "":
            return renderjson(self, {"response": 2})
        year = int(self.request.get("year"))
        month = int(self.request.get("month"))
        day = int(self.request.get("day"))
        section = Section(
            date = datetime.date(year, month, day),
            content = self.request.get("content"),
            user = user
            )
        section.initialorder()
        section.put()
        values = {
            "response": 1,
            "sectionid": section.key().id()
            }
        renderjson(self, values)

class JsonUpdateSection(webapp2.RequestHandler):
    ''' sectionid, content, user '''
    def post(self):
        user = users.get_current_user()
        section = Section.get_by_id(int(self.request.get("sectionid")))
        newcontent = self.request.get("content")
        if newcontent == "":
            section.delete()
            response = 0
        else:
            section.content = newcontent
            section.put()
            response = 1
        values = {
            "response": response,
            }
        renderjson(self, values)

class JsonGetSections(webapp2.RequestHandler):
    '''year, month, day'''
    def post(self):
        user = users.get_current_user()
        year = int(self.request.get("year"))
        month = int(self.request.get("month"))
        day = int(self.request.get("day"))
        thisday = datetime.date(year, month, day),
        sections = Section.all().filter("user =", user).filter("date =", thisday).run()
        values = {
            "response": 1,
            "sections": sections
            }
        renderjson(self, values)
