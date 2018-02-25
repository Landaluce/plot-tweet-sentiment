import tweepy
from api_credentials import TWITTER_API_KEYS, GOOGLE_API_KEY
from constants import *
import json
import pickle
import os
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, Range1d, PanTool, WheelZoomTool
)
from content_analysis_model import ContentAnalysisModel
from time import sleep, time
import glob


class Tweet:
    id = 0
    content = ""
    latitude = 0.0
    longitude = 0.0
    language = 0.0
    created_at = ""
    sentiment = 0.0

    def __init__(self, id, content, latitude, longitude, created_at, language=None):
        self.id = id
        self.content = content
        self.latitude = latitude
        self.longitude = longitude
        self.created_at = created_at
        self.language = language


class Tweets:
    tweets = []

    def __init__(self):
        self.tweets = []

    @property
    def ids(self):
        return [tweet.id for tweet in self.tweets]
    @property
    def latitudes(self):
        return [tweet.latitude for tweet in self.tweets]

    @property
    def longitudes(self):
        return [tweet.longitude for tweet in self.tweets]


def search_tweets(search_query, number_tweets=15, geocode=None, lang=None):
    """Gets a list of tweets.

    https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
    :param search_query: search query used to find tweets (String)
    :param number_tweets: number of tweets to get (Integer)
    :param lang: Restricts tweets to the given language, given by an ISO 639-1 code. Language detection is best-effort.
    :param geocode: Returns tweets by users located within a given radius of the given latitude/longitude.
    :return: List of tweet objects
    """
    key_index = 0
    authentication = tweepy.OAuthHandler(
        TWITTER_API_KEYS[key_index]["consumer_key"],
        TWITTER_API_KEYS[key_index]["consumer_secret"])
    authentication.set_access_token(
        TWITTER_API_KEYS[key_index]["access_token"],
        TWITTER_API_KEYS[key_index]["access_token_secret"])
    twitter_api = tweepy.API(authentication)
    max_id = 0  # If results only below a specific ID are, set max_id to that ID, else default to no upper limit
    tweets = []
    while len(tweets) < number_tweets:
        try:
            if max_id <= 0:
                if not SINCE_ID:
                    new_tweets = twitter_api.search(q=search_query,
                                                    count=TWEETS_PER_QUERY,
                                                    geocode=geocode,
                                                    lang=lang,
                                                    tweet_mode="extended")
                else:
                    new_tweets = twitter_api.search(q=search_query,
                                                    count=TWEETS_PER_QUERY,
                                                    geocode=geocode,
                                                    lang=lang,
                                                    tweet_mode="extended",
                                                    since_id=SINCE_ID)
            else:
                if not SINCE_ID:
                    new_tweets = twitter_api.search(q=search_query,
                                                    count=TWEETS_PER_QUERY,
                                                    geocode=geocode,
                                                    lang=lang,
                                                    tweet_mode="extended",
                                                    max_id=str(max_id - 1))
                else:
                    new_tweets = twitter_api.search(q=search_query,
                                                    count=TWEETS_PER_QUERY,
                                                    geocode=geocode,
                                                    lang=lang,
                                                    tweet_mode="extended",
                                                    max_id=str(max_id - 1),
                                                    since_id=SINCE_ID)
            if not new_tweets or len(new_tweets) == 0:
                print("No more tweets found")
                break
            else:
                for tweet in new_tweets:
                    if tweet._json['coordinates']:
                        tweets.append(tweet)
                max_id = new_tweets[-1].id
        except tweepy.TweepError as error:
            to_json = json.loads(error.reason.replace("[", "").replace("]", "").replace("'", "\""))
            if to_json["code"] == LIMIT_EXCEEDED_ERROR_CODE:
                print(to_json["message"])
                if key_index == 0:
                    start_time = time()
                if key_index == len(TWITTER_API_KEYS) - 1:
                    key_index = 0
                    remaining_time = 900 - (time() - start_time)
                    minutes, seconds = divmod(remaining_time, 60)
                    print(len(tweets), "tweets found")
                    print("the program will resume in %d minutes and %d seconds" % (minutes, seconds))
                    while remaining_time > 0:
                        sleep(10)
                        remaining_time = 900 - (time() - start_time)
                        minutes, seconds = divmod(remaining_time, 60)
                        if minutes < 0:
                            print("restarting")
                            break
                        else:
                            print("the program will resume in %d minutes and %d seconds" % (minutes, seconds))
                else:
                    print("switching keys")
                key_index += 1
            else:
                print(to_json["message"])
                print(to_json, "--")
                break
    return tweets[:number_tweets]


