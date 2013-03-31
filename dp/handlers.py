import os, webapp2, json, datetime, random, urllib, hashlib
from models import *
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db

providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id',
    'MyOpenID' : 'myopenid.com'
    #    'Yahoo'    : 'yahoo.com',
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
        values["avatarhash"] = hashlib.md5(values["account"].email.lower()).hexdigest()
    else:     # let user choose authenticator
        values["logins"] = []
        for name, uri in providers.items():
            url = users.create_login_url(dest_url='/logincheck', federated_identity=uri)
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
        account = Account.all().filter("user =", user).get()
        values = {
            "user": user,
            "account": account,
            }
        render(self, "landing.html", values)

class LoginCheck(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.redirect("/")
        account = Account.all().filter("user =", user).get()
        if not account:
            account = Account(
                user = user,                
                userid = user.user_id(),
                federatedidentity = user.federated_identity(),
                provider = user.federated_provider(),
                email = "",
                firstname = "",
                lastname = "",
                sectionscreated = 0,
                sectionedits = 0,
                sectionsdeleted = 0,
                )
            account.put()
            record = SiteRecord.all().get()
            if record.accounts:
                record.accounts += 1
                record.put()
            else:
                record.accounts = 1
                record.put()
            #check if there was data for user, add to account:
            sections = Section.all().filter("user =", user).run()
            if sections:
                for section in sections:
                    #add to account, increase account.sectionscreated
                    section.account = account
                    section.put()
                    account.sectionscreated += 1
                account.put()
        self.redirect("/home")

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        if not user:
            return self.redirect("/")
        values = {
            "user": user,
            "account": account,
            }
        render(self, "home.html", values)

class UserPage(webapp2.RequestHandler):
    '''useridentifier is either userid or username'''
    '''datestring, yyyymmdd'''
    def get(self, useridentifier = None, datestring = None):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()        
        onaccount = None
        sections = None
        if not useridentifier and not datestring:
            template = "nouser.html"
        if useridentifier != None:
            template = "userhome.html"
            try:
                int(useridentifier)
                accountid = True
            except:
                accountid = False
            if accountid:
                onaccount = Account.get_by_id(int(useridentifier))
            else:
                onaccount = Account.all().filter("username =", useridentifier).get()
            if datestring:
                template = "userday.html"
                thisday = datetime.date(int(datestring[0:4]), int(datestring[4:6]), int(datestring[6:8]))                
                sections = Section.all().filter("date =", thisday).filter("account =", account).run()
        values = {
            "user": user,
            "account": account,
            "onaccount": onaccount,
            "sections": sections,
            }
        render(self, template, values)

class SettingsPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        if not user:
            return self.redirect("/")
        values = {
            "user": user,
            "account": account,
            "alertmessage": self.request.get("alertmessage"),
            }
        render(self, "settings.html", values)
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        username = self.request.get("username")
        firstname = self.request.get("firstname")
        lastname = self.request.get("lastname")
        email = self.request.get("email")
        if account:
            if firstname != "":
                account.firstname = firstname
            if lastname != "":
                account.lastname = lastname
            if email != "":
                account.email = email
            if username != "":
                if not username.replace(".", "").isalpha() or " " in username:
                    return self.redirect("/settings?alertmessage=Sorry only letters and periods are allow in usernames")
                if username != account.username:
                    #check for duplicate
                    checkusername = Account.all().filter("username =", username).get()
                    if checkusername:
                        #redirect with an alertmessage
                        return self.redirect("/settings?alertmessage=Username " + username + " is already in use.")
                    else:
                        account.username = username
            else:
                if account.username != "":
                    return self.redirect("/settings?alertmessage=You shall not remove your username.")
            account.put()
        self.redirect("/settings")

class AjaxLoadSections(webapp2.RequestHandler):
    '''datestring, mm/dd/yyyy'''
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        month, day, year = self.request.get("datestring").split("/")
        thisday = datetime.date(int(year), int(month), int(day))
        sections = Section.all().filter("date =", thisday).filter("account =", account).run()
        values = {
            "response": 1,
            "sections": sections,
            "user": user,
            "account": account,
            }
        render(self, "_loadsections.html", values)

class JsonNewSection(webapp2.RequestHandler):
    ''' content, year, month, day '''
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        content = self.request.get("content")
        if content == "":
            return renderjson(self, {"response": 0})
        year = int(self.request.get("year"))
        month = int(self.request.get("month"))
        day = int(self.request.get("day"))
        section = Section(
            date = datetime.date(year, month, day),
            content = self.request.get("content"),
            user = user,
            account = account,
            length = len(self.request.get("content")),
            title = self.request.get("content").split("\n")[0][:60],
            )
        section.initialorder()
        section.put()
        record = SiteRecord.all().get()
        record.sectionscreated += 1    
        record.put()
        account.sectionscreated += 1
        account.put()
        values = {
            "response": 1,
            "sectionid": section.key().id(),
            "accountid": account.key().id(),
            }
        renderjson(self, values)

class JsonUpdateSection(webapp2.RequestHandler):
    ''' sectionid, content, user '''
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        section = Section.get_by_id(int(self.request.get("sectionid")))
        newcontent = self.request.get("content")
        record = SiteRecord.all().get()
        if newcontent == "":      #everything is deleted!
            section.delete()
            response = 0
            record.sectionsdeleted += 1
            account.sectionsdeleted += 1
        else:                     #new stuff, save the change
            section.content = newcontent
            section.title = newcontent.split("\n")[0][:60]
            section.account = account
            section.length = len(newcontent)
            section.put()
            response = 1
            record.sectionedits += 1
            account.sectionedits += 1
        account.put()
        record.put()
        values = {
            "response": response,
            "accountid": account.key().id(),
            }
        renderjson(self, values)

class JsonGetSections(webapp2.RequestHandler):
    '''year, month, day'''
    def post(self):
        user = users.get_current_user()
        account = Account.all().filter("user =", user).get()
        year = int(self.request.get("year"))
        month = int(self.request.get("month"))
        day = int(self.request.get("day"))
        thisday = datetime.date(year, month, day),
        sections = Section.all().filter("user =", user).filter("date =", thisday).run()
        values = {
            "response": 1,
            "sections": sections,
            "accountid": account.key().id(),
            }
        renderjson(self, values)

class Maintain(webapp2.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return self.response.out.write("Sorry, not admin")
        sections = Section.all().run()
        for i in sections:
            i.length = len(i.content)
            i.put()
        self.response.out.write("Complete")
