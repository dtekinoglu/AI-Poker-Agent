from pypokerengine.players import BasePokerPlayer
import handprobability as handProb
import random as rand
import opponent_action_logistic_regression as oa

# IDEA: Rip off angela's agent and see if it works.
ROUND_ENUM = {'preflop': 0, 'flop': 1, 'turn': 2, 'river': 3}

# Checkmate the raise player >:)
Anti_Raise_Player = {'raise': 0, 'call': 0, 'fold': 0, 'uuid': ''}

# Random number generator
class LCG:
    def __init__(self, seed):
        self.seed = seed
        self.a = 1103515245
        self.c = 12345
        self.m = 2**32

    def next(self):
        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed / self.m

class EvilPlayerJr(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        # WEIGHTS:
        TRIFOLD_0 = .75
        TRIFOLD_1 = .2
        TRIFOLD_2 = .8
        TRIFOLD_3 = .9
        
        BAD_HAND = 1
        MID_HAND = 7

        SUIT_CALL = .5
        NUMBER_CALL = .5
        HIGH_CALL = .75

        # Consistent yet random bluff factor for each round
        lcg = LCG(round_state['round_count'])

        # Trainable bluff factor (DO NOT TRAIN)
        threshold = .00
        do_bluff = lcg.next() <= threshold

        ROUND = round_state['street']
        ROUND_NUM = ROUND_ENUM[round_state['street']]

        sample = rand.uniform(0,1)

        # Detect Raise
        parsed_history = []
        action_histories = round_state['action_histories']
        curr_round = action_histories[ROUND]
        parsed_history = [x['action'].lower() for x in curr_round if x['action'] == 'RAISE' or x['action'] == 'CALL' or x['action'] == 'FOLD']
        parsed_uuid = [x['uuid'].lower() for x in curr_round]

        # Get new UUID if available
        if len(curr_round):
            parsed_uuid = curr_round[-1]['uuid']
        else:
            parsed_uuid = Anti_Raise_Player['uuid']

        # Detect new game
        if Anti_Raise_Player['uuid'] != parsed_uuid:
            Anti_Raise_Player['raise'] = 0
            Anti_Raise_Player['call'] = 0
            Anti_Raise_Player['fold'] = 0
            Anti_Raise_Player['uuid'] = parsed_uuid

        # Calculate opponent move if known 
        if len(parsed_history):
            Anti_Raise_Player[parsed_history[-1]] += 1

        # Train sample cuttoffs
        def trifold():
            if do_bluff:
                return 'raise'
            elif ROUND_NUM == 0:
                return 'fold' if sample > TRIFOLD_0 else 'call'
            elif ROUND_NUM == 1:
                return 'fold' if sample > TRIFOLD_1 else 'call'
            elif ROUND_NUM == 2:
                return 'fold' if sample > TRIFOLD_2 else 'call'
            elif ROUND_NUM == 3:
                return 'fold' if sample > TRIFOLD_3 else 'call'
            else:
                return 'fold'

        # Determine which move to make given the desired choice
        def move(move):
            if move == 'fold':
                move = trifold()

            if move in valid_actions:
                return move
            else:
                return 'call'

        if round_state['street'] != 'preflop':
            handOdds = handProb.handDistribution(hole_card, round_state['community_card'], 50, 1)['with_hole']
            handKeys = list(handOdds.keys())
            handOddsList = []

            for hand in handKeys:
                handOddsList.append(handOdds[hand])
            handOddsList.reverse()

            # Hand distribution decider (weight)
            bad_hand = BAD_HAND
            mid_hand = MID_HAND
            if sum(handOddsList[bad_hand:mid_hand]) >= 1:
                return move('call')
            elif sum(handOddsList[mid_hand:10]) >= 1:
                return move('raise')
            return move('fold')
        
        # Good hands
        if round_state['street'] == 'preflop':
            # Suit
            if hole_card[0][0] == hole_card[1][0]:
                if sample <= SUIT_CALL:
                    return move('call')
                return move('raise')

            # Number
            if hole_card[0][1] == hole_card[1][1]:
                if sample <= NUMBER_CALL:
                    return move('call')
                return move('raise')
            
            # High Card
            if hole_card[0][1] in ['T', 'J', 'Q', 'K', 'A'] or hole_card[1][1] in ['T', 'J', 'Q', 'K', 'A']:
                if sample <= HIGH_CALL:
                    return move('call')
                return move('raise')
        
        return move('fold')

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
  return EvilPlayerJr()
