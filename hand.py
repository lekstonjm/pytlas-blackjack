class Hand:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def evaluate(self):
        test_count = 0
        value = 0
        test_again = True
        while test_again:
            ace_count = test_count
            test_count += 1
            test_again = False
            for card in self.cards:                    
                if card.is_ace:
                    if ace_count > 0:
                        value += 1
                        ace_count -= 1
                    else:
                        value += 11
                        test_again = True
        return value

    def clear(self):
        self.cards = []

    def __str__(self):
        msg = ''
        delimiter = ""
        for card in self.cards:
            msg += delimiter + str(card)
            delimiter = ", "
        return msg 

    def i18n(self, req):
        msg = ''
        delimiter = ""
        for card in self.cards:
            msg += delimiter + card.i18n(req)
            delimiter = ", "
        return msg