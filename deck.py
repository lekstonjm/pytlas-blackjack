from .card import Card
import random


class Deck:
    def __init__(self):
        self.cards = []

    def shuffle(self):
        figures = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        colors = ['clubs','diamonds', 'hearts','spades']
        values = [1,2,3,4,5,6,7,8,9,10,10,10,10]
        for color in colors: 
            for index in range(0,len(figures)):                 
                value = values[index]
                figure = figures[index]
                card = Card(color, figure, value)
                self.cards.append(card)
                counter = len(self.cards)
                while counter > 0:
                    index = random.randint(0, counter - 1)
                    temp = self.cards[index]
                    self.cards[index] = self.cards[counter - 1]
                    self.cards[counter-1] = temp
                    counter = counter - 1

    def draw(self):
        card = self.cards[0]
        self.cards = self.cards[-(len(self.cards)-1):]
        return card