def plot(center_lat, center_lng, positive_tweets, neutral_tweets, negative_tweets, radius, units, title):
    map_options = GMapOptions(lat=center_lat,
                              lng=center_lng,
                              map_type="roadmap",
                              zoom=3)
    plot = GMapPlot(x_range=Range1d(),
                    y_range=Range1d(),
                    map_options=map_options)
    plot.title.text = title + \
                      " pos:" + str(len(positive_tweets.tweets)) +\
                      " neu:" + str(len(neutral_tweets.tweets)) +\
                      " neg:" + str(len(negative_tweets.tweets))
    plot.api_key = GOOGLE_API_KEY
    conversion_factor_mi_to_m = 1609.334
    conversion_factor_km_to_m = 1000
    if units is "mi":
        new_radius = radius * conversion_factor_mi_to_m
    else:
        new_radius = radius * conversion_factor_km_to_m
    center_point_sr = ColumnDataSource(
        data=dict(
            lat=[center_lat],
            lon=[center_lng]
        )
    )
    center_point = Circle(x="lon",
                          y="lat",
                          size=10,
                          fill_color="red",
                          fill_alpha=1,
                          line_color=None)

    plot.add_glyph(center_point_sr, center_point)

    radius_sr = ColumnDataSource(
        data=dict(
            lat=[center_lat],
            lon=[center_lng]
        )
    )
    radius_circle = Circle(x="lon",
                           y="lat",
                           radius=new_radius,
                           fill_color=None,
                           line_color="red")
    plot.add_glyph(radius_sr, radius_circle)

    source = ColumnDataSource(
        data=dict(
            lat=positive_tweets.latitudes,
            lon=positive_tweets.longitudes
        )
    )
    circle = Circle(x="lon",
                    y="lat",
                    size=10,
                    fill_color=None,
                    line_color="green")
    plot.add_glyph(source, circle)

    source = ColumnDataSource(
        data=dict(
            lat=neutral_tweets.latitudes,
            lon=neutral_tweets.longitudes
        )
    )
    circle = Circle(x="lon",
                    y="lat",
                    size=10,
                    fill_color=None,
                    line_color="black")
    plot.add_glyph(source, circle)

    source = ColumnDataSource(
        data=dict(
            lat=negative_tweets.latitudes,
            lon=negative_tweets.longitudes
        )
    )
    circle = Circle(x="lon",
                    y="lat",
                    size=10,
                    fill_color=None,
                    line_color="red")
    plot.add_glyph(source, circle)
    plot.add_tools(PanTool(), WheelZoomTool())
    output_file("gmap_plot.html")
    show(plot)


def generate_title(search_query, lang=None, geocode=None):
    options = (search_query,)
    folder_name_format = 'sq:%s'
    if lang:
        options += (lang,)
        folder_name_format += ' lang:%s'
    if geocode:
        options += (geocode,)
        folder_name_format += ' geocode:%s'
    return folder_name_format % options


def get_sentiment(tweet):
    analysis = ContentAnalysisModel()
    path = 'dictionaries'
    for infile in glob.glob(os.path.join(path, '*.*')):
        read_file = open(infile, "r")
        file_name = infile.split("/")[1]
        analysis.add_dictionary(file_name=file_name,
                                label=file_name.split(".")[0],
                                content=read_file.read())
    analysis.add_file(file_name=tweet.id,
                      label=tweet.id,
                      content=tweet.content)
    analysis.count()
    analysis._formula = "[positive]-[negative]"
    if analysis.is_secure():
        analysis.generate_scores()
        tweet.sentiment = analysis.scores[0]


