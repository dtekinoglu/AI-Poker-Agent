from pypokerengine.players import BasePokerPlayer
import handprobability as handProb
import random as rand

# Map round names to numbers (Abstraction)
ROUND_ENUM = {'preflop': 0, 'flop': 1, 'turn': 2, 'river': 3}

class Group11Player(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        # List of trained weights
        weights = [
            0.3281547950071396,
            0.8747720058096283,
            0.5847482152699021,
            0.7214578804204361,
            0.012928631272851085,
            0.5746492140001189,
            0.4095508933413212,
            0,
            2
        ]

        # WEIGHTS:
        TRIFOLD_0 = weights[0] # 0 - 1
        TRIFOLD_1 = weights[1] # 0 - 1
        TRIFOLD_2 = weights[2] # 0 - 1
        TRIFOLD_3 = weights[3] # 0 - 1

        # Percentage to call over raise
        SUIT_CALL = weights[4] # 0 ~ 1
        NUMBER_CALL = weights[5] # 0 ~ 1
        HIGH_CALL = weights[6] # 0 ~ 1
        
        # 1 - 10, bad is lower
        BAD_HAND = weights[7] # 1 - 10
        MID_HAND = weights[8] # 1 - 10

        # Easy access for current round
        ROUND_NUM = ROUND_ENUM[round_state['street']]

        # Generate a uniform sample once for each betting round
        sample = rand.uniform(0,1)

        # Train sample cuttoffs
        def trifold():
            if ROUND_NUM == 0:
                return 'fold' if sample > TRIFOLD_0 else move('call')
            elif ROUND_NUM == 1:
                return 'fold' if sample > TRIFOLD_1 else move('call')
            elif ROUND_NUM == 2:
                return 'fold' if sample > TRIFOLD_2 else move('call')
            elif ROUND_NUM == 3:
                return 'fold' if sample > TRIFOLD_3 else move('call')
            else:
                return 'fold'

        # Determine which move to make given the desired choice
        def move(move):
            valid_actions_map = map(lambda x: x['action'], valid_actions)
            if move == 'fold':
                move = trifold()
            if move in valid_actions_map:
                return move
            else:
                return 'call'

        # Run for the flop, turn, and river portion of the game
        if round_state['street'] != 'preflop':
            # Get the distribution of hands
            handOdds = handDistribution(hole_card, round_state['community_card'])

            # Hand distribution decider (weight)
            bad_hand = BAD_HAND
            mid_hand = MID_HAND
            if sum(handOdds[bad_hand:mid_hand]) >= 1:
                return move('call')
            elif sum(handOdds[mid_hand:10]) >= 1:
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
  return Group11Player()


# -------------------- HAND STRENGTH CALCULATION -------------------- #


# Map suit and rank to numbers (Abstraction)
SUIT_CONVERSIONS = {'C': 0, 'D': 1, 'H': 2, 'S': 3}
VALUE_CONVERSIONS = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}


# Converts the hole and community cards into a list of (suit, value) tuples
# Tuples are more efficient and easier to work with
def convert_known(hole, community):
    return [(SUIT_CONVERSIONS[card[0]], VALUE_CONVERSIONS[card[1:]]) for card in [*hole, *community]]


# Sorts the known cards by rank
def sortKnown(hole, community):
    return sorted(convert_known(hole, community), key=lambda x: x[1])


# Processes a hand to calculate sets of
# pairs, triples, quadruples, unique values, and
# buckets by suit, all sorted by rank.
# This allows for easy checking of hand strength
def processCards(cards):
    # Lists for suits and values
    suits = ([],[],[],[])
    valueList = [0, 0, 0, 0, 0, 0, 0]

    # Starting with -1 eliminates the 'i - 1' operation in counts[i-1]
    curr_count = -1
    iters = -1
    last = -1

    # Lists are slower but mutable
    counts = [0, 0, 0, 0]

    # Looping is time-equivalent to hardcoding lists/sets
    # We can save operations by combining the count and suit loop
    for card in cards:
        # Algorithm for counting sets of pairs, triples, and quadruples
        curr_count += 1
        iters += 1
        value = card[1]

        if iters == 0:
            curr_count = -1
        elif last != value:
            counts[curr_count] += 1
            curr_count = -1
        last = value

        # Append values to the suit and value list
        # Suit list allows simple calculation of flush/straight flush/royal flush
        suits[card[0]].append(value)
        valueList[iters] = value

    # Append the last count item not detected by the loop
    curr_count += 1
    counts[curr_count] += 1

    # Get unique ranks
    valueSet = set(valueList)

    # Return 3 independent values
    return suits, list(valueSet), counts


