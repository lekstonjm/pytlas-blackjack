from pytlas import intent, training, translations
import random
# This entity will be shared among training data since it's not language specific


en_figures = ['as','2','3','4','5','6','7','8','9','10','jack','queen','king']
en_colors = ['clubs','diamonds', 'hearts','spades']


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
  let's play blackjack
  I want play blackjack

%[blackjack/draw]
  draw a card
  give me a card
  one card please

%[blackjack/end_of_turn]
  that's all
  it's ok for me

%[blackjack/list_player_hand]
  show my hand
  list my hand

%[blackjack/done]
  I quit the table
  bye
"""


deck = []
player_hand = []
bank_hand = []
end_of_turn = False
player_won = False

def new_turn():
  global player_hand
  global bank_hand
  global end_of_turn
  global player_won
  player_hand = []
  bank_hand = []
  end_of_turn = False
  player_won = False
  shuffle()

def shuffle():
  global deck
  values = [1,2,3,4,5,7,7,8,9,10,10,10,10]
  for color in en_colors: 
    for index in range(0,len(en_figures)): 
      value = values[index]
      deck.append( {'value': value, 'figure' : en_figures[index], 'color' : color })
  counter = len(deck)
  while counter > 0:
    index = random.randint(0, counter - 1)
    temp = deck[index]
    deck[index] = deck[counter - 1]
    deck[counter-1] = temp
    counter = counter - 1

def draw():
  global deck 
  card = deck[0]
  deck = deck[-(len(deck)-1):]
  return card

def has_card():
  global deck 
  if (len(deck) > 0):
    return True
  return False

def add_hand(hand, card):
  hand.append(card)  

def evaluate_hand(hand):
  value = 0
  for card in hand:
    value = value + card['value']
  return value

@intent('help_blackjack')
def on_help_blackjack(req):
  req.agent.answer(req._(help_en))
  return req.agent.done()

@intent('play_blackjack')
def on_play_blackjack(req):
  global player_hand
  req.agent.context('blackjack')
  new_turn()
  card = draw()  
  add_hand(player_hand, card)
  req.agent.answer(req
    ._('Here is your first card: {0} of {1}')
    .format(req._(card['figure']), req._(card['color']))
  )
  return req.agent.done()

def ask_new_turn(req):
    new_game = req.intent.slot('new_game').first().value
    yes = req._('Yes')
    no = req._('No')
    if not new_game:
      return req.agent.ask('new_game', req._('would you like start a new game') , [yes, no])
    if new_game == yes:
      return on_play_blackjack(req)
    else:
      return on_blackjack_done(req)

@intent('blackjack/draw')
def on_blackjack_draw(req):
  global player_hand
  global end_of_turn

  if end_of_turn:
    return ask_new_turn(req)

  if (not has_card()):
    end_of_turn = True
    req.agent.answer(req._('No more card.'))
    return req.agent.done()
  card = draw()  
  add_hand(player_hand, card)
  value = evaluate_hand(player_hand)
  msg = req._('This is a {0} of {1}').format(req._(card['figure']), req._(card['color']))
  if value > 21:
    msg = msg + '\n' + req._('You lost')
    end_of_turn = True
  req.agent.answer(msg)
  return req.agent.done()


@intent('blackjack/end_of_turn')
def on_end_of_turn(req):
  global bank_hand
  global player_hand
  global end_of_turn
  global player_won

  if end_of_turn:
    return ask_new_turn(req)

  end_of_turn = True
  again = True
  while again:
    if not has_card():
      player_won = True
      again = False
    card = draw()
    add_hand(bank_hand,card)
    croupier_value = evaluate_hand(bank_hand)
    player_value = evaluate_hand(player_hand)
    if croupier_value > 21:
      again = False
      player_won = True
    elif croupier_value > player_value:
      again = False 
      player_won = False
  msg = req._('Bank hand contains:')
  for card in bank_hand:
    msg = msg + '\n' + req._('- {0} of {1}').format(req._(card['figure']), req._(card['color']))
  msg = msg + '\n'
  if player_won:
    msg = msg + req._('You won')
  else:
    msg = msg + req._('You lost')  
  req.agent.answer(msg)  
  return req.agent.done()

@intent('blackjack/list_player_hand')
def on_list_player_hand(req):
  global player_hand
  msg = req._('Your hand contains:')
  for card in player_hand:
    msg = msg + req._('\n- {0} of {1}').format(req._(card['figure']), req._(card['color']))
  req.agent.answer(msg)
  return req.agent.done()

@intent('blackjack/done')
def on_blackjack_done(req):
  req.agent.context(None)
  req.agent.answer(req._('Of course.\nHave a good day.'))
  return req.agent.done()

@intent('blackjack/__fallback__')
def on_blackjack_fallback(req):
  req.agent.answer(req._('What would you like to do?'))
  return req.agent.done()