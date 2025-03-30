import re
from nltk.corpus import stopwords
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from rake_nltk import Rake

def preprocess_user_query(query: str):
    """
    Preprocess the user query:
    - Tokenize the query into words
    - Remove stopwords
    - Return a cleaned list of keywords
    """
    stop_words = set(stopwords.words('english'))

    # tokenize & remove sepcial chars the query
    words = word_tokenize(query.lower())
    words = [re.sub(r'\W+', '', word) for word in words]
    keywords = [word for word in words if word not in stop_words and word != '']

    return keywords


def keyword_extraction(query: str):
    rake = Rake()
    rake.extract_keywords_from_text(query)
    keywords = rake.get_ranked_phrases()
    return keywords


if __name__ == "__main__":
    print(keyword_extraction("What is the meaning of Hedging?"))
