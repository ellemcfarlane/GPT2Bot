import string
def clean_text(text, length=False, delete='', truncate=False):
    """
    Processes given text string according to other parameters
    :param text: string to be processed
    :param length: desired length to shorten text to
    :param delete: characters to remove from text
    :param truncate: if set to True, removes trailing comma and other preposition-like words from end of text
    :return: newText, a string representing the processed text
    """
    newText = text
    truncateWords = ['and', 'but', 'the', 'is']
    # replace word given by delete
    if delete != '':
        text.replace(delete, '')
    # remove trailing commas and words in truncateWords from the end
    if truncate:
        newText = text.split()
        if newText[-1] in truncateWords:
            del newText[-1]
        if newText[-1][-1] == ',':
            newText[-1] = newText[-1].replace(',', '.')
        newText = " ".join(newText)
    # shorten sentence if possible
    if length < len(newText):
        newText = newText[:length-1]
        print('truncated response length to: ', len(newText))
    return newText

def decipher(text, code):
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
    # set randomness for first word to .3, and second to 1
    boltzmanns = []
    # check if text contains any secret words and set randomness b1 and b2 accordingly
    for word in text.split():
        if word in secret_words:
            boltzmanns.append(code[word])

    # return None if no code words in text
    if len(boltzmanns) == 0:
        return None
    # return boltzmann average value for code words present
    else:
        avg = sum(boltzmanns)/float(len(boltzmanns))
        return avg

# cd = {'drowsy': .2, 'frozen': 0.0, 'speed': 1.0, 'coffee': .8, 'fire': .9}
# text = "are you feeling drowsy!? coffee. .or.guilty"
# print(text.translate(str.maketrans('', '', string.punctuation)))
# print(decipher(text, cd))


