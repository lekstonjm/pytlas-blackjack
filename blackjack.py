import intent, training, translations

import random

class Card(object):
    def __init__(self, color, figure, value):
        self.color = color
        self.figure = figure
        self.value = value
        self.is_ace = False
        if self.figure == 'ace':
            self.is_ace = True

    def __str__(self):
        return '{0} of {1}'.format(self.figure, self.color)

class Shoe(object):
    def __init__(self):
        self.figures = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        self.colors = ['clubs','diamonds', 'hearts','spades']
        self.values = [1,2,3,4,5,6,7,8,9,10,10,10,10]
        self.cards = []
    
    def create(self, shoe_number):
        for _packet_index in range(shoe_number):
            for color in self.colors: 
                for index in range(0,len(self.figures)):                 
                    value = self.values[index]
                    figure = self.figures[index]
                    card = Card(color, figure, value)
                    self.cards.append(card)

    def shuffle(self):
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

class Hand(object):
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

class Game(object):
  # game state
  START = 0
  NEW_TURN = 1
  BEGIN_OF_TURN = 2
  PLAYER_FIRST_ACTION = 3
  PLAYER_ACTIONS = 4
  DEALER_ACTIONS = 5
  END_OF_TURN = 6
  #player action
  HIT = 0
  STAND = 1
  DOUBLE = 2
  SPLIT = 3
  RETRY = 4
  INSURANCE = 6
  BET = 7
  HELP = 8

  def __init__(self):
    self.blackjack_odds = 3/2
    self.standard_odds = 1
    self.state = self.START 
    self.player_action = None
    self.player_money = 100
    self.player_bet = 0
    self.player_double = False
    self.player_hit_counter = 0
    self.player_insurance = None
    self.player_hand = Hand()
    self.dealer_hand = Hand()
    self.shoe = Shoe()
  
  def start(self, req):
    number_of_packets = req.intent.slot('number_of_packets').first().value
    if not number_of_packets:
      number_of_packets = 1 
      self.shoe.create(number_of_packets)      
    req.agent.answer(req._('Welcome in blackjack game'))
    req.agent.answer(req._('A shoe containing {0} packets has been shuffled').format(number_of_packets))
    req.agent.answer(req._('You start with 100$  ships'))
    self.player_bet = None
    self.player_action = None
    self.state = self.NEW_TURN
    return None

  def new_turn(self, req):
    self.player_double = False
    self.player_action_counter = 0
    self.player_insurance = None
    self.player_bet = req.intent.slot('player_bet').first().value    
    if not self.player_bet:
      return req.agent.ask('player_bet', req._('What is your bet?'))
    self.player_money -= self.player_bet
    self.state = self.BEGIN_OF_TURN
    return None

  def begin_of_turn(self, req):
    self.player_hand.add(self.shoe.draw())
    self.player_hand.add(self.shoe.draw())
    self.dealer_hand.add(self.shoe.draw())
    req.agent.answer(req._('You got a {0} and a {1}').format(req._(self.player_hand.cards[0]), req._(self.player_hand.cards[1])))
    req.agent.answer(req._('dealer got a {0} and a face down card').format(req._(self.dealer_hand.cards[0])))
    self.state = self.PLAYER_FIRST_ACTION
    return req.agent.done()

  def player_first_action(self, req):
    if self.player_action == self.DOUBLE:
      self.player_double = True
      self.player_action = self.HIT        
    self.state = self.PLAYER_ACTIONS
    return None

  def player_actions(self, req):
    if self.player_action == self.HIT:
      self.player_hand.add(self.shoe.draw())
      self.player_hit_counter++    
      req.agent.answer(req._('Your got a {0}').format(req._(self.player_hand.cards[self.player_hand.cards.count - 1])))

      if  self.player_hand.evaluate() > 21:
        self.state = self.END_OF_TURN
      elif self.player_hand.evaluate() == 21 or (self.player_double and self.player_hit_counter >= 3):
        self.state = self.DEALER_TURN

    elif self.player_action == self.STAND:
      self.state = self.DEALER_TURN
    else:
      return on_blackjack_help(req)
    return None
  
  def dealer_actions(self, req):
    again = True
    while again:
        self.dealer_hand.add(self.shoe.draw())
        req.agent.answer(req._('dealer got a {0}').format(req._(self.dealer_hand.cards[self.dealer_hand.cards.count - 1])))      
        if self.dealer_hand.evaluate() > self.player_hand.evaluate() or self.dealer_hand.evaluate() > 17:
            again = False
    self.state = self.END_OF_TURN
    return None

  def end_of_turn(self, req):
    if self.player_hand.evaluate() > 21:
      req.agent.answer(req._('Unfortunately! your hand is over 21. You lost'))
    elif self.dealer_hand.evaluate() > 21:
      req.agent.answer(req._('Congratulation! dealer hand is over 21. You won'))
      self.player_money += self.player_bet * 2        
    elif self.player_hand.evaluate() == self.dealer_hand.evaluate():
      req.agent.answer(req._('Tie, no one won'))
    elif self.player_hand.evaluate() == 21:
      req.agent.answer(req._('Blackjack! You won'))
      self.player_money += self.player_bet * 3/2        
    elif self.player_hand.evaluate() > self.dealer_hand.evaluate():
      req.agent.answer(req._('Congratulation! You won.'))
      self.player_money += self.player_bet * 2        
    elif self.player_hand.evaluate() < self.dealer_hand.evaluate():
      req.agent.answer(req._('Unfortunately! You lost'))
    else:
      req.agent.answer(req._('Tie'))
    req.agent.answer(req._('Bet for a new turn'))
    self.state = self.NEW_TURN
    return req.agent.done()


  def apply_rule(self, req):
    while(true):
      if self.state == self.START:
        ret = self.start(req)
      elif self.state == self.NEW_TURN:
        ret = self.new_turn(req)
      elif self.state == self.WAIT_NEW_TURN:
        ret = self.wait_for_new_turn(req)
      elif self.state == self.BEGIN_OF_TURN:
        ret = self.begin_of_turn(req)
      elif self.state == self.PLAYER_FIRST_ACTION:
        ret = self.player_first_action(req)
      elif self.state == self.PLAYER_ACTIONS:
        ret = self.player_actions(req)
      if self.state == self.DEALER_TURN:
        ret = self.dealer_actions(req)      
      if self.state == self.END_OF_TURN:
        ret = self.end_of_turn(req)          

