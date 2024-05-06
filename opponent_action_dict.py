
# The agent’s action,
# denoted by a, is determined by the current round state. Each state of the game
# consists of four components:
# 1. The private cards visible to the player.
# 2. The community cards visible to both player and opponent.
# 3. The current bet placed by you and
# 4. The current bet placed by the opponent.
# 5. This one is not listed in the instruction but also should be considered: how much money the opponent have (sum to 20000)

# Simple implementation using Monte Carlo Sampling
# Argument: the opponent will determine its next move based on the 5 states and
# They may also make their action based on the history, which is basically taking our player's action into consideration
# To take this part into account we would be basically predicting how the opponent predicts our action, which is nested
# We can probably ignore the history for now.

GUESS_PROB = 1/3
SMALL_BLIND = 10
BIG_BLIND = 20

# Each state maintains a set of probabilities of transitioning to other states
class State:
    def __init__(self, hole_cards, community_cards, betted, opponent_bet, opponent_pocket_level): # opponent_pocket refers to how much money the opponent has
        # The instruction seems to have conflicting use of pot
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.betted = betted # Not implemented in game tree
        self.opponent_bet = opponent_bet # Not implemented in game tree
        self.opponent_pocket = opponent_pocket_level # 6 intervals
        self.transition_dict = {}
        self.seen_times = 0

    # Given a current state and an action, the next state is deterministic
    def record_move(self, action):
        self.seen_times += 1
        if action not in self.prob_dict:
            self.transition_dict[(action)] = 1
        else:
            self.transition_dict[(action)] += 1
    
    def get_probability(self, action):
        # Should think about what the initial value is
        if self.seen_times == 0:
            return GUESS_PROB
        if (action) not in self.prob_dict:
            return 0
        else:
            return self.transition_dict[action] / self.seen_times

class OpponentAction:
    def __init__(self):
        self.states = {} # Could integrate State into OpponentAction to use less memory, though this provides modularity
        # states = {
        #     "(hole_cards, community_cards, betted, opponent_pocket_level)": State
        # }

    # Divide the total money in 5 intervals
    def __calc_opponent_pocket_level(self, opponent_pocket):
        opponent_pocket_level = 0
        if opponent_pocket >= 0 and opponent_pocket < 3334:
            opponent_pocket_level = 'LOSING'
        elif opponent_pocket < 6667:
            opponent_pocket_level = 'LOW'
        elif opponent_pocket < 13334:
            opponent_pocket_level = 'EVEN'
        elif opponent_pocket < 16667:
            opponent_pocket_level = 'HIGH'
        elif opponent_pocket >= 16667 and opponent_pocket <= 20000:
            opponent_pocket_level = 'WINNING'
        else: print('invalid opponent_pocket')
        return opponent_pocket_level
    
    # def __calc_next_state(hole_cards, community_cards, betted, opponent_bet, opponent_pocket, action):
    #     if action == 'fold':
    #         return (hole_cards, community_cards, 0, 0, opponent_pocket)
    #     elif action == 'raise':
    #         return (hole_cards, community_cards, betted, opponent_bet + BIG_BLIND, opponent_pocket - BIG_BLIND)
    #     elif action == 'call':
    #         return (hole_cards, community_cards, betted, opponent_bet + SMALL_BLIND, opponent_pocket - SMALL_BLIND)
    #     else:
    #         print('invalid move in __calc_next_state')

    
    # Gametree should call this function when the opponent makes a move with the CURRENT state info and the action
    def update(self, hole_cards, community_cards, betted, opponent_bet, opponent_pocket, action,):
        opponent_pocket_level = self.__calc_opponent_pocket_level(opponent_pocket)
        cur_state = None
        # Create a new State if first seen, else update old object
        if ((hole_cards, community_cards, betted, opponent_pocket_level)) not in self.states:
            cur_state = State(hole_cards, community_cards, betted, opponent_bet, opponent_pocket_level)
        else:
            cur_state = self.states[(hole_cards, community_cards, betted, opponent_pocket_level)]
        # record move
        cur_state.record_move(action)
    
    # Gametree should call this function to predict probabilities with the CURRENT state info and the action
    def predict(self, hole_cards, community_cards, betted, opponent_pocket, action):
        opponent_pocket_level = self.__calc_opponent_pocket_level(opponent_pocket)
        if ((hole_cards, community_cards, betted, opponent_pocket_level)) not in self.states:
            return GUESS_PROB
        else:
            cur_state = self.states[(hole_cards, community_cards, betted, opponent_pocket_level)]
            return cur_state.get_probability(action)
    
# How to use: initiate an OpponentAction object at the start of the game, 
# call OpponentAction.update every time the opponent makes a move
# call predict when needing to know the probability of the next move