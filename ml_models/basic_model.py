import re

class BasicSpamModel:
    def __init__(self):
        self.keywords = [
            'купите', 'бесплатно', 'выиграли', 'приз', 
            'срочно', 'только сегодня', 'акция', 'гарантия'
        ]
        
    def predict(self, text: str) -> bool:
        text_lower = text.lower()
        return any(re.search(rf'\b{kw}\b', text_lower) for kw in self.keywords)

    @property
    def cost(self):
        return 100
