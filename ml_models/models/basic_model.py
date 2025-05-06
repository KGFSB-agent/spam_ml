import re

class BasicSpamModel:
    def __init__(self):
        self.keywords = [
        'buy now', 'free', 'won', 'prize', 'congratulations',
        'urgent', 'only today', 'discount', 'guarantee',
        'limited time', 'offer', 'deal', 'click here', 
        'credit', 'loan', 'money', 'profit', 'save',
        'special promotion', 'apply now', 'call now', 
        'winner', 'selected', 'claim', 'bonus'
    ]
        
    def predict(self, text: str) -> bool:
        text_lower = text.lower()
        return any(re.search(rf'\b{kw}\b', text_lower) for kw in self.keywords)

    @property
    def cost(self):
        return 100
