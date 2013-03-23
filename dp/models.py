from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url

class Account(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    user = db.UserProperty()
    userid = db.StringProperty()
    federatedidentity = db.StringProperty()
    federatedprovider = db.StringProperty()
    notedays = db.StringListProperty()
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    email = db.StringProperty()
    sectionscreated = db.IntegerProperty(default = 0)
    sectionedits = db.IntegerProperty(default = 0)   
    sectionsdeleted = db.IntegerProperty(default = 0) 
    def fullname(self):
        if self.firstname != "":
            return self.firstname + " " + self.lastname
        else:
            return None
    def totalsections(self):
        return self.sectionscreated - self.sectionsdeleted

class Section(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    date = db.DateProperty(required = True)
    content = db.TextProperty()
    order = db.IntegerProperty()
    user = db.UserProperty()
    account = db.ReferenceProperty(Account)
    title = db.StringProperty()
    length = db.IntegerProperty()

    def initialorder(self):
        try: self.order = self.account.section_set.filter("date =", self.date).count() + 1
        except: self.order = 1

class SiteRecord(db.Model):
    sectionscreated = db.IntegerProperty(default = 0)
    sectionsdeleted = db.IntegerProperty(default = 0)
    sectionedits = db.IntegerProperty(default = 0)
    accounts = db.IntegerProperty(default = 0)
