import timeit
import random

# Constant lists pre-written for optimization
SUIT = ['C', 'D', 'H', 'S']
CARD = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUE_CONVERSIONS = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, '10': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12} # Map strings to numbers (Abstraction)
VALUE_RANGE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] # Pre-written range array for speed

# Converts a set of known hole and community cards into an abstracted set
def convert_known(hole, community):
    return [(card[0], VALUE_CONVERSIONS[card[1:]]) for card in [*hole, *community]]

# Generates a deck that contains values not in the known card list
def generateDeckTuple(suit, card, known):
    deck = []
    for suit in SUIT:
        for card in VALUE_RANGE:
            suitCard = (suit, card)
            if suitCard not in known:
                deck.append((suit, card))
    return deck

# Samples without replacement and sorts the new hand by value
def sampleSortDeck(deck, known):
    sample = random.sample(deck, k=(7 - len(known)))
    return sorted([*known, *sample], key=lambda x: x[1])

# Pre-processes a hand to speed up future checks
def processCards(cards):
    # Add a list for each suit, a unique set of values, and a count for each pair, triple, and quadruple of a number
    result = {'C': [], 'D': [], 'H': [], 'S': [], 'valueList': set(), 'valueCounts': {1: 0, 2: 0, 3: 0, 4: 0}}

    # Used to quickly count pairs/triples/quadruples
    counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # Save each card value and get the count
    for card in cards:
        result[card[0]].append(card[1])
        result['valueList'].add(card[1])
        counts[card[1]] += 1

    # Get the count of each value in the hand
    for i in result['valueList']:
        result['valueCounts'][counts[i]] += 1

    # Convert to a list for future searching
    result['valueList'] = list(result['valueList'])

    return result

# Checks if a set of cards contains a royal flush
def checkRoyalFlush(cardData):
    for suit in SUIT:
        # We can check the bounds since it is sorted, numbers are unique per suit, and
        # the royal flush is on the right
        if len(cardData[suit]) > 4 and cardData[suit][-5] == 8 and cardData[suit][-1] == 12:
            return True
        # TOODOO HERE CHECK IF IT BREAKS OR ADD MORE IF STATEMENTS
    return False

# Checks if a set of cards contains a straight flush
def checkStraightFlush(cardData):
    for suit in SUIT:
        for i in range(len(cardData[suit]) - 4):
            # Sorted and unique, check if 4 items ahead = item - 4
            if cardData[suit][i] == cardData[suit][i + 4] - 4:
                return True
    return False

# Checks if a set of cards contains a four of a kind
def checkFourKind(cardData):
    return cardData['valueCounts'][4] > 0

# Checks if a set of cards contains a three of a kind
def checkThreeKind(cardData):
    return cardData['valueCounts'][3] > 0

# Checks if a set of cards contains 2 pairs
def check2Pair(cardData):
    return cardData['valueCounts'][2] > 1

# Checks if a set of cards contains a pair
def checkPair(cardData):
    return cardData['valueCounts'][2] > 0

# Checks if a set of cards contains a full-house
def checkFullHouse(cardData):
    return cardData['valueCounts'][2] > 0 and cardData['valueCounts'][3] > 0

# Checks if a set of cards contains a flush
def checkFlush(cardData):
    #for suit in SUIT:
    #    if len(cardData[suit]) > 4:
    #        return True
    if len(cardData['C']) > 4 or len(cardData['D']) > 4 or len(cardData['H']) > 4 or len(cardData['S']) > 4:
        return True
    return False

# Checks if a set of cards contains a straight
def checkStraight(cardData):
    for i in range(len(cardData['valueList']) - 4):
        # Sorted and unique, check if 4 items ahead = item - 4
        # By the problem, every item in the range must be in the straight
        if cardData['valueList'][i] == cardData['valueList'][i + 4] - 4:
            return True
    return False

def handDistribution(hole, community, ms_limit, iter_limit=1000000, suit=SUIT, card=CARD):
    # Track total time taken to run the script
    start = timeit.default_timer()

    # Prepare the deck and known cards only once
    known = convert_known(hole, community)
    deck = generateDeckTuple(suit, card, known)

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

    isFlush = False

    # Count the number of loops completed
    iters = 0
    while True:
        # Get hand for simulation
        sample = sampleSortDeck(deck, known)
        cardData = processCards(sample)

        isFlush = False

        # Check flushes
        if checkFlush(cardData) is True:
            # Checks these only if there is a flush
            if checkStraightFlush(cardData) is True:
                if checkRoyalFlush(cardData) is True:
                    royalFlush += 1
                else:
                    straightFlush += 1
            else:
                isFlush = True

        # 4-kind has no relations
        elif checkFourKind(cardData) is True:
            fourKind += 1

        # Checking full-house relation broke 3-kind :(
        elif checkFullHouse(cardData) is True:
            fullHouse += 1

        # We already know the state of flushes
        elif isFlush is True:
            flush += 1
        
        # Checking for straight vs straight flush is too different to relate
        elif checkStraight(cardData) is True:
            straight += 1

        # Already checked 3-kind
        elif checkThreeKind(cardData) is True:
        # elif isThreeKind is True:
            threeKind += 1

        # There can only be 2 pairs if there is 1 pair
        elif checkPair(cardData) is True:
            if check2Pair(cardData) is True:
                twoPair += 1
            else:
                pair += 1

        # High-card is the best you can do if you pass over the rest
        else:
            high += 1

        # Track iterations
        iters += 1

        # Always finish at the end if over-time or over limit of simulations
        if timeit.default_timer() - start > ms_limit / 1000 or iter_limit < iters:
            break
    
    # Average the results to get a full distribution
    results = {'Royal Flush': royalFlush / iters,
                'Straight Flush':straightFlush / iters,
                'Four Kind':fourKind / iters,
                'Full House':fullHouse / iters,
                'Flush':flush / iters,
                'Straight':straight / iters,
                'Three Kind':threeKind / iters,
                'Two Pair':twoPair / iters,
                'Pair':pair / iters,
                'High':high / iters}
    
    return_obj = {'hole': hole, # Return the hole cards used in the calculation
                    'community': community, # Same with community cards
                    'iterations': iters, # Return iteration count to get how effective it was
                    'with_hole': results}
    print(iters)
    return return_obj

if __name__ == '__main__':
    for i in range(1):
        t = timeit.timeit(lambda: handDistribution(['C6', 'DK'], [], 50), number=1, globals=globals())
        print(t)
        
        dict = handDistribution(['C6', 'DK'], [], 50)
        dict = handDistribution(['S7', 'CQ'], [], 50)
        print(dict)