# This entity will be shared among training data since it's not language specific

help_en="""
Let's play blackjack
"""

@training('en')
def en_data(): return """
%[help_blackjack]
  how does blackjack skill work
  give me help on blackjack skill
  what is blackjack skill

%[play_blackjack]
  I want play blackjack
  let's play blackjack
  play blackjack with @[number_of_packets] packets

%[blackjack/hit]
  hit

%[blackjack/stand]
  stand

%[blackjack/double]
  double

%[blackjack/]
@[number_of_packets](type=int)
  1
  2
  3
  4
"""
game = Game()

@intent('help_blackjack')
def on_help_blackjack(req):
  req.agent.answer(req._('general help'))
  return req.agent.done()

@intent('play_blackjack')
def on_play_blackjack(req):
  req.agent.context('blackjack')
  global game
  return game.apply_rule(req)

@intent('blackjack/hit')
def on_hit(req):
  global game
  game.player_action = game.HIT
  return game.apply_rule(req)

@intent('blackjack/stand')
def on_stand(req):
  global game
  game.player_action = game.STAND
  return game.apply_rule(req)

@intent('blackjack/double')
def on_double(req):
  global game
  game.player_action = game.DOUBLE
  return game.apply_rule(req)

@intent('blackjack/split')
def on_split(req):
  global game
  game.player_action = game.SPLIT
  return game.apply_rule(req)

@intent('blackjack/bet')
def on_bet(req):
  global game
  game.player_action = game.BET
  return game.apply_rule(req)

@intent('blackjack/help')
def on_help(req):
  global game
  game.player_action = game.HELP
  return game.apply_rule(req)

@intent('blackjack/quit')
def on_quit(req):
  req.agent.context(None)
  req.agent.answer(req._('Goodbye'))
  return req.agent.done()