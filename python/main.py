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
                jinja_current_directory.get_template('templates/start-page.html')
        self.response.write(start_template.render())

class HomePage(webapp2.RequestHandler):
    def get(self):
        home_template = \
                jinja_current_directory.get_template('templates/home-page.html')
        log_out_dict = {'logout_link' : users.create_logout_url('/')}
        self.response.write(home_template.render(log_out_dict))

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

class InfoUpdatePage(webapp2.RequestHandler):
    def get(self):
        form_template = \
            jinja_current_directory.get_template('templates/form-and-profile-page.html')
        info_update_page_dict = {'logout_link' : users.create_logout_url('/')}
        current_user = get_logged_in_user(self)
        if current_user.image_model and current_user.image_model.id():
            img_id = current_user.image_model
            img_id = img_id.id()
            info_update_page_dict['image_profile'] = "/img?id=" + str(img_id)
        self.response.write(form_template.render(info_update_page_dict))

        # this places a form in a space for the user to upload an image
    def submit_form(request):
        if request.method == 'POST':
            form = Form(request.POST)
            if not form.has_changed():
                self.response.write("Please fill out all fields before submitting.")
                # Generate Error
    def post(self):
        # get the user info from their form
        uni_in_form = self.request.get("schools")
        age_in_form = self.request.get("ages")
        major_in_form = self.request.get("majors")
        insta = self.request.get("social_media")
        handle = str(insta).replace("@",'')
        social_media_in_form = "https://www.instagram.com/" + handle + "/"

        # this gets me an array of strings, where each string is a value
        interest_in_form_array = self.request.get("interests", allow_multiple=True)

        # image is caught
        # image_in_form = self.request.get("image")
        # print "\n\n\n\n\n\n\n\n"
        # print image_in_form
        # print "\n\n\n\n\n\n\n\n"
        # self.response.out.write('<div><img src="/img?img_id=%s"></img>' %
            # user.key.urlsafe())
        # image_in_form = images.resize(image_in_form, 32, 32)
        # image is saved to a specific file (aka /images)

        # convert the string array into an array of Interest Objects
        array_of_interest_objs = []
        for interest in interest_in_form_array:
            this_interest = Interest(name=interest)
            array_of_interest_objs.append(this_interest)
            this_interest.put()

        # our_user is the existing_user
        our_user = get_logged_in_user(self)

        # give our_user values in the data store
        our_user.university = uni_in_form
        our_user.age = age_in_form
        our_user.major = major_in_form
        our_user.social_media = social_media_in_form
        our_user.interests = array_of_interest_objs
        # our_user.image = image_in_form

        # save those changes to our_user values
        our_user.put()

        log_out_dict = {'logout_link' : users.create_logout_url('/')}

        self.redirect('/people')


class PeoplePage(webapp2.RequestHandler):
    def get(self):
        current_user = get_logged_in_user(self)
        people_temp_dict = {}
        people_template = jinja_current_directory.get_template('templates/people-page.html')
        if not current_user.university:
            people_temp_dict = {'Error' : "Oops - please fill out profile form first to find your matches!", "logout_link": users.create_logout_url('/')}
            self.response.write(people_template.render(people_temp_dict))
            return None

        # get list of all university matches
        uni_matches = User.query(User.university == current_user.university,
                            User.email != current_user.email).fetch()
        interest_matches = []
        no_interest_matches = []

        # here's where I sort the uni matches
        for other_user in uni_matches:
            similarity_index = current_user.compare_interests(other_user)
            other_user_dict = other_user.to_dict()
            # check to make sure other_user.image_model exist
            if(other_user.image_model):
                other_user_dict['image_url'] = "/img?id=" + str(other_user.image_model.id())
            else:
                other_user_dict['image_url'] = "../images/Missing_avatar.svg.png"
            if(similarity_index >= 3):
                interest_matches.insert(0, other_user_dict)
            elif similarity_index == 2:
                interest_matches.insert(int(len(interest_matches)/2), other_user_dict)
            elif similarity_index == 1:
                interest_matches.append(other_user_dict)
            elif similarity_index == 0:
                no_interest_matches.append(other_user_dict)

        # If the array is too short, add the rest of the uni matches
        if len(interest_matches) < 20:
            interest_matches.extend(no_interest_matches)

        # now it's time to trim it so there's a max 20 recommended users
        # cut it off - because the best ones will be in the front!
        interest_matches = interest_matches[:20]
        match_dict = {'matches': interest_matches, 'logout_link' : users.create_logout_url('/')}
        # render matches into the html (or it should anyway)
        self.response.write(people_template.render(match_dict))

# gets image data from post and stores it to the datastore
class ImagePage(webapp2.RequestHandler):
    def get(self):
        img_id = self.request.get('id')

        if not img_id:
            return self.error(400)
        img_item = Image.get_by_id(long(img_id))

        if not img_item:
            return self.error(404)
        img_in_binary = images.Image(img_item.image)
        img_in_binary.resize(200, 200)
        some_img = img_in_binary.execute_transforms(output_encoding=images.JPEG)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(some_img)

        # send it back to the page!
        # OMG if this works I can use it in my peoples page too!?!
        # like, I could send the image in binary over? Or I could have each user call this method?
        # they each have their own image IDs
        # and then that ID can be used to build like a dictionary? (Or will that mess it up)
    def post(self):
        avatar = self.request.get('image')

        avatar = images.resize(avatar, 500, 500)
        current_user = get_logged_in_user(self)

        this_image = Image(image=avatar)
        img_id = this_image.put()
        current_user.image_model = img_id
        current_user.put()
        self.redirect('/info_update')

app = webapp2.WSGIApplication([
    ('/', StartPage),
    ('/home', HomePage),
    ('/login', LoginPage),
    ('/info_update', InfoUpdatePage),
    ('/people', PeoplePage),
    ('/img', ImagePage)
], debug=True)
