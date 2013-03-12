import os, webapp2, json, datetime, random
from models import *
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db

providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id',
    'Yahoo'    : 'yahoo.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}
taglines = [
    'Blogs are big, Daypage is small.',
    'Web Journaling that doesn\'t hurt.',
    'Daypage is a day-centric note taking platform, as opposed to a note-centric day taking platform.',
    'Blogging without all the fuss.',
    'You deserve day tracking this simple.',
    'Blogging without the fluff, an actual web log.',
    'What a Star Captain would use.',
    'It\'s actually fun! - Conrad Frame',
    'Some things are horrible; Daypage is not one of those things.',
    ]

#render(self, 'account.html', values)
def render(self, t, values):
    if values["user"]:  # signed in already
        values["logout"] = users.create_logout_url('/')
    else:     # let user choose authenticator
        values["logins"] = []
        for name, uri in providers.items():
            url = users.create_login_url(dest_url='/home', federated_identity=uri)
            temp = {"name": name, "url": url }
            values["logins"].append(temp)
    try: values['referer'] = self.request.headers['Referer']
    except: values['referer'] = "/"
    if users.is_current_user_admin():
        values['admin'] = True
    values['tagline'] = random.choice(taglines)
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
        values = {
            "user": user,
            }
        render(self, "landing.html", values)

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.redirect("/")
        values = {
            "user": user,
            }
        render(self, "home.html", values)

class AjaxLoadSections(webapp2.RequestHandler):
    '''datestring, mm/dd/yyyy'''
    def post(self):
        user = users.get_current_user()
        month, day, year = self.request.get("datestring").split("/")
        thisday = datetime.date(int(year), int(month), int(day))
        sections = Section.all().filter("date =", thisday).filter("user =", user).order("order").run()
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
        record = SiteRecord.all().get()
        record.sectionscreated += 1
        record.put()
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
        record = SiteRecord.all().get()
        if newcontent == "":
            section.delete()
            response = 0
            record.sectionsdeleted += 1
        else:
            section.content = newcontent
            section.title = newcontent.split("\n")[0][:60]
            section.put()
            response = 1
            record.sectionedits += 1
        record.put()
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

class Maintain(webapp2.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return self.response.out.write("Sorry, not admin")
        self.response.out.write("Complete")
