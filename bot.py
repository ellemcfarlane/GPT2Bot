import tweepy
from datetime import datetime
from secret import consumer_key, consumer_secret, access_token, access_secret, handle
import response_logic as gpt
import process_text as pt

"""
This Twitter bot uses OpenAI's GPT-2 text generation model to respond to users. If a user tweets it certain key words,
the randomness in its response will be reflected. For example, if the word frozen is mentioned, it's response randomness
is set to 0 (min), and if coffee is mentioned, it is set to 1.0 (max).
"""

# get authentication info
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

# log into the API
api = tweepy.API(auth)
print('[{}] Logged into Twitter API as @{}\n-----------'.format(
    datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
    handle
))

# string array of words that will trigger the on_status function
trigger_words = ['@' + handle]  # respond to @mentions]

# dictionary mapping certain words to values of randomness, which will influence response randomness
boltzmann_code = {'drowsy': .2, 'frozen': 0.0, 'speed': 1.0, 'coffee': .8, 'fire': .9}

# load GPT2 Model for responses
gpt.loadModel()

# override the default listener to add code to on_status
class MyStreamListener(tweepy.StreamListener):

    # listener for tweets
    # -------------------
    # this function will be called any time a tweet comes in
    # that contains words from the array created above
    def on_status(self, status):

        # log the incoming tweet
        print('[{}] Received: "{}" from @{}'.format(
            datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
            status.text,
            status.author.screen_name
        ))

        # ignores response tweet from bot
        if status.user.id == api.me().id:
            return

        # get the text from the tweet mentioning the bot
        message = status.text
        # remove the handle from the tweet
        message = message.split(' ', 1)[1]

        # decide randomness of response based on frequency of boltzmann code words
        boltzmann = pt.decipher(message, boltzmann_code)
        # formulate response
        response = '@' + status.author.screen_name + ' ' + gpt.getAnswer(message, temperature=boltzmann)
        # clean response
        response = pt.clean_text(response, length=200, delete="\n\n", truncate=True)

        # respond to the tweet
        api.update_status(
            status=response,
            in_reply_to_status_id=status.id
        )

        print('[{}] Responded to @{}'.format(
            datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
            status.author.screen_name
        ))

# create a stream to receive tweets
try:
    streamListener = MyStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=streamListener)
    stream.filter(track=trigger_words)
except KeyboardInterrupt:
    print('\nGoodbye')