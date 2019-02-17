from .hand import Hand
from .deck import Deck
class Table:
    INIT = 0
    START = 1
    FIRST_TURN = 2
    PLAYER_TURN = 3
    CROUPIER_TURN = 4
    END = 5
    def __init__(self):
        self.game_state = self.INIT 
        self.player_hand = Hand()
        self.croupier_hand = Hand()
        self.deck = Deck()

    def new_game(self):
        self.game_state = self.START         
        self.player_hand.clear()
        self.croupier_hand.clear()
        self.deck.shuffle()
        self.first_turn()
    
    def first_turn(self):
        self.game_state = self.FIRST_TURN
        self.player_hand.add(self.deck.draw())
        self.croupier_hand.add(self.deck.draw())

    def player_turn(self):
        self.game_state = self.PLAYER_TURN

    def hit(self):
        if not (self.game_state == self.PLAYER_TURN):
            return None
        card = self.deck.draw()
        self.player_hand.add(card)
        if self.player_hand.evaluate() > 21 :
            self.game_state = self.END
        return card

    def stand(self):
        if not (self.game_state == self.PLAYER_TURN):
            return False
        self.croupier_turn()
    
    def croupier_turn(self):
        self.game_state = self.CROUPIER_TURN
        again = True
        while again:
            self.croupier_hand.add(self.deck.draw())
            if (self.croupier_hand.evaluate() > 17):
                again = False
        self.game_state = self.END

    def result(self):
        if self.player_hand.evaluate() > 21:
            return [True, False]    
        if self.croupier_hand.evaluate() > 21:
            return [False, True]
        if self.player_hand.evaluate() > self.croupier_hand.evaluate():
            return [False, True]
        elif self.player_hand.evaluate() < self.croupier_hand.evaluate():
            return [True, False]
        else:
            return [False, False]
