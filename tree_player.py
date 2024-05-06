from pypokerengine.players import BasePokerPlayer
import gametree as gt
import timeit
import opponent_action_logistic_regression
import handprobability as hp

oa = opponent_action_logistic_regression.OpponentAction()

labels = {
    'raise': 0, 
    'call': 1, 
    'fold': 2,
    '': 3
}

class TreePlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    # Get action history
    parsed_history = []
    action_histories = round_state['action_histories']
    curr_round = round_state['street']
    parsed_history = [x['action'].lower() for x in action_histories[curr_round] if x['action'] == 'RAISE' or x['action'] == 'CALL' or x['action'] == 'FOLD']

    # Opponent UUID
    if len(action_histories[curr_round]):
      opponent_uuid = action_histories[curr_round][-1]['uuid']
    else:
      opponent_uuid = ''
    
    # Opponent and personal betting
    opponent_bets = 0
    my_bets = 0
    if opponent_uuid != '':
      for round in action_histories.keys():
        for action in action_histories[round]:
          if action['uuid'] == opponent_uuid:
            try:
              opponent_bets += action['add_amount']
            except:
              try:
                opponent_bets += action['paid']
              except:
                opponent_bets += 0
          else:
            try:
              my_bets += action['add_amount']
            except:
              try:
                my_bets += action['paid']
              except:
                my_bets += 0

    # Community card Value
    handOdds = hp.handDistribution(hole_card, round_state['community_card'], 50, 1)['with_hole']
    handKeys = list(handOdds.keys())
    handOddsList = []
    for hand in handKeys:
        handOddsList.append(handOdds[hand])
    handOddsList.reverse()
    community_value = handOddsList.index(2)

    # Opponent last action
    labels = {
      'fold': 0,
      'call': 1,
      'raise': 2
    }
    action_prob_arrary = [0, 0, 0]
    try:
      opponent_last_action = parsed_history[-1]
      action_prob_arrary[labels[opponent_last_action]] = 1
      oa.update(community_cards=community_value, op_bet=opponent_bets, my_bet=my_bets, action=action_prob_arrary)
    except:
      opponent_last_action = ''

    pot = round_state['pot']['main']['amount'] + sum(map(lambda x: x['amount'], round_state['pot']['side']))
    tree = gt.LimitPokerTree(hole_cards=hole_card, community_cards=round_state['community_card'], history=parsed_history, pot=pot, opponent_Action=oa)
    tree.build_tree()
    action_choice = tree.getNodeAction()
    if action_choice == 'call':
      my_bets += 10
    elif action_choice == 'raise':
      my_bets += 20
    
    # oa.predict(community_cards=community_value, op_bet=opponent_bets, my_bet=my_bets)
    return action_choice

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

def setup_ai():
  return TreePlayer()
