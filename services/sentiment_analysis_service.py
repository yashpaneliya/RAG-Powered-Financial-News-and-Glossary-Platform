from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from core.logger import logger

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    """
    Analyzes sentiment for a given text using VADER.
    Returns 'positive', 'neutral', or 'negative'.
    """
    try:
        if not text or text.strip() == "":
            return "neutral"
        
        scores = analyzer.polarity_scores(text)
        compound_score = scores["compound"]

        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        return 'neutral'
    
if __name__ == '__main__':
    text = """Gold prices reached a record high of USD 3,128.06 per ounce amid tariff concerns and economic uncertainty. Investor sentiment is shifting towards safe-haven assets like gold due to fears of a recession and anticipated Federal Reserve rate cuts."""
    sentiment = analyze_sentiment(text)
    print(sentiment)