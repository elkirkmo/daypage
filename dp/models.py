from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url

class Account(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    user = db.UserProperty()
    userid = db.StringProperty()
    notedays = db.StringListProperty()
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    email = db.StringProperty()
    sectionscreated = db.IntegerProperty(default = 0)
    sectionedits = db.IntegerProperty(default = 0)   
    sectionsdeleted = db.IntegerProperty(default = 0) 
    def fullname(self):
        return self.firstname + " " + self.lastname

class Section(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    date = db.DateProperty(required = True)
    content = db.TextProperty()
    order = db.IntegerProperty()
    user = db.UserProperty()
    account = db.ReferenceProperty(Account)
    title = db.StringProperty()

    def initialorder(self):
        self.order = Section.all().filter("date =", self.date).count() + 1

class SiteRecord(db.Model):
    sectionscreated = db.IntegerProperty(default = 0)
    sectionsdeleted = db.IntegerProperty(default = 0)
    sectionedits = db.IntegerProperty(default = 0)
    accounts = db.IntegerProperty(default = 0)
