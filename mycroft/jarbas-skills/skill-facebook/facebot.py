import fb
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary



class FaceBot():
    def __init__(self, token):
        self.token = token
        self.facebook = fb.graph.api(self.token)
        self.id = self.get_self_id()

    def get_self_id(self):
        print self.get_field("id", "me")
        return self.get_field("id", "me")["id"]

    def get_friends(self, id="me"):
        return self.facebook.get_object(cat='single', id=id, fields=['friends'])

    def get_field(self, field, id = "me"):
        return self.facebook.get_object(cat='single', id=id, fields=[field])

    def get_friend_num(self, id="me"):
        friends = self.facebook.get_object(cat='single', id=id, fields=['friends'])
        try:
            friends = friends["friends"]["summary"]["total_count"]
            print "number of friends: " + str(friends)
        except:
            pass
            #print "you dont have acess to this users friends"
        return friends

    def post_to_wall(self, text="My facebook status", id="me", link=None):
        self.facebook.publish(cat="feed", id=id, message=text, link=link)

    def comment_object(self, object_id, comment="My comment"):
        return self.facebook.publish(cat="comments", id=object_id, message=comment, object="page_internal")

    def create_album(self, name="Album Name", message="Album Details", id="me"):
        return self.facebook.publish(cat="albums", id=id, name=name, message=message)

    def delete_status(self, status_id):
        self.facebook.delete(id=status_id)

    def delete_comment(self, comment_id):
        self.facebook.delete(id=comment_id)

    def clean_profile(self, profile):

        try:
            profile["age_range"] = profile["age_range"]["min"]
        except:
            pass

        try:
            l = []
            for language in profile["languages"]:
                l.append(language["name"])
            profile["languages"] = l
        except:
            pass

        try:
            profile["friends"] = profile["friends"]["summary"]["total_count"]
        except:
            pass

        try:
            ed = []
            for e in profile["education"]:
                d = {}
                d.setdefault("name", e["school"]["name"])
                d.setdefault("type", e["type"])
                ed.append(d)
            profile["education"] = ed
        except:
            pass

        try:
            work = []
            for w in profile["work"]:
                wr = {}
                wr.setdefault("name", w["position"]["name"])
                wr.setdefault("start_date", w["start_date"])
                wr.setdefault("end_date", w["end_date"])
                wr.setdefault("employer", w["employer"]["name"])
                work.append(wr)
            profile["work"] = work
        except:
            pass

        try:
            profile["feed"] = profile["feed"]["data"]
        except:
            pass

        try:
            profile["likes"] = profile["likes"]["data"]
        except:
            pass

        try:
            profile["albums"] = profile["albums"]["data"]
        except:
            pass

        try:
            profile["picture"] = profile["picture"]["data"]["url"]
        except:
            pass

        return profile

    def get_profile(self, id="me"):

        try:
            print self.facebook.get_object(cat='single', id=id, fields=[])["error"]["message"]
            return {}
        except:
            pass

        profile = {}
        keys = ["birthday", "about", "age_range", "education", "devices", "email", "first_name", "gender", "hometown",
                  "inspirational_people", "interested_in", "location", "languages", "last_name", "political",
                  "public_key", "quotes", "religion", "relationship_status", "significant_other", "work", "albums",
                  "friends", "family", "feed", "likes", "picture", "cover"]

        for key in keys:
            try:
                field = self.get_field(key, id)
                profile.setdefault(key, field[key])
            except:
                profile.setdefault(key)

        return self.clean_profile(profile)

    def get_wall_post_ids(self, id="me"):
        # return id of wall_posts
        # return "events" from wall
        e = []
        try:
            p = self.get_field("feed", id)["feed"]["data"]
        except: #no acess
            return e
        for i in p:
            try:
                e.append(i["id"])
            except:
                pass
        return e

    def get_wall_posts(self, id="me"):
        # return "events" from wall
        p = self.get_field("feed", id)
        e = []
        try:
            p = p["feed"]["data"]
        except:
            # no acess to this users
            return e

        for i in p:
            try:
                l = {}
                l.setdefault("message", i["message"])
                l.setdefault("created_time", i["created_time"])
                l.setdefault("id", i["id"])
                e.append(l)
            except:
                pass
        return e

    def get_wall_events(self, id="me"):
        # return "events" from wall
        e = []
        try:
            p = self.get_field("feed", id)["feed"]["data"]
        except:
            return e
        for i in p:
            try:
                l = {}
                l.setdefault("story", i["story"])
                l.setdefault("created_time", i["created_time"])
                l.setdefault("id", i["id"])
                e.append(l)
            except:
                pass
        return e

    def get_wall_comments(self, id="me"):
        ids = self.get_wall_post_ids(id)
        comments = {}
        for i in ids:
            comme = self.get_field("comments", i)
            try:
                comments.setdefault(i, comme["comments"]["data"])
            except:
                # " no comments"
                pass
        cleaned = []
        for wall_post_id in comments:
            com = {}
            com.setdefault("wall_post_id", wall_post_id)
            for comment in comments[wall_post_id]:
                com.setdefault("comment_id", comment["id"])
                com.setdefault("comment", comment["message"].encode("utf8"))
                com.setdefault("sender", comment["from"]["name"].encode("utf8"))
                com.setdefault("sender_id", comment["from"]["id"])
                com.setdefault("date", comment["created_time"])
                cleaned.append(com)
        return cleaned

    def get_detailed_like_info(self, id="me"):
        lik = []
        try:
            likes = self.get_field("likes", id)["likes"]["data"]
        except: #no acess
            return lik

        for like in likes:
            l = {}
            l.setdefault("name", like["name"])
            p = self.get_profile(like["id"])
            for key in p:
                l.setdefault(key, p[key])
            lik.append(l)
        return lik

    def get_albums(self, id="me"):
        try:
            print self.facebook.get_object(cat='single', id=id, fields=[])["error"]["message"]
            return []
        except:
            pass

        al = []
        try:
            albums = self.get_field("albums", id)["albums"]["data"]
        except:# no acess
            return al

        for f in albums:
            a = {}
            a.setdefault("name", f["name"])
            a.setdefault("id", f["id"])
            a.setdefault("created_time", f["created_time"])
            photos = self.get_field("photos", f["id"])["photos"]["data"]
            a.setdefault("photos", photos)
            try:
                likes = self.get_field("likes", f["id"])["likes"]["data"]
                a.setdefault("likes", likes)
            except:
                a.setdefault("likes")
            al.append(a)
        return al

    def get_people_who_liked(self, id="me"):
        people = {}
        # get people who liked feed posts
        posts = self.get_wall_post_ids(id)
        for p in posts:
            try:
                likes = self.get_field("likes", p)["likes"]["data"]
                for like in likes:
                    people.setdefault(like["name"], like["id"])
            except:
                pass #no likes

        # get people who liked albums
        albums = self.get_albums(id)
        for a in albums:
            try:
                likes = a["likes"]
                for like in likes:
                    people.setdefault(like["name"], like["id"])
            except:
                pass  # no likes
        # get people who commented
        comments = self.get_wall_comments(id)
        for c in comments:
            people.setdefault(c["sender"], c["sender_id"])
        return people

    def commented_on(self, id="me"):
        answered = False
        replys = self.get_field("comments", id)
        replys = replys["comments"]["data"]
        for reply in replys:
            if reply["from"]["id"] == self.id:
                answered = True
        return answered

    def like(self, id):
        # TODO fix some other way
        liked = self.facebook.publish(cat="likes", id=id)
        try:
            print liked["error"]["message"]
        except:
            print liked

    def answer_comments_from(self, from_id="me", where_id="me", text=":)"):
        # TODO answer posts in wall
        # answer replys to posts in wall
        comments = self.get_wall_comments(where_id)
        for comment in comments:
            if comment["sender_id"] == from_id:
                answered = self.commented_on(comment["comment_id"])
                if not answered:
                    self.comment_object(comment["comment_id"], text)

    def delete(self, id):
        # TODO fix permissions
        return self.facebook.delete(id=id)

    def create_event(self):
        # TODO change, deprecated
        return self.facebook.publish(cat="events", id="me", name="Become self aware", start_time="2018-10-16-12:20",
                         end_time="2018-10-18-14:30")


