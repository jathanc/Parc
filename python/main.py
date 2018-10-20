import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.api import images
from models import User
from models import Interest
from models import Image
import os.path

jinja_current_directory = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)

# gets current logged-in user
# so it is easy to access their data on each new page
# request_handler is key for self, but since this method isn't in a class
# that makes it very hard to call self xD
def get_logged_in_user(request_handler):
    # gets current user via a method defined in google app engine
    user = users.get_current_user()

    # if this user doesn't exist (aka no one is signed into Google)
    if not user:
        # send them to Google log-in url
        dict = {
            'log_in_url' : users.create_login_url('/')
        }
        # put that Google log-in link on the page and get them in!
        log_in_template = jinja_current_directory.get_template('templates/login-page.html')
        request_handler.response.write(log_in_template.render(dict))
        print 'transaction halted because user is not logged in'
        return None

    # at this point, the user is logged into google
    # now let's make sure that user has been logged into our site
    # aka do we have their Google ID in OUR model (which is called User)?
    # user (appengine) vs User (our own Model). Definitely not confusing
    existing_user = User.get_by_id(user.user_id())

    # if this person is not a user in our database, throw an error
    if not existing_user:
        print 'transaction halted because user not in database'
        request_handler.error(500)
        return None

    # otherwise if they exist in both Google and our site, let's return them
    # now we can easily access their information
    return existing_user

class StartPage(webapp2.RequestHandler):
    def get(self):
        start_template = \
                jinja_current_directory.get_template('templates/welcome.html')
        self.response.write(start_template.render())

class LoginPage(webapp2.RequestHandler):
    def get(self):
        login_template = \
                jinja_current_directory.get_template('templates/login-page.html')
        home_template = jinja_current_directory.get_template('templates/home-page.html')
        login_dict = {}
        name = ""
        user = users.get_current_user()

        # if the user is logged with Google
        if user:
            # magical users method from app engine xD
            email_address = user.nickname()
            # uses User (model obj) method to get the user's Google ID.
            # hopefully it returns something...
            our_site_user = User.get_by_id(user.user_id())
            #dictionary - this gives the sign-out link
            signout_link_html = '<a href="%s">sign out</a>' % (users.create_logout_url('/'))
            signout_link = users.create_logout_url('/')

            # if the user is logged in to both Google and us
            if our_site_user:
                sign_out_dict = {'logout_link' : signout_link, 'name' : our_site_user.name, 'email_address' : email_address}
                # self.response.write(home_template.render(sign_out_dict))
                # this redirect should be better than rendering the page
                self.redirect('/home')

            # If the user is logged into Google but never been to us before..
            # if we want to fix OUR login page, this is where
            else:
                # self.response.write('''
                #  Welcome to our site, %s!  Please sign up! <br>
                #  <form method="post" action="/login">
                #  <input type="text" name="first_name">
                #  <input type="text" name="last_name">
                #  <input type="submit">
                #  </form><br> %s <br>
                #  ''' % (email_address, signout_link_html))
                self.response.write(login_template.render())

        # Otherwise, the user isn't logged in to Google or us!
        else:
            self.redirect(users.create_login_url('/login'))
            # self.response.write('''Please log in to Google to use our site! <br><a href="%s">Sign in</a>''' % (users.create_login_url('/login')))

    def post(self):
        user = users.get_current_user()
        if not user:
            # You shouldn't be able to get here without being logged in to Google
            self.error(404)
            return
        our_user = User(
            email=user.nickname(),     # current user's email
            id=user.user_id(),         # current user's ID number
            name=self.request.get("first_name") + " " + self.request.get("last_name")
            )
        our_user.put()
        wel_dict = {'welcome': 'Thanks for signing up, %s!' %
            our_user.name}

        home_template = jinja_current_directory.get_template('templates/home-page.html')
        self.response.write(home_template.render(wel_dict))

            # need to figure out how we're doing interests
            # do they already exist? How do I get those interest objects made
            # before I put them into the our_user object like this??
            # interests=self.request.get('interests'),
            # university=self.request.get('university'),


app = webapp2.WSGIApplication([
    ('/', StartPage),
    ('/home', HomePage),
    ('/login', LoginPage),
    ('/info_update', InfoUpdatePage),
    ('/people', PeoplePage),
    ('/img', ImagePage)
], debug=True)
