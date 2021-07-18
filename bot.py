import tweepy
from datetime import datetime
from secret import consumer_key, consumer_secret, access_token, access_secret, handle
import argparse
import string
import gpt_2_simple as gpt2

"""
This Twitter bot uses OpenAI's 124M GPT-2 model to respond to users. If a user tweets it certain key words,
the randomness in its response will be reflected. For example, if the word frozen is mentioned, it's response randomness
is set to 0 (min), and if coffee is mentioned, it is set to 1.0 (max).
"""
# Bot class
class GPT2Bot:
    def __has_all_credentials(self):
        return consumer_key and consumer_secret and access_token and access_secret and handle

    def __init__(self):
        if not self.__has_all_credentials():
            print("Missing twitter api credential. Make sure to set all credentials in the environment.")
            return

        # get authentication info
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)

        # log into the API
        self.api = tweepy.API(self.auth)
        print('[{}] Logged into Twitter API as @{}\n-----------'.format(
            datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
            handle
        ))

        # set GPT-2 model
        self.model_name = "124M"
        # initiate session
        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess, model_name=self.model_name)

        # string array of words that will trigger the on_status function
        self.trigger_words = ['@' + handle]  # respond to @mentions]

        # dictionary mapping certain words to values of randomness, which will influence response randomness
        self.boltzmann_code = {'frozen': 0.0, 'drowsy': .2, 'tea': .6, 'coffee': .8, 'fire': .9, 'burning': 1.0}

        # cleans bot's responses
        self.text_proc = TextProcessor()


    def stream_response(self):
        # keeps bot running and responds "live" to any tweets mentioning it
        try:
            print("Listening for tweets. Ctl-C to exit streaming mode.")
            streamListener = MyStreamListener(self)
            stream = tweepy.Stream(auth=self.api.auth, listener=streamListener)
            stream.filter(track=self.trigger_words)
        except KeyboardInterrupt:
            print('\nGoodbye')

    def reply_all(self, since_id=None):
        """
        replies to mentions with an ID greater (more recent) than the specified ID.
        Default id is that of bot's most recent tweet.
        :param since_id: int for tweet ID
        """
        # if no id specified, reply to all mentions after most recent tweet by bot
        if not since_id:
            since_id = self.api.user_timeline(id=self.api.me().id, count=1)[0].id

        # replies to all past unseen mentions while bot was not streaming
        mentions = self.api.mentions_timeline(since_id)
        if not mentions:
            print("No new mentions.")
        for mention in mentions:
            # get the text from the tweet mentioning the bot
            message = mention.text
            # remove first word from the tweet
            first_word = message.split(' ', 1)[0].lower()
            # ignores tweet if first word indicates tweet is not directed to bot (just mentions the bot)
            if first_word != '@' + self.api.me().screen_name.lower():
                continue
            self.__respond__(mention)

    def trend_tweet(self):
        # forms message based on number one trend near NYC and tweets it

        # get top trends for NYC
        trends = self.api.trends_place(2459115)[0]['trends']
        # sort by most popular
        trends.sort(key=lambda trend: int(trend['tweet_volume'] or 0), reverse=True)
        top_trend = trends[0]['name'].replace('#', '') + " is"
        # create GPT-2 response mentioning trend
        message = self.form_response(top_trend)
        # clean message for status
        status = self.text_proc.clean_text(message, length=281, delete="\n\n", truncate=True)

        # tweet about top trend
        self.api.update_status(
            status=status
        )

        print("tweeted about " + top_trend)

    def __respond__(self, status):
        # responds to tweet mentioning the bot
        # -------------------
        # log the incoming tweet
        print('[{}] Received: "{}" from @{}'.format(
            datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
            status.text,
            status.author.screen_name
        ))

        # ignores response tweet from bot
        if status.user.id == self.api.me().id:
            return

        # get the text from the tweet mentioning the bot
        message = status.text
        # remove the handle from the tweet
        message = message.split(' ', 1)[1]

        # decide randomness of response based on frequency of boltzmann code words
        boltzmann = self.text_proc.decipher(message, self.boltzmann_code)
        # formulate response
        response = '@' + status.author.screen_name + ' ' + self.form_response(message, temperature=boltzmann)
        # clean response
        response = self.text_proc.clean_text(response, length=281, delete="\n\n", truncate=True)

        # respond to the tweet
        self.api.update_status(
            status=response,
            in_reply_to_status_id=status.id
        )

        print('[{}] Responded to @{}'.format(
            datetime.now().strftime("%H:%M:%S %Y-%m-%d"),
            status.author.screen_name
        ))

    def form_response(self, prefix, length=45, temperature=.7, top_p=.9):
        # generate GPT-2 response with given prefix (text to "inspire" the GPT-2 AI)
        response = gpt2.generate(self.sess, return_as_list=True,
                                 model_name=self.model_name,
                                 prefix=prefix,
                                 length=45,
                                 temperature=0.7,
                                 top_p=0.9,
                                 include_prefix=True
                                 )[0]
        return response
    
    def basic_test(self, message):
        # generate response to given message with default settings
        boltzmann = self.text_proc.decipher(message, self.boltzmann_code)
        # formulate response
        response = self.form_response(message, temperature=boltzmann)
        # clean response
        response = self.text_proc.clean_text(response, length=281, chars_to_remove=['"'], truncate=True)
        return response