# Checks if a hand contains a royal flush
def checkRoyalFlush(suits):
    # We can check the bounds since it is sorted, numbers are unique per suit, and
    # the royal flush is on the right
    if (len(suits[0]) > 4 and suits[0][-5] == 8 and suits[0][-1] == 12)\
    or (len(suits[1]) > 4 and suits[1][-5] == 8 and suits[1][-1] == 12)\
    or (len(suits[2]) > 4 and suits[2][-5] == 8 and suits[2][-1] == 12)\
    or (len(suits[3]) > 4 and suits[3][-5] == 8 and suits[3][-1] == 12):
        return True
    return False


# Checks if a hand contains a straight flush
def checkStraightFlush(suits):
    # We can check the bounds since it is sorted, and ranks are unique per suit
    # Since it is any straight,, we check each 5 set of cards available
    s0 = suits[0]
    s1 = suits[1]
    s2 = suits[2]
    s3 = suits[3]
    lne_s0 = len(s0)
    lne_s1 = len(s1)
    lne_s2 = len(s2)
    lne_s3 = len(s3)
    if (lne_s0 > 4 and s0[0] == s0[4] - 4)\
    or (lne_s0 > 5 and s0[1] == s0[5] - 4)\
    or (lne_s0 > 6 and s0[2] == s0[6] - 4)\
    or (lne_s1 > 4 and s1[0] == s1[4] - 4)\
    or (lne_s1 > 5 and s1[1] == s1[5] - 4)\
    or (lne_s1 > 6 and s1[2] == s1[6] - 4)\
    or (lne_s2 > 4 and s2[0] == s2[4] - 4)\
    or (lne_s2 > 5 and s2[1] == s2[5] - 4)\
    or (lne_s2 > 6 and s2[2] == s2[6] - 4)\
    or (lne_s3 > 4 and s3[0] == s3[4] - 4)\
    or (lne_s3 > 5 and s3[1] == s3[5] - 4)\
    or (lne_s3 > 6 and s3[2] == s3[6] - 4):
        return True
    return False


# Determines how good the agent's current hand is
def handDistribution(hole, community):
    # Get a sorted tuple conversion of the known cards
    known = sortKnown(hole, community)

    # Save results to help calculate averages
    royalFlush = 0
    straightFlush = 0
    fourKind = 0
    fullHouse = 0
    flush = 0
    straight = 0
    threeKind = 0
    twoPair = 0
    pair = 0
    high = 0
    
    # Values for optimizing strength calculation
    isFlush = False
    isThreeKind = False

    # Process the cards
    suits, values, counts = processCards(known)

    # save repeat operations
    len_Clubs = len(suits[0])
    len_Diamonds = len(suits[1])
    len_Hearts = len(suits[2])
    len_Spades = len(suits[3])
    num_unique_values = len(values)
    sample_pair_count = counts[1]

    # Using a while loop with breaking allows for break/continue shenanigans
    while True:
        # Check flushes
        if len_Clubs > 4\
        or len_Diamonds > 4\
        or len_Hearts > 4\
        or len_Spades > 4:
            
            # Checks these only if there is a flush
            if checkStraightFlush(suits) is True:
                if checkRoyalFlush(suits) is True:
                    royalFlush += 1
                    break
                else:
                    straightFlush += 1
                    break
            else:
                isFlush = True

        # Check 4-kind
        if counts[3] > 0:
            fourKind += 1
            break

        # Check full-house
        if counts[2] > 0:
            if sample_pair_count > 0:
                fullHouse += 1
                break
            else:
                isThreeKind = True

        # We already know the state of flushes
        if isFlush:
            flush += 1
            break
        
        # Checking for straight vs straight flush is too different to relate
        if (num_unique_values > 4 and values[0] == values[4] - 4)\
        or (num_unique_values > 5 and values[1] == values[5] - 4)\
        or (num_unique_values > 6 and values[2] == values[6] - 4):
            straight += 1
            break

        # Check 3-kind
        if isThreeKind:
            threeKind += 1
            break

        # There can only be 2 pairs if there is 1 pair
        if sample_pair_count > 0:
            if sample_pair_count > 2:
                twoPair += 1
            else:
                pair += 1
            break

        # High-card is the best you can do if you pass over the rest
        else:
            high += 1
        
        break

    # Ordered list of hand strengths from low to high
    results = [
        high,
        pair,
        twoPair,
        threeKind,
        straight,
        flush,
        fullHouse,
        fourKind,
        straightFlush,
        royalFlush
    ]
    
    return results