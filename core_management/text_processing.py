import re
from textblob import TextBlob


# Function to return list of hashtags in a string
def reg_chk(post):
    # returns a pipe separated string of all hashtags present in a string
    return "|".join(re.findall("#[A-Za-z_]+[0-9]*[A-Za-z_]*", post))


def get_stop_words():
    return ['are', 'under', 'by', 'during', 'does', 'y', 'ours', 'own', 'before', 'she', 'myself', 'your', 'this',
            "don't", 'weren', 'be', 'shouldn', 'or', 'into', 'ain', 'their', 'shan', 'and', 'with', 'there', 'because',
            'down', 'here', 'been', "isn't", 'his', 'than', 'about', 'doesn', 'our', 'below', "it's", 's', 'wouldn',
            'theirs', 'its', 'had', 'her', 'did', 'very', 'other', 'only', 've', 'didn', 'while', 'can', 't', 'each',
            'any', 'most', 'but', 'through', 'he', 'won', 'whom', 'not', 'once', 'what', 'no', 'nor', "she's", 'from',
            'up', 'again', 'i', "weren't", 're', "you've", 'where', 'have', "needn't", 'in', 'over', 'above', 'haven',
            "that'll", 'yourself', 'how', 'few', 'against', 'too', 'will', 'more', "aren't", 'who', "shouldn't",
            'having', 'now', 'yourselves', "won't", 'hers', 'so', 'himself', 'mustn', 'has', 'off', "hadn't", 'should',
            'to', "couldn't", 'needn', 'my', 'we', 'the', 'o', 'until', "hasn't", 'itself', 'they', 'those', 'hasn',
            'ourselves', 'were', 'then', 'after', 'for', 'when', 'yours', 'was', 'if', 'as', 'a', 'do', 'that', 'you',
            'these', 'isn', "wasn't", 'is', 'aren', 'mightn', 'hadn', 'd', "you'll", 'just', 'wasn', 'being', "doesn't",
            'it', 'which', "shan't", 'same', 'between', "didn't", 'll', 'them', "should've", 'such', 'at', 'all', 'ma',
            'on', 'me', 'further', 'of', 'him', 'some', "you're", 'm', 'both', 'why', 'doing', 'don', 'herself', 'out',
            "wouldn't", "haven't", "mightn't", 'couldn', "you'd", "mustn't", 'am', 'an', 'themselves', 'us', 'uk',
            'uae', 'keep', 'set', 'new', 'old']

def get_common_words(input_str):
    posts_str = str(input_str)
    # Removed hashtags from posts
    posts_str = re.sub("#[A-Za-z_]+[0-9]*[A-Za-z_]*", "", posts_str)

    # Removed URLS from posts
    posts_str = re.sub(r'http\S+', '', posts_str)

    # Removed Numbers from posts
    posts_str = re.sub(r'\b[0-9]+\b', '', posts_str)
    # Removed punctuations from posts
    # posts_str = posts_str.translate(string.maketrans("", "", string.punctuation))
    # posts_str = posts_str.translate(None, string.punctuation)
    posts_str = re.sub(r'[^\w\s]', ' ', posts_str)

    # stop_words = set(stopwords.words('english'))
    stop_words = get_stop_words()
    # word_tokens = word_tokenize(posts_str)
    word_tokens = posts_str.split(" ")

    # Removed stop-words from posts
    filtered_sentence = [w.strip().lower() for w in word_tokens if w.strip().lower() not in stop_words]

    # Removed words having length upto 2 chars
    filtered_sentence = [word for word in filtered_sentence if len(word) > 3]

    # Counted occurrence of words
    my_dict = {str(i): filtered_sentence.count(i) for i in filtered_sentence}

    # sorted dictionary on highest count
    data_lst = list(my_dict.items())
    data_lst.sort(key=lambda ele: ele[1], reverse=True)

    # Filtered and Formatted top 10 values
    data_lst = [{"word": x[0], "count": str(x[1])} for x in data_lst[:10]]

    return data_lst


def get_most_used_hashtags(input_str):
    data = reg_chk(str(input_str))

    # converted hashtags to list
    filtered_data = data.split("|")

    # created dictionary with the count of hashtags occurrences
    my_dict = {str(i): filtered_data.count(i) for i in filtered_data}
    if "" in my_dict:
        del my_dict[""]

    # sorted dictionary on highest count
    data_lst = list(my_dict.items())
    data_lst.sort(key=lambda ele: ele[1], reverse=True)

    # Filtered and Formatted top 10 values
    data_lst = [{"tag": x[0], "count": str(x[1])} for x in data_lst[:10]]

    return data_lst


def get_word_clouds(input_str):
    posts_str = str(input_str)

    # Removed hashtags from posts
    posts_str = re.sub("#[A-Za-z_]+[0-9]*[A-Za-z_]*", "", posts_str)

    # Removed URLS from posts
    posts_str = re.sub(r'http\S+', '', posts_str)

    # Removed Numbers from posts
    posts_str = re.sub(r'\b[0-9]+\b', '', posts_str)

    # Removed punctuations from posts
    # posts_str = posts_str.translate(string.maketrans("", ""), string.punctuation)
    posts_str = re.sub(r'[^\w\s]', ' ', posts_str)

    # Removed words having length upto 3 from posts
    posts_str = re.sub(r'\b[a-zA-z0-9]{1,3}\b', '', posts_str)

    # stop_words = set(stopwords.words('english'))
    stop_words = get_stop_words()
    # word_tokens = word_tokenize(posts_str)
    word_tokens = posts_str.split(" ")

    # Removed empty string from list
    word_tokens = list([x for x in word_tokens if x != ""])  # removed set
    # Removed stop-words from posts
    filtered_sentence_lst = [w.strip().lower() for w in word_tokens if w.strip().lower() not in stop_words]

    # Re joined list as str
    filtered_sentence = ' '.join(filtered_sentence_lst)

    filtered_sentence = filtered_sentence.replace(r'[ ]+', " ")
    return filtered_sentence


def get_sentiments(input_str):
    if len(input_str) !=0:
        custom_token= get_word_clouds(input_str)
        analysis = TextBlob(custom_token)
        if analysis.sentiment.polarity > 0:
            sentiment_res = 'Positive'
        elif analysis.sentiment.polarity == 0:
            sentiment_res = 'Neutral'
        else:
            sentiment_res = 'Negative'
        sentiment_re= [{"confidence": analysis.sentiment.polarity, "prediction": sentiment_res}]
        return sentiment_re
    else:
        sentiment_re = [{"confidence": 0, "prediction": ""}]
        return sentiment_re


def process_data(input_str, algorithm_type):
    if input_str is not None and algorithm_type is not None:
        try:
            if algorithm_type == "common_words":
                response = get_common_words(input_str)
            elif algorithm_type == "most_used_hashtags":
                response = get_most_used_hashtags(input_str)
            elif algorithm_type == "word_clouds":
                response = get_word_clouds(input_str)
            elif algorithm_type == "sentiment":
                response = get_sentiments(input_str)
            else:
                response= None

            return response
        except:
            return None
    else:
        return None

# print(process_data("my name is #khan and I am not a terrorist", "sentiment"))
