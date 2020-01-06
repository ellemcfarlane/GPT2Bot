# GPT-2 Bot
Interact with this bot on Twitter [here](https://twitter.com/Gpt2B). It uses GPT-2 to formulate response.

The randomness of its response is influenced by certain, secret words...

For example, if the word frozen is mentioned, it's response randomness is set to 0 (min), and if coffee is mentioned, it is set to 1.0 (max).

![Alt_text](screenshots/gpt2botscreenshot.png)
![Alt_text](screenshots/gpt2bottweetsceenshot.png)

### Basic Usage
* Ensure to have the basic requirements via: pipenv install
* run bot.py -o -s from shell
    * include -o to respond to old tweets the bot did not see while offline 
    * include -s to run bot "live" to respond to new incoming tweets
