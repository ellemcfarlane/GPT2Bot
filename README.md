# GPT-2 Bot
Interact with this bot on Twitter [here](https://twitter.com/Gpt2B). It uses OpenAI's 124M GPT-2 model to formulate responses.

The randomness of its response is influenced by certain, secret words...

For example, if the word frozen is mentioned, its response randomness is set to 0 (min), and if coffee is mentioned, it is set to 1.0 (max).

![Alt_text](screenshots/gpt2botscreenshot.png)
![Alt_text](screenshots/gpt2bottweetsceenshot.png)

### Basic Usage from Terminal
* Installation:
   * use python 3.7
   * ```pip install requirements.txt```

* run:  
    ```python bot.py -{flags}```  
    flags options  
    * -u to respond to old tweets the bot did not see while offline 
    * -n to tweet about top trend near NYC
    * -l to run bot "live" to respond to new incoming tweets
    * -t {message} to test bot's response to given message