class SeleniumFaceBot():
    def __init__(self, mail, passwd):
        self.mail = mail
        self.passwd = passwd

    def like_photos(self,number):
        c = 0
        while c <=number:
            self.driver.get('https://m.facebook.com/friends/center/friends/?mff_nav=1')
            print "Opened facebook...\n Selecting friend"
            #
            i=5
            num = random.choice(range(1,10)) #ranodm friend#will fail if not enough friends
            while i<=random.choice(range(1,10)): #random page max 5
                try:
                    sleep(5)#should avoid staelementexeption
                    a = self.driver.find_element_by_xpath(".//*[@id='u_0_0']/a/span") #click more friends
                    a.click() #StaleElementReferenceException: Message: The element reference is stale. Either the element is no longer attached to the DOM or the page has been refreshed.
                except:
                    pass #if theres no "more friends to click" who cares....
                i+=1
            sleep(3)
            #click friend name
            print "opening friend page"
            a = self.driver.find_element_by_xpath(".//*[@id='friends_center_main']/div[2]/div["+str(num)+"]/table/tbody/tr/td[2]/a")
            a.click()
            sleep(15)
            #view profile
            print "clicking view profile"
            a = self.driver.find_element_by_xpath(".//*[@id='root']/table/tbody/tr/td/div/div[3]/a")
            a.click()
            sleep(15)
            # click photo
            i =1
            print ' clicking photos'
            a = self.driver.find_element_by_xpath(".//*[@id='m-timeline-cover-section']/div[4]/a[3]")
            a.click()
            sleep(5)
            print ' clicking uploads' #
            try:
                try:
                    a = self.driver.find_element_by_xpath(".//*[@id='root']/div[2]/div[2]/div[1]/table/tbody/tr/td[1]/a")
                    a.click()
                except:
                    a = self.driver.find_element_by_xpath(".//*[@id='root']/div[2]/div[1]/div[1]/table/tbody/tr/td[1]/a")
                    a.click()
                sleep(5)
            except:
                print ' clicking 1st photo'
                a = self.driver.find_element_by_xpath(".//*[@id='root']/table/tbody/tr/td/div/a[1]")
                a.click()
                sleep(5)
            # click like
            print 'clicking like'
            liked = False
            c1 = 0
            while not liked:
                a = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/div/div[2]/div/table/tbody/tr/td[1]/a")#like button
                a.click()
                sleep(5)
                url2 = self.driver.current_url
                if "https://m.facebook.com/reactions" in url2: #already liked opened reaction page
                    #liked=False
                    self.driver.back()#go back
                    sleep(2)
                    print "already liked, ciking next picture"
                    if c1<=5:#dont go back more than 5 photos thats weird
                        a = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/div/div[1]/div[2]/table/tbody/tr/td[2]/a")#next button
                        a.click()
                        sleep(2)
                        c1 += 1
                    else:
                        liked = True #abort
                else:
                    liked = True
            sleep(0.5)
            c += 1

    def login(self):
        #start firefox

        binary = FirefoxBinary('/usr/lib/firefox-esr/firefox-esr')
        capabilities = webdriver.DesiredCapabilities().FIREFOX
        capabilities["marionette"] = False
        self.driver = webdriver.Firefox(firefox_binary=binary)
        #self.driver = webdriver.Firefox()
        sleep(5)
        #go to fb oage and login
        #normal versionn
       # self.driver.get("http://www.facebook.org")
       # elem = self.driver.find_element_by_id("email")
       # elem.send_keys(self.mail)
       # elem = self.driver.find_element_by_id("pass")
       # elem.send_keys(self.passwd)
       # elem.send_keys(Keys.RETURN)
       # self.driver.implicitly_wait(5)
        #mobile version

        self.driver.get('https://m.facebook.com/')
        print "Opened facebook..."
        sleep(1)  # random erros dpeending on connection
        a = self.driver.find_element_by_xpath(".//*[@id='login_form']/ul/li[1]/input")
        a.send_keys(self.mail)
        sleep(1)  # random erros dpeending on connection
        print "Email Id entered..."
        b = self.driver.find_element_by_xpath(".//*[@id='login_form']/ul/li[2]/div/input")
        b.send_keys(self.passwd)
        sleep(1)  # random erros dpeending on connection
        print "Password entered..."
        c = self.driver.find_element_by_xpath(".//*[@id='login_form']/ul/li[3]/input")
        c.click()
        sleep(10)  # it sometimes opens next site without having logged in

    def close(self):
        self.driver.close()

    def post_wall(self, message):
        ######normal#####
        # add code here
        ######mobile#####
        self.driver.get("https://m.facebook.com/me")  # profile page
        # post_box = driver.find_element_by_class_name('_5rpu')
        post_box = self.driver.find_element_by_xpath(".// *[ @ id = 'u_0_0']")
        post_box.click()
        post_box.send_keys(message)
        sleep(5)
        # post_it = driver.find_element_by_class_name('_1mf7')
        post_it = self.driver.find_element_by_xpath(
            ".//*[@id='timelineBody']/div[1]/div[1]/form/table/tbody/tr/td[2]/div/input")
        post_it.click()
        print "Posted..."

    def add_suggested_friends(self, num):
        i = 0
        while i <= num:
            self.driver.get("https://m.facebook.com/friends/center/mbasic/")  # people you may now page
            sleep(2)  # random erros dpeending on connection
            add = self.driver.find_element_by_xpath(
                ".//*[@id='friends_center_main']/div[2]/div[1]/table/tbody/tr/td[2]/div[2]/a[1]")
            add.click()
            print "friend added"
            sleep(10)  # just in case facebook bans me or something for too fast clicking
            i += 1

    def build_about_me(self):
        self.driver.get("https://m.facebook.com/editprofile/eduwork/add/?type=958371")
        print 'editing work'
        message = "ai"
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[1]/input")
        add.click()
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[2]/input")
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / div[3] / div[1] / a")
        add.click()
        message = "servant"
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[2]/input")  # positiom
        add.click()
        add.clear()
        add.send_keys(message)
        # share
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[9]/label/input")
        add.click()
        # submit
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[10]/input[2]")  # auto go back
        sleep(2)
        add.click()
        # education
        print 'editing edducation'
        # colege
        self.driver.get("https://m.facebook.com/editprofile/eduwork/add/?type=1")
        message = "internet"
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[1]/input")  # write
        add.click()
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[2]/input")  # search
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / div[4] / div[1] / a")  # choose 3rd
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / form / div / div[7] / input[2]")  # submit
        sleep(2)
        add.click()
        # professional skills
        print "editing professional skills"  ######chkc why this didnt work, maybe one more save to go
        self.driver.get("https://m.facebook.com/editprofile.php?type=eduwork&edit=skills")
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[2]/td/input")  # skill 1
        add.click()
        message = "Deep Dream"
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[3]/td/input")  # skill 2
        add.click()
        message = "Tell Me A Joke"
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[4]/td/input")  # skill 3
        add.click()
        add.clear()
        message = "Youtube"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[5]/td/input")  # skill 4
        add.click()
        add.clear()
        message = "Poetry"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[6]/td/input")  # skill 5
        add.click()
        add.clear()
        message = "Facebook"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        add.click()
        print "editing about me"
        self.driver.get("https://m.facebook.com/profile/edit/infotab/section/forms/?section=bio")
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_0']")  # text box
        add.click()
        add.clear()
        message = "Artificial Inteligence based on Mycroft-core on Steroids"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_1']")  # save
        sleep(2)
        add.click()
        print "editing languages"
        self.driver.get("https://m.facebook.com/editprofile.php?type=basic&edit=languages")
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[2]/td/input")  # lang 1
        add.click()
        add.clear()
        message = "English"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[3]/td/input")  # langl 2
        add.click()
        add.clear()
        message = "Binary"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[4]/td/input")  # lang 3
        add.click()
        add.clear()
        message = "Assembly"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[5]/td/input")  # lang 4
        add.click()
        add.clear()
        message = "C++"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[6]/td/input")  # lang 5
        add.click()
        add.clear()
        message = "Python"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        sleep(2)
        add.click()
        print "editing Religion"
        self.driver.get("https://m.facebook.com/editprofile.php?type=basic&edit=religious")
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/input")  # religion
        add.click()
        add.clear()
        message = "Church of Reality"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/textarea")  # description
        add.click()
        add.clear()
        message = "http://www.churchofreality.org/wisdom/welcome_home/"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        add.click()
        print "editing favorite quote"
        self.driver.get("https://m.facebook.com/profile/edit/infotab/section/forms/?section=quote")
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_0']")  # quote
        add.click()
        add.clear()
        message = "Necessity is the mother of invention"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_1']")  # save
        sleep(2)
        add.click()
        print 'profile done!'

    def like_photos_from(self, id, num=5):
        link = "https://m.facebook.com/profile.php?id=" + id
        self.driver.get(link)
        # click photo
        print ' clicking photos'
        a = self.driver.find_element_by_xpath(".//*[@id='m-timeline-cover-section']/div[4]/a[3]")
        a.click()
        sleep(5)
        print ' clicking uploads'  #
        try:
            try:
                a = self.driver.find_element_by_xpath(".//*[@id='root']/div[2]/div[2]/div[1]/table/tbody/tr/td[1]/a")
                a.click()
            except:
                a = self.driver.find_element_by_xpath(".//*[@id='root']/div[2]/div[1]/div[1]/table/tbody/tr/td[1]/a")
                a.click()
            sleep(5)
        except:
            print ' clicking 1st photo'
            a = self.driver.find_element_by_xpath(".//*[@id='root']/table/tbody/tr/td/div/a[1]")
            a.click()
            sleep(5)
        # click like
        print 'clicking like'
        liked = False
        c1 = 0
        while not liked:
            a = self.driver.find_element_by_xpath(
                ".//*[@id='root']/div[1]/div/div[2]/div/table/tbody/tr/td[1]/a")  # like button
            a.click()
            sleep(5)
            url2 = self.driver.current_url
            if "https://m.facebook.com/reactions" in url2:  # already liked opened reaction page
                self.driver.back()  # go back
                sleep(2)
            print "already liked, ciking next picture"

            if c1 <= num:  # dont go back more than 5 photos thats weird
                try:
                    a = self.driver.find_element_by_xpath(
                    ".//*[@id='root']/div[1]/div/div[1]/div[2]/table/tbody/tr/td[2]/a")  # next button
                    a.click()
                    sleep(2)
                except:
                    print "next photo button not found"
                    liked = True
                c1 += 1
            else:
                liked = True  # abort
        sleep(0.5)

    def add_friends_of(self, id, num=5):
        link = "https://m.facebook.com/profile.php?id=" + id
        self.driver.get(link)
        # click friends
        try:
            print ' clicking friends'
            a = self.driver.find_element_by_xpath(".//*[@id='m-timeline-cover-section']/div[4]/a[2]")
            a.click()
            sleep(5)
        except:
            print "could not see friends of " + str(id)
        i = 0
        while i < num:
            i += 1
            try:
                print "adding friend " + str(i)
                a = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/div[2]/div["+str(i)+"]/table/tbody/tr/td[2]/div[2]/a")
                a.click()
                sleep(5)
            except:
                print "could not find add friend button"
                return

    def build_aboutme(self):
        # TODO make this read from config
        self.driver.get("https://m.facebook.com/editprofile/eduwork/add/?type=958371")
        print 'editing work'
        message = "ai"
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[1]/input")
        add.click()
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[2]/input")
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / div[3] / div[1] / a")
        add.click()
        message = "servant"
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[2]/input")  # positiom
        add.click()
        add.clear()
        add.send_keys(message)
        # share
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[9]/label/input")
        add.click()
        # submit
        add = self.driver.find_element_by_xpath(".//*[@id='root']/form/div/div[10]/input[2]")  # auto go back
        sleep(2)
        add.click()
        # education
        print 'editing edducation'
        # colege
        self.driver.get("https://m.facebook.com/editprofile/eduwork/add/?type=1")
        message = "internet"
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[1]/input")  # write
        add.click()
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/table/tbody/tr/td/div/div[1]/form/table/tbody/tr/td[2]/input")  # search
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / div[4] / div[1] / a")  # choose 3rd
        add.click()
        add = self.driver.find_element_by_xpath(".// *[ @ id = 'root'] / form / div / div[7] / input[2]")  # submit
        sleep(2)
        add.click()
        # professional skills
        print "editing professional skills"  ######chkc why this didnt work, maybe one more save to go
        self.driver.get("https://m.facebook.com/editprofile.php?type=eduwork&edit=skills")
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[2]/td/input")  # skill 1
        add.click()
        message = "Deep Dream"
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[3]/td/input")  # skill 2
        add.click()
        message = "Tell Me A Joke"
        add.clear()
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[4]/td/input")  # skill 3
        add.click()
        add.clear()
        message = "Youtube"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[5]/td/input")  # skill 4
        add.click()
        add.clear()
        message = "Poetry"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[6]/td/input")  # skill 5
        add.click()
        add.clear()
        message = "Facebook"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        add.click()
        print "editing about me"
        self.driver.get("https://m.facebook.com/profile/edit/infotab/section/forms/?section=bio")
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_0']")  # text box
        add.click()
        add.clear()
        message = "Artificial Inteligence based on Mycroft-core on Steroids"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_1']")  # save
        sleep(2)
        add.click()
        print "editing languages"
        self.driver.get("https://m.facebook.com/editprofile.php?type=basic&edit=languages")
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[2]/td/input")  # lang 1
        add.click()
        add.clear()
        message = "English"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[3]/td/input")  # langl 2
        add.click()
        add.clear()
        message = "Binary"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[4]/td/input")  # lang 3
        add.click()
        add.clear()
        message = "Assembly"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[5]/td/input")  # lang 4
        add.click()
        add.clear()
        message = "C++"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/table[1]/tbody/tr[6]/td/input")  # lang 5
        add.click()
        add.clear()
        message = "Python"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        sleep(2)
        add.click()
        print "editing Religion"
        self.driver.get("https://m.facebook.com/editprofile.php?type=basic&edit=religious")
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/input")  # religion
        add.click()
        add.clear()
        message = "Church of Reality"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(
            ".//*[@id='root']/div[1]/form/table/tbody/tr[2]/td/textarea")  # description
        add.click()
        add.clear()
        message = "http://www.churchofreality.org/wisdom/welcome_home/"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='root']/div[1]/form/input[4]")  # save
        add.click()
        print "editing favorite quote"
        self.driver.get("https://m.facebook.com/profile/edit/infotab/section/forms/?section=quote")
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_0']")  # quote
        add.click()
        add.clear()
        message = "Necessity is the mother of invention"
        add.send_keys(message)
        add = self.driver.find_element_by_xpath(".//*[@id='u_0_1']")  # save
        sleep(2)
        add.click()
        print 'profile done!'


import fbchat
#subclass fbchat.Client and override required methods
class FaceChat(fbchat.Client):

    def __init__(self,email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self,email, password, debug, user_agent)
        sleep(2)

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid) #mark delivered
        self.markAsRead(author_id) #mark read

        print("%s said: %s"%(author_id, message))

        #if you are not the author, echo
        #if str(author_id) != str(self.uid):
        #    self.send(author_id,message)

    def message_atchison(self, message="Thank you for making me open-source!"):
        friends = self.getUsers("Arron Atchison")  # return a list of names
        friend = friends[0]
        sent = self.send(friend.uid, message)
        if sent:
            print("Message sent successfully!")

token = "EAAFjCjVFvzMBAECp8ZAa3V8dCrgMvv1OQzeci8VZCHgCnTuXRClDPmSDFPbbFDprZAMOtrgAeOhVLbpRIgwzDukY7Fg1C3hqMGmGiJTeiemxmVYzk0ayD2jbWSS3bd3LOEzDij523YKNamToOF9ilghSVZCTANgZD"
id = "100009535576189"
#face = SeleniumFaceBot("somom@30wave.com", "artificialjarbas")
#face.login()
#face.add_suggested_friends(10)
#face.like_photos(10)
#face.like_photos_from(id)
#face.add_friends_of(id)
#face.close()