# override the default listener to add code to on_status
class MyStreamListener(tweepy.StreamListener):
    # listener for tweets
    # -------------------
    def __init__(self, bot):
        """
        :param bot: GPT2Bot object
        """
        super().__init__()
        self.bot = bot

    # this function will be called any time a tweet comes in
    # that contains words from bot.trigger_words()
    def on_status(self, status):
        self.bot.__respond__(status)

class TextProcessor:
    def clean_text(self, text, length=False, chars_to_remove=None, truncate=False):
        """
        Processes given text string according to other parameters
        :param text: string to be processed
        :param length: desired length to shorten text to
        :param chars_to_remove: list of characters to remove from text
        :param truncate: if set to True, removes trailing comma and other preposition-like words from end of text
        :return: new_text, a string representing the processed text
        """
        new_text = text
        # remove given chars
        for char in chars_to_remove:
            new_text = new_text.replace(char, '')

        # replace double lines with single lines
        new_text = new_text.replace('\n\n', '\n')

        # shorten response to last full sentence (ending with period)
        idx_last_period = new_text.rfind(".")
        if idx_last_period != -1: # period found
            new_text = new_text[:idx_last_period+1]

        # shorten sentence if possible
        if length < len(new_text):
            new_text = new_text[:length - 1]
            print('truncated response length to: ', len(new_text))
            
        return new_text

    def decipher(self, text, code):
        """
        Returns boltzmann numbers if either of secret_words is present in text
        :param code: dictionary mapping code words to their boltzmann (randomness) values
        :param text: string
        :return: boltzmann number average for all keys in code that are also in text. If no keys present in text,
        returns None
        *Note: function ignores punctuation, so punctuation cannot be encoded in code*
        """
        # remove capitalization to search for words
        text.lower()
        # remove any punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # get words to search for in text
        secret_words = code.keys()
        # check if text contains any secret words and collect their boltzman values
        boltzmanns = []
        for word in text.split():
            if word in secret_words:
                boltzmanns.append(code[word])
        # return None if no code words in text
        if len(boltzmanns) == 0:
            return None
        # return boltzmann average value for code words present
        else:
            avg = sum(boltzmanns) / float(len(boltzmanns))
            return avg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="To stream or not to stream")
    parser.add_argument("-u", help="respond to previous unanswered tweets", action="store_true", default=False)
    parser.add_argument("-n", help="tweet about top trend near NYC", action="store_true", default=False)
    parser.add_argument("-l", help="listen and respond to live tweets", action="store_true", default=False)
    parser.add_argument("-t","--test", nargs="+", help="test response to given message. Does not send tweet.", default=[])
    args = parser.parse_args()
    old_resp = args.u
    top_trend = args.n
    to_stream = args.l
    test_words = args.test
   
    all_flags_false = not(old_resp or top_trend or to_stream or test_words)
    if all_flags_false:
        print("Please give an argument to run the bot. Run -h to see options.")
    else:
        mybot = GPT2Bot()
        if test_words:
            test_phrase = "".join(test_words)
            response = mybot.basic_test(test_phrase)
            print(response)
        if old_resp:
            # since_id = tweet id found after /status/ in url
            mybot.reply_all()
        if top_trend:
            mybot.trend_tweet()
        if to_stream:
            mybot.stream_response()




