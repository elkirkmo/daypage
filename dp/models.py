from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url

class Account(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    user = db.UserProperty()
    

class Section(db.Model):
    date_created = db.DateTimeProperty(auto_now_add = True)
    date_edited = db.DateTimeProperty(auto_now = True)
    date = db.DateProperty(required = True)
    text = db.TextProperty()
    order = db.IntegerProperty()

    def initialorder(self):
        self.order = Section.all().filter("date =", self.date).count() + 1
