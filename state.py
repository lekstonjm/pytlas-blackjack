import abc
from .hand import Hand
from .deck import Deck

class State(object, meta=abc.ABCMeta):
    @abc.abstractmethod
    def new_game(self, game, req):
        raise NotImplementedError('')
    @abc.abstractmethod
    def hit(self, game, req):
        raise NotImplementedError('')
    @abc.abstractmethod
    def stand(self, game, req):
        raise NotImplementedError('')
    @abc.abstractmethod
    def list_hand(self, game, req):    
        raise NotImplementedError('')

class Init(State):
    pass
class Game(object):
    def __init__(self):
        self.player_hand = Hand()
        self.bank_hand = Hand()
        self.deck = Deck()
        self.state = Init()
        



class Basic(State):
    def new_game(self, game, req):
        game.deck.shuffle()
        game.player_hand.clear()
        game.croupier_hand.clear()
        req.agent.answer(req._('Let\'s start'))
        card = game.deck.draw()
        if card.is_ace:
            game.state = SelectAceValue()
        req.agent.answer(req._('Croupier draw {0}').format(req._(game.table.croupier_hand)))
        req.agent.answer(req._('Player got {0}').format(req._(game.table.player_hand)))
        req.agent.answer(req._('Hit or stand ?'))
        return req.agent.done()
    def hit(self, game, req):
        req.agent.answer(req._('You cannt do it now'))
        return req.agent.done()
    def stand(self, game, req):
        req.agent.answer(req._('You cannt do it now'))
        return req.agent.done()
    def list_hand(self, game, req):
        msg = req._('Your hand contains:')
        for card in game.table.player_hand:
            msg = msg + req._('\n- {0} of {1}').format(req._(card['figure']), req._(card['color']))
        req.agent.answer(msg)
        return req.agent.done()




class SelectAceValue(Defaut):
    def hit(self, game, req):
        ace_value = req.intent.slot('ace_value').first().value
        one = req._('1')
        if not ace_value:
            return req.agent.ask('ace_value', req._('you just drawn an ace, please choose its value') , [one, eleven])
        if ace_value == one:
            game.card_drawn['value'] = 1
        else:
            game.card_drawn['value'] = 10


class PlayerTurn(Defaut):
    def hit(self, game, req):
        card = game.table.hit()
        if card.is_ace:
            game.card_drawn = card
            one = req._('1')
            eleven = req._('11')
            game.state = SelectAceValue()
            return req.agent.ask('ace_value', req._('you just drawn an ace, please choose its value') , [one, eleven])