def main(search_query, number_tweets, latitude, longitude, radius, units='mi',
         get_new_tweets=True):

    geocode = "%.2f,%.2f,%d%s" % (latitude, longitude, radius, units)
    file_name = generate_title(search_query=search_query,
                               geocode=geocode)
    directory = os.path.join(TWEETS_DIRECTORY, file_name + ".p")
    tweets = Tweets()
    positive_tweets = Tweets()
    neutral_tweets = Tweets()
    negative_tweets = Tweets()
    if os.path.isfile(directory):
        print("loading old tweets")
        tweets = pickle.load(open(directory, "rb"))
    if get_new_tweets:
        print("getting new tweets")
        new_tweets = search_tweets(search_query=search_query,
                                   number_tweets=number_tweets,
                                   geocode=geocode)
        if len(new_tweets):
            print("calculating sentiment")
            for tweet in new_tweets:
                if tweet._json['coordinates'] and tweet._json['id'] not in tweets.ids:
                    new_tweet = Tweet(id=tweet._json['id'],
                                      content=tweet._json['full_text'],
                                      latitude=round(tweet._json['coordinates']['coordinates'][1], 2),
                                      longitude=round(tweet._json['coordinates']['coordinates'][0], 2),
                                      created_at=tweet._json['created_at'])
                    get_sentiment(new_tweet)
                    tweets.tweets.append(new_tweet)
            if not os.path.isdir(TWEETS_DIRECTORY):
                os.mkdir(TWEETS_DIRECTORY)
            print("saving new tweets")
            pickle.dump(tweets, open(os.path.join(directory), "wb"))
    for tweet in tweets.tweets:
        if tweet.sentiment == 0:
            neutral_tweets.tweets.append(tweet)
        elif tweet.sentiment > 0:
            positive_tweets.tweets.append(tweet)
        else:
            negative_tweets.tweets.append(tweet)
    print("plotting", len(tweets.tweets), "tweets")
    plot(center_lat=latitude,
         center_lng=longitude,
         positive_tweets=positive_tweets,
         neutral_tweets=neutral_tweets,
         negative_tweets=negative_tweets,
         radius=radius,
         units=units,
         title=file_name)

def menu():
    answer = ""
    while answer != "3":
        print("\t1. Get new tweets")
        print("\t2. Plot saved tweets")
        print("\t3. Exit")
        answer = input("\tWhat would you like to do? ")
        if answer == "1":
            search_query = input("Search query: ")
            number_tweets = int(input("Number of tweets: "))
            latitude = float(input("latitude: "))
            longitude = float(input("longitude: "))
            radius = int(input("radius: "))
            units = input("units(mi/km): ")
            main(search_query=search_query,
                 number_tweets=number_tweets,
                 latitude=latitude,  # Geocode of the center of US
                 longitude=longitude,
                 radius=radius,
                 units=units  # radius' units (mi or km)
                 )
        elif answer == "2":
            files = os.listdir("Tweets/")
            files = [name.split(".p")[0] for name in files]
            if len(files):
                count = 1
                for file in files:
                    print(str(count) + ".", file)
                index = int(input("Choose a file: ")) - 1
                if index < 0 or index >= len(files):
                    correct = False
                else:
                    correct = True
                while not correct:
                    index = int(input("incorrect option, please try again:")) - 1
                    if index < 0 or index >= len(files):
                        correct = False
                    else:
                        correct = True
                search_query = files[index].split(" ")[0].split(":")[1]
                latitude = float(files[index].split(" ")[1].split(",")[0].split(":")[1])
                longitude = float(files[index].split(" ")[1].split(",")[1])
                radius = int(files[index].split(" ")[1].split(",")[2][0:-2])
                units = files[index].split(" ")[1].split(",")[2][-2:]
                main(search_query=search_query,
                     number_tweets=0,
                     latitude=latitude,  # Geocode of the center of US
                     longitude=longitude,
                     radius=radius,
                     units=units,  # radius' units (mi or km)
                     get_new_tweets=False
                     )
            else:
                print(" there are no tweets saved")
        elif answer != "3":
            print("Invalid choice, try again")


menu()

'''
main(search_query='SpaceX',
     number_tweets=100,
     latitude=39.83,     # Geocode of the center of US
     longitude=-98.58,
     radius=2200,
     units='mi'          # radius' units (mi or km)
)
'''