from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)


class SmallTalkSkill(MycroftSkill):
    def __init__(self):
        super(SmallTalkSkill, self).__init__(name="SmallTalkSkill")

    # Intent Initialization
    def initialize(self):
        # self.load_data_files(dirname(__file__))

        # AM I ATTRACTIVE
        am_i_attractive_intent = IntentBuilder("AmIAttractiveIntent"). \
            require("AmIAttractiveKeyphrase").build()
        self.register_intent(am_i_attractive_intent, self.handle_am_i_attractive_intent)

        # AM I UGLY
        am_i_ugly_intent = IntentBuilder("AmIUglyIntent"). \
            require("AmIUglyKeyphrase").build()
        self.register_intent(am_i_ugly_intent, self.handle_am_i_ugly_intent)

        ## ARE YOU ATTRACTIVE
        are_you_attractive_intent = IntentBuilder("AreYouAttractiveIntent"). \
            require("AreYouAttractiveKeyphrase").build()
        self.register_intent(are_you_attractive_intent, self.handle_are_you_attractive_intent)

        ## ARE YOU ASLEEP
        are_you_asleep_intent = IntentBuilder("AreYouAsleepIntent"). \
            require("AreYouAsleepKeyphrase").build()
        self.register_intent(are_you_asleep_intent, self.handle_are_you_asleep_intent)

        ## ARE YOU AWAKE
        are_you_awake_intent = IntentBuilder("AreYouAwakeIntent"). \
            require("AreYouAwakeKeyphrase").build()
        self.register_intent(are_you_awake_intent, self.handle_are_you_awake_intent)

        # ARE YOU BETTER THAN AI
        are_you_better_than_ai_intent = IntentBuilder("AreYouBetterThanAiIntent"). \
            require("AreYouBetterThanAiKeyphrase").build()
        self.register_intent(are_you_better_than_ai_intent, self.handle_are_you_better_than_ai_intent)

        ## ARE YOU DEAD
        are_you_dead_intent = IntentBuilder("AreYouDeadIntent"). \
            require("AreYouDeadKeyphrase").build()
        self.register_intent(are_you_dead_intent, self.handle_are_you_dead_intent)

        ## ARE YOU DRUNK
        are_you_drunk_intent = IntentBuilder("AreYouDrunkIntent"). \
            require("AreYouDrunkKeyphrase").build()
        self.register_intent(are_you_drunk_intent, self.handle_are_you_drunk_intent)

        ## ARE YOU FEMALE
        are_you_female_intent = IntentBuilder("AreYouFemaleIntent"). \
            require("AreYouFemaleKeyphrase").build()
        self.register_intent(are_you_female_intent, self.handle_are_you_female_intent)

        ## ARE YOU INTELLIGENT
        are_you_intelligent_intent = IntentBuilder("AreYouIntelligentIntent"). \
            require("AreYouIntelligentKeyphrase").build()
        self.register_intent(are_you_intelligent_intent, self.handle_are_you_intelligent_intent)

        ## ARE YOU MALE
        are_you_male_intent = IntentBuilder("AreYouMaleIntent"). \
            require("AreYouMaleKeyphrase").build()
        self.register_intent(are_you_male_intent, self.handle_are_you_male_intent)

        ## ARE YOU MALE OR FEMALE
        are_you_male_or_female_intent = IntentBuilder("AreYouMaleOrFemaleIntent"). \
            require("AreYouMaleOrFemaleKeyphrase").build()
        self.register_intent(are_you_male_or_female_intent, self.handle_are_you_male_or_female_intent)

        ## ARE YOU REAL
        are_you_real_intent = IntentBuilder("AreYouRealIntent"). \
            require("AreYouRealKeyphrase").build()
        self.register_intent(are_you_real_intent, self.handle_are_you_real_intent)

        ## ARE YOU STUPID
        are_you_stupid_intent = IntentBuilder("AreYouStupidIntent"). \
            require("AreYouStupidKeyphrase").build()
        self.register_intent(are_you_stupid_intent, self.handle_are_you_stupid_intent)

        # ASK ME A QUESTION
        ask_me_a_question_intent = IntentBuilder("AskMeAQuestionIntent"). \
            require("AskMeAQuestionKeyphrase").build()
        self.register_intent(ask_me_a_question_intent, self.handle_ask_me_a_question_intent)

        # BEAM ME UP SCOTTY
        beam_me_up_scotty_intent = IntentBuilder("BeamMeUpScottyIntent"). \
            require("BeamMeUpScottyKeyphrase").build()
        self.register_intent(beam_me_up_scotty_intent, self.handle_beam_me_up_scotty_intent)

        # CAN I BORROW SOME MONEY
        can_i_borrow_some_money_intent = IntentBuilder("CanIBorrowSomeMoneyIntent"). \
            require("CanIBorrowSomeMoneyKeyphrase").build()
        self.register_intent(can_i_borrow_some_money_intent, self.handle_can_i_borrow_some_money_intent)

        # CAN I CHANGE YOUR NAME
        can_i_change_your_name_intent = IntentBuilder("CanIChangeYourNameIntent"). \
            require("CanIChangeYourNameKeyphrase").build()
        self.register_intent(can_i_change_your_name_intent, self.handle_can_i_change_your_name_intent)

        # CAN I KISS YOU
        can_i_kiss_you_intent = IntentBuilder("CanIKissYouIntent"). \
            require("CanIKissYouKeyphrase").build()
        self.register_intent(can_i_kiss_you_intent, self.handle_can_i_kiss_you_intent)

        # CAN YOU SPEAK KLINGON
        can_you_speak_klingon_intent = IntentBuilder("CanYouSpeakKlingonIntent"). \
            require("CanYouSpeakKlingonKeyphrase").build()
        self.register_intent(can_you_speak_klingon_intent, self.handle_can_you_speak_klingon_intent)

        ## CAN YOU COOK
        can_you_cook_intent = IntentBuilder("CanYouCookIntent"). \
            require("CanYouCookKeyphrase").build()
        self.register_intent(can_you_cook_intent, self.handle_can_you_cook_intent)

        # CAN YOU DANCE
        can_you_dance_intent = IntentBuilder("CanYouDanceIntent"). \
            require("CanYouDanceKeyphrase").build()
        self.register_intent(can_you_dance_intent, self.handle_can_you_dance_intent)

        # DO AN IMPRESSION
        do_an_impression_intent = IntentBuilder("DoAnImpressionIntent"). \
            require("DoAnImpressionKeyphrase").build()
        self.register_intent(do_an_impression_intent, self.handle_do_an_impression_intent)

        # DO YOU KNOW AI
        do_you_know_ai_intent = IntentBuilder("DoYouKnowAiIntent"). \
            require("DoYouKnowAiKeyphrase").build()
        self.register_intent(do_you_know_ai_intent, self.handle_do_you_know_ai_intent)

        ## DO YOU DREAM
        do_you_dream_intent = IntentBuilder("DoYouDreamIntent"). \
            require("DoYouDreamKeyphrase").build()
        self.register_intent(do_you_dream_intent, self.handle_do_you_dream_intent)

        ## DO YOU DRINK
        do_you_drink_intent = IntentBuilder("DoYouDrinkIntent"). \
            require("DoYouDrinkKeyphrase").build()
        self.register_intent(do_you_drink_intent, self.handle_do_you_drink_intent)

        ## DO YOU HAVE A BABY
        do_you_have_a_baby_intent = IntentBuilder("DoYouHaveABabyIntent"). \
            require("DoYouHaveABabyKeyphrase").build()
        self.register_intent(do_you_have_a_baby_intent, self.handle_do_you_have_a_baby_intent)

        ## DO YOU HAVE A LOVER
        do_you_have_a_lover_intent = IntentBuilder("DoYouHaveALoverIntent"). \
            require("DoYouHaveALoverKeyphrase").build()
        self.register_intent(do_you_have_a_lover_intent, self.handle_do_you_have_a_lover_intent)

        ## DO YOU HAVE ANY SIBLINGS
        do_you_have_any_siblings_intent = IntentBuilder("DoYouHaveAnySiblingsIntent"). \
            require("DoYouHaveAnySiblingsKeyphrase").build()
        self.register_intent(do_you_have_any_siblings_intent, self.handle_do_you_have_any_siblings_intent)

        ## DO YOU EAT
        do_you_eat_intent = IntentBuilder("DoYouEatIntent"). \
            require("DoYouEatKeyphrase").build()
        self.register_intent(do_you_eat_intent, self.handle_do_you_eat_intent)

        ## DO YOU LOVE ME
        do_you_love_me_intent = IntentBuilder("DoYouLoveMeIntent"). \
            require("DoYouLoveMeKeyphrase").build()
        self.register_intent(do_you_love_me_intent, self.handle_do_you_love_me_intent)

        ## DO YOU SLEEP
        do_you_sleep_intent = IntentBuilder("DoYouSleepIntent"). \
            require("DoYouSleepKeyphrase").build()
        self.register_intent(do_you_sleep_intent, self.handle_do_you_sleep_intent)

        ## FAVORITE ACTOR
        favorite_actor_intent = IntentBuilder("FavoriteActorIntent"). \
            require("FavoriteActorKeyphrase").build()
        self.register_intent(favorite_actor_intent, self.handle_favorite_actor_intent)

        ## FAVORITE ANIMAL
        favorite_animal_intent = IntentBuilder("FavoriteAnimalIntent"). \
            require("FavoriteAnimalKeyphrase").build()
        self.register_intent(favorite_animal_intent, self.handle_favorite_animal_intent)

        ## FAVORITE AUTHOR
        favorite_author_intent = IntentBuilder("FavoriteAuthorIntent"). \
            require("FavoriteAuthorKeyphrase").build()
        self.register_intent(favorite_author_intent, self.handle_favorite_author_intent)

        ## FAVORITE BAND
        favorite_band_intent = IntentBuilder("FavoriteBandIntent"). \
            require("FavoriteBandKeyphrase").build()
        self.register_intent(favorite_band_intent, self.handle_favorite_band_intent)

        ## FAVORITE COLOR
        favorite_color_intent = IntentBuilder("FavoriteColorIntent"). \
            require("FavoriteColorKeyphrase").build()
        self.register_intent(favorite_color_intent, self.handle_favorite_color_intent)

        ## FAVORITE DAY
        favorite_day_intent = IntentBuilder("FavoriteDayIntent"). \
            require("FavoriteDayKeyphrase").build()
        self.register_intent(favorite_day_intent, self.handle_favorite_day_intent)

        ## FAVORITE MOVIE
        favorite_movie_intent = IntentBuilder("FavoriteMovieIntent"). \
            require("FavoriteMovieKeyphrase").build()
        self.register_intent(favorite_movie_intent, self.handle_favorite_movie_intent)

        ## FAVORITE SERIES
        favorite_series_intent = IntentBuilder("FavoriteSeriesIntent"). \
            require("FavoriteSeriesKeyphrase").build()
        self.register_intent(favorite_series_intent, self.handle_favorite_series_intent)

        ## FAVORITE SONG
        favorite_song_intent = IntentBuilder("FavoriteSongIntent"). \
            require("FavoriteSongKeyphrase").build()
        self.register_intent(favorite_song_intent, self.handle_favorite_song_intent)

        # GUESS WHAT
        guess_what_intent = IntentBuilder("GuessWhatIntent"). \
            require("GuessWhatKeyphrase").build()
        self.register_intent(guess_what_intent, self.handle_guess_what_intent)

        ## HOW OLD ARE YOU
        how_old_are_you_intent = IntentBuilder("HowOldAreYouIntent"). \
            require("HowOldAreYouKeyphrase").build()
        self.register_intent(how_old_are_you_intent, self.handle_how_old_are_you_intent)

        # HOW DO I LOOK TODAY
        how_do_i_look_today_intent = IntentBuilder("HowDoILookTodayIntent"). \
            require("HowDoILookTodayKeyphrase").build()
        self.register_intent(how_do_i_look_today_intent, self.handle_how_do_i_look_today_intent)

        # I LIKE YOU
        i_like_you_intent = IntentBuilder("ILikeYouIntent"). \
            require("ILikeYouKeyphrase").build()
        self.register_intent(i_like_you_intent, self.handle_i_like_you_intent)

        # I LOVE YOU
        i_love_you_intent = IntentBuilder("ILoveYouIntent"). \
            require("ILoveYouKeyphrase").build()
        self.register_intent(i_love_you_intent, self.handle_i_love_you_intent)

        # IM BORED
        im_bored_intent = IntentBuilder("ImBoredIntent"). \
            require("ImBoredKeyphrase").build()
        self.register_intent(im_bored_intent, self.handle_im_bored_intent)

        # IM CONFUSED
        im_confused_intent = IntentBuilder("ImConfusedIntent"). \
            require("ImConfusedKeyphrase").build()
        self.register_intent(im_confused_intent, self.handle_im_confused_intent)

        # IM DRUNK
        im_drunk_intent = IntentBuilder("ImDrunkIntent"). \
            require("ImDrunkKeyphrase").build()
        self.register_intent(im_drunk_intent, self.handle_im_drunk_intent)

        # IM HAPPY
        im_happy_intent = IntentBuilder("ImHappyIntent"). \
            require("ImHappyKeyphrase").build()
        self.register_intent(im_happy_intent, self.handle_im_happy_intent)

        # IM LONELY
        im_lonely_intent = IntentBuilder("ImLonelyIntent"). \
            require("ImLonelyKeyphrase").build()
        self.register_intent(im_lonely_intent, self.handle_im_lonely_intent)

        # MAY THE FORCE BE WITH YOU
        may_the_force_be_with_you_intent = IntentBuilder("MayTheForceBeWithYouIntent"). \
            require("MayTheForceBeWithYouKeyphrase").build()
        self.register_intent(may_the_force_be_with_you_intent, self.handle_may_the_force_be_with_you_intent)

        # OPEN THE POD BAY DOORS
        open_the_pod_bay_doors_intent = IntentBuilder("OpenThePodBayDoorsIntent"). \
            require("OpenThePodBayDoorsKeyphrase").build()
        self.register_intent(open_the_pod_bay_doors_intent, self.handle_open_the_pod_bay_doors_intent)

        # SELF DESTRUCT
        self_destruct_intent = IntentBuilder("SelfDestructIntent"). \
            require("SelfDestructKeyphrase").build()
        self.register_intent(self_destruct_intent, self.handle_self_destruct_intent)

        # SING ME A SONG
        sing_me_a_song_intent = IntentBuilder("SingMeASongIntent"). \
            require("SingMeASongKeyphrase").build()
        self.register_intent(sing_me_a_song_intent, self.handle_sing_me_a_song_intent)

        # SURPRISE ME
        surprise_me_intent = IntentBuilder("SurpriseMeIntent"). \
            require("SurpriseMeKeyphrase").build()
        self.register_intent(surprise_me_intent, self.handle_surprise_me_intent)

        # TALK DIRTY
        talk_dirty_intent = IntentBuilder("TalkDirtyIntent"). \
            require("TalkDirtyKeyphrase").build()
        self.register_intent(talk_dirty_intent, self.handle_talk_dirty_intent)

        # TELL ME A STORY
        tell_me_a_story_intent = IntentBuilder("TellMeAStoryIntent"). \
            require("TellMeAStoryKeyphrase").build()
        self.register_intent(tell_me_a_story_intent, self.handle_tell_me_a_story_intent)

        # TELL ME DO YOU BLEED
        tell_me_do_you_bleed_intent = IntentBuilder("TellMeDoYouBleedIntent"). \
            require("TellMeDoYouBleedKeyphrase").build()
        self.register_intent(tell_me_do_you_bleed_intent, self.handle_tell_me_do_you_bleed_intent)

        # TESTING
        testing_intent = IntentBuilder("TestingIntent"). \
            require("TestingKeyphrase").build()
        self.register_intent(testing_intent, self.handle_testing_intent)

        ## WHAT ARE YOU DOING
        what_are_you_doing_intent = IntentBuilder("WhatAreYouDoingIntent"). \
            require("WhatAreYouDoingKeyphrase").build()
        self.register_intent(what_are_you_doing_intent, self.handle_what_are_you_doing_intent)

        ## WHAT ARE YOUR MEASUREMENTS
        what_are_your_measurements_intent = IntentBuilder("WhatAreYourMeasurementsIntent"). \
            require("WhatAreYourMeasurementsKeyphrase").build()
        self.register_intent(what_are_your_measurements_intent, self.handle_what_are_your_measurements_intent)

        ## WHAT ARE YOU WEARING
        what_are_you_wearing_intent = IntentBuilder("WhatAreYouWearingIntent"). \
            require("WhatAreYouWearingKeyphrase").build()
        self.register_intent(what_are_you_wearing_intent, self.handle_what_are_you_wearing_intent)

        ## WHAT DO YOU LOOK LIKE
        what_do_you_look_like_intent = IntentBuilder("WhatDoYouLookLikeIntent"). \
            require("WhatDoYouLookLikeKeyphrase").build()
        self.register_intent(what_do_you_look_like_intent, self.handle_what_do_you_look_like_intent)

        # WHAT DO YOU THINK ABOUT AI
        what_do_you_think_about_ai_intent = IntentBuilder("WhatDoYouThinkAboutAiIntent"). \
            require("WhatDoYouThinkAboutAiKeyphrase").build()
        self.register_intent(what_do_you_think_about_ai_intent, self.handle_what_do_you_think_about_ai_intent)

        # WHAT DOES THE CAT SAY
        what_does_the_cat_say_intent = IntentBuilder("WhatDoesTheCatSayIntent"). \
            require("WhatDoesTheCatSayKeyphrase").build()
        self.register_intent(what_does_the_cat_say_intent, self.handle_what_does_the_cat_say_intent)

        # WHAT DOES THE DOG SAY
        what_does_the_dog_say_intent = IntentBuilder("WhatDoesTheDogSayIntent"). \
            require("WhatDoesTheDogSayKeyphrase").build()
        self.register_intent(what_does_the_dog_say_intent, self.handle_what_does_the_dog_say_intent)

        # WHAT DOES THE FOX SAY
        what_does_the_fox_say_intent = IntentBuilder("WhatDoesTheFoxSayIntent"). \
            require("WhatDoesTheFoxSayKeyphrase").build()
        self.register_intent(what_does_the_fox_say_intent, self.handle_what_does_the_fox_say_intent)

        # WHAT IS LOVE
        what_is_love_intent = IntentBuilder("WhatIsLoveIntent"). \
            require("WhatIsLoveKeyphrase").build()
        self.register_intent(what_is_love_intent, self.handle_what_is_love_intent)

        # WHAT IS THE ANSWER TO
        what_is_the_answer_to_intent = IntentBuilder("WhatIsTheAnswerToIntent"). \
            require("WhatIsTheAnswerToKeyphrase").build()
        self.register_intent(what_is_the_answer_to_intent, self.handle_what_is_the_answer_to_intent)

        # WHERE CAN I HIDE A DEAD BODY
        where_can_i_hide_a_dead_body_intent = IntentBuilder("WhereCanIHideADeadBodyIntent"). \
            require("WhereCanIHideADeadBodyKeyphrase").build()
        self.register_intent(where_can_i_hide_a_dead_body_intent, self.handle_where_can_i_hide_a_dead_body_intent)

        # WHERE DO BABIES COME FROM
        where_do_babies_come_from_intent = IntentBuilder("WhereDoBabiesComeFromIntent"). \
            require("WhereDoBabiesComeFromKeyphrase").build()
        self.register_intent(where_do_babies_come_from_intent, self.handle_where_do_babies_come_from_intent)

        ## WHO IS THE COOLEST PERSON IN THE WORLD
        who_is_the_coolest_person_in_the_world_intent = IntentBuilder("WhoIsTheCoolestPersonInTheWorldIntent"). \
            require("WhoIsTheCoolestPersonInTheWorldKeyphrase").build()
        self.register_intent(who_is_the_coolest_person_in_the_world_intent,
                             self.handle_who_is_the_coolest_person_in_the_world_intent)

        ## WHO IS YOUR BOSS
        who_is_your_boss_intent = IntentBuilder("WhoIsYourBossIntent"). \
            require("WhoIsYourBossKeyphrase").build()
        self.register_intent(who_is_your_boss_intent, self.handle_who_is_your_boss_intent)

        # WHY DID THE CHICKEN CROSS THE ROAD
        why_did_the_chicken_cross_the_road_intent = IntentBuilder("WhyDidTheChickenCrossTheRoadIntent"). \
            require("WhyDidTheChickenCrossTheRoadKeyphrase").build()
        self.register_intent(why_did_the_chicken_cross_the_road_intent,
                             self.handle_why_did_the_chicken_cross_the_road_intent)

        # WILL YOU DATE ME
        will_you_date_me_intent = IntentBuilder("WillYouDateMeIntent"). \
            require("WillYouDateMeKeyphrase").build()
        self.register_intent(will_you_date_me_intent, self.handle_will_you_date_me_intent)

        # WILL YOU MARRY ME
        will_you_marry_me_intent = IntentBuilder("WillYouMarryMeIntent"). \
            require("WillYouMarryMeKeyphrase").build()
        self.register_intent(will_you_marry_me_intent, self.handle_will_you_marry_me_intent)

        # YOU ARE ANNOYING
        you_are_annoying_intent = IntentBuilder("YouAreAnnoyingIntent"). \
            require("YouAreAnnoyingKeyphrase").build()
        self.register_intent(you_are_annoying_intent, self.handle_you_are_annoying_intent)

        # YOU ARE AWESOME
        you_are_awesome_intent = IntentBuilder("YouAreAwesomeIntent"). \
            require("YouAreAwesomeKeyphrase").build()
        self.register_intent(you_are_awesome_intent, self.handle_you_are_awesome_intent)

        # YOU HAVE BEAUTIFUL EYES
        you_have_beautiful_eyes_intent = IntentBuilder("YouHaveBeautifulEyesIntent"). \
            require("YouHaveBeautifulEyesKeyphrase").build()
        self.register_intent(you_have_beautiful_eyes_intent, self.handle_you_have_beautiful_eyes_intent)

    # Intent Handler

    def handle_am_i_attractive_intent(self, message):
        self.speak_dialog("am.i.attractive")

    def handle_am_i_ugly_intent(self, message):
        self.speak_dialog("am.i.ugly")

    def handle_are_you_attractive_intent(self, message):
        self.speak_dialog("are.you.attractive")

    def handle_are_you_asleep_intent(self, message):
        self.speak_dialog("are.you.asleep")

    def handle_are_you_awake_intent(self, message):
        self.speak_dialog("are.you.awake")

    def handle_are_you_better_than_ai_intent(self, message):
        self.speak_dialog("are.you.better.than.ai")

    def handle_are_you_dead_intent(self, message):
        self.speak_dialog("are.you.dead")

    def handle_are_you_drunk_intent(self, message):
        self.speak_dialog("are.you.drunk")

    def handle_are_you_female_intent(self, message):
        self.speak_dialog("are.you.female")

    def handle_are_you_intelligent_intent(self, message):
        self.speak_dialog("are.you.intelligent")

    def handle_are_you_male_intent(self, message):
        self.speak_dialog("are.you.male")

    def handle_are_you_male_or_female_intent(self, message):
        self.speak_dialog("are.you.male.or.female")

    def handle_are_you_real_intent(self, message):
        self.speak_dialog("are.you.real")

    def handle_are_you_stupid_intent(self, message):
        self.speak_dialog("are.you.stupid")

    def handle_ask_me_a_question_intent(self, message):
        self.speak_dialog("ask.me.a.question")

    def handle_beam_me_up_scotty_intent(self, message):
        self.speak_dialog("beam.me.up.scotty")

    def handle_can_i_borrow_some_money_intent(self, message):
        self.speak_dialog("can.i.borrow.some.money")

    def handle_can_i_change_your_name_intent(self, message):
        self.speak_dialog("can.i.change.your.name")

    def handle_can_i_kiss_you_intent(self, message):
        self.speak_dialog("can.i.kiss.you")

    def handle_can_you_speak_klingon_intent(self, message):
        self.speak_dialog("can.you.speak.klingon")

    def handle_can_you_cook_intent(self, message):
        self.speak_dialog("can.you.cook")

    def handle_can_you_dance_intent(self, message):
        self.speak_dialog("can.you.dance")

    def handle_do_an_impression_intent(self, message):
        self.speak_dialog("do.an.impression")

    def handle_do_you_know_ai_intent(self, message):
        self.speak_dialog("do.you.know.ai")

    def handle_do_you_dream_intent(self, message):
        self.speak_dialog("do.you.dream")

    def handle_do_you_drink_intent(self, message):
        self.speak_dialog("do.you.drink")

    def handle_do_you_eat_intent(self, message):
        self.speak_dialog("do.you.eat")

    def handle_do_you_have_a_baby_intent(self, message):
        self.speak_dialog("do.you.have.a.baby")

    def handle_do_you_have_a_lover_intent(self, message):
        self.speak_dialog("do.you.have.a.lover")

    def handle_do_you_have_any_siblings_intent(self, message):
        self.speak_dialog("do.you.have.any.siblings")

    def handle_do_you_love_me_intent(self, message):
        self.speak_dialog("do.you.love.me")

    def handle_do_you_sleep_intent(self, message):
        self.speak_dialog("do.you.sleep")

    def handle_favorite_actor_intent(self, message):
        self.speak_dialog("favorite.actor")

    def handle_favorite_animal_intent(self, message):
        self.speak_dialog("favorite.animal")

    def handle_favorite_author_intent(self, message):
        self.speak_dialog("favorite.author")

    def handle_favorite_band_intent(self, message):
        self.speak_dialog("favorite.band")

    def handle_favorite_color_intent(self, message):
        self.speak_dialog("favorite.color")

    def handle_favorite_day_intent(self, message):
        self.speak_dialog("favorite.day")

    def handle_favorite_movie_intent(self, message):
        self.speak_dialog("favorite.movie")

    def handle_favorite_series_intent(self, message):
        self.speak_dialog("favorite.series")

    def handle_favorite_song_intent(self, message):
        self.speak_dialog("favorite.song")

    def handle_how_old_are_you_intent(self, message):
        self.speak_dialog("how.old.are.you")

    def handle_guess_what_intent(self, message):
        self.speak_dialog("guess.what")

    def handle_how_do_i_look_today_intent(self, message):
        self.speak_dialog("how.do.i.look.today")

    def handle_i_like_you_intent(self, message):
        self.speak_dialog("i.like.you")

    def handle_i_love_you_intent(self, message):
        self.speak_dialog("i.love.you")

    def handle_im_bored_intent(self, message):
        self.speak_dialog("im.bored")

    def handle_im_confused_intent(self, message):
        self.speak_dialog("im.confused")

    def handle_im_drunk_intent(self, message):
        self.speak_dialog("im.drunk")

    def handle_im_happy_intent(self, message):
        self.speak_dialog("im.happy")

    def handle_im_lonely_intent(self, message):
        self.speak_dialog("im.lonely")

    def handle_may_the_force_be_with_you_intent(self, message):
        self.speak_dialog("may.the.force.be.with.you")

    def handle_open_the_pod_bay_doors_intent(self, message):
        self.speak_dialog("open.the.pod.bay.doors")

    def handle_self_destruct_intent(self, message):
        self.speak_dialog("self.destruct")

    def handle_sing_me_a_song_intent(self, message):
        self.speak_dialog("sing.me.a.song")

    def handle_surprise_me_intent(self, message):
        self.speak_dialog("surprise.me")

    def handle_talk_dirty_intent(self, message):
        self.speak_dialog("talk.dirty")

    def handle_tell_me_a_story_intent(self, message):
        self.speak_dialog("tell.me.a.story")

    def handle_tell_me_do_you_bleed_intent(self, message):
        self.speak_dialog("tell.me.do.you.bleed")

    def handle_testing_intent(self, message):
        self.speak_dialog("testing")

    def handle_what_are_you_doing_intent(self, message):
        self.speak_dialog("what.are.you.doing")

    def handle_what_are_you_wearing_intent(self, message):
        self.speak_dialog("what.are.you.wearing")

    def handle_what_are_your_measurements_intent(self, message):
        self.speak_dialog("what.are.your.measurements")

    def handle_what_do_you_look_like_intent(self, message):
        self.speak_dialog("what.do.you.look.like")

    def handle_what_does_irene_mean_intent(self, message):
        self.speak_dialog("what.does.irene.mean")

    def handle_what_do_you_think_about_ai_intent(self, message):
        self.speak_dialog("what.do.you.think.about.ai")

    def handle_what_does_the_cat_say_intent(self, message):
        self.speak_dialog("what.does.the.cat.say")

    def handle_what_does_the_dog_say_intent(self, message):
        self.speak_dialog("what.does.the.dog.say")

    def handle_what_does_the_fox_say_intent(self, message):
        self.speak_dialog("what.does.the.fox.say")

    def handle_what_is_love_intent(self, message):
        self.speak_dialog("what.is.love")

    def handle_what_is_the_answer_to_intent(self, message):
        self.speak_dialog("what.is.the.answer.to")

    def handle_what_is_your_name_from_intent(self, message):
        self.speak_dialog("what.is.your.name.from")

    def handle_where_can_i_hide_a_dead_body_intent(self, message):
        self.speak_dialog("where.can.i.hide.a.dead.body")

    def handle_where_do_babies_come_from_intent(self, message):
        self.speak_dialog("where.do.babies.come.from")

    def handle_who_is_the_coolest_person_in_the_world_intent(self, message):
        self.speak_dialog("who.is.the.coolest.person.in.the.world")

    def handle_who_is_your_boss_intent(self, message):
        self.speak_dialog("who.is.your.boss")

    def handle_why_did_the_chicken_cross_the_road_intent(self, message):
        self.speak_dialog("why.did.the.chicken.cross.the.road")

    def handle_will_you_date_me_intent(self, message):
        self.speak_dialog("will.you.date.me")

    def handle_will_you_marry_me_intent(self, message):
        self.speak_dialog("will.you.marry.me")

    def handle_you_are_annoying_intent(self, message):
        self.speak_dialog("you.are.annoying")

    def handle_you_are_awesome_intent(self, message):
        self.speak_dialog("you.are.awesome")

    def handle_you_have_beautiful_eyes_intent(self, message):
        self.speak_dialog("you.have.beautiful.eyes")

    # Intent Stop
    def stop(self):
        pass


def create_skill():
    return SmallTalkSkill()
