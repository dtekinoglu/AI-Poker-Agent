import timeit
import random
from numpy.random import choice


SUIT = ['C', 'D', 'H', 'S']
SUIT_RANGE = [0, 1, 2, 3]
SUIT_CONVERSIONS = {'C': 0, 'D': 1, 'H': 2, 'S': 3}

VALUE = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
VALUE_RANGE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
VALUE_CONVERSIONS = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12} # Map strings to numbers (Abstraction)

HANDS = ['High', 'Pair', 'Two Pair', 'Three Kind', 'Straight', 'Flush', 'Full House', 'Four Kind', 'Straight Flush', 'Royal Flush']



def get_single_process(hole, community):
    known = convert_known(hole, community)
    deck = generateDeckTuple(known)
    sample = sampleSortDeck(deck, known)
    return processCards(sample)

def convert_known(hole, community):
    return [(SUIT_CONVERSIONS[card[0]], VALUE_CONVERSIONS[card[1:]]) for card in [*hole, *community]]

# Samples and adds with splat operator
def sortKnown(hole, community):
    return sorted(convert_known(hole, community), key=lambda x: x[1])

def generateDeckTuple(known):
    deck = []
    for suit in SUIT_RANGE:
        for value in VALUE_RANGE:
            suitCard = (suit, value)
            if suitCard not in known:
                deck.append((suit, value))
    return deck

# Samples and adds with splat operator
def sampleSortDeck(deck, known):
    sample = random.sample(deck, k=(7 - len(known)))
    return sorted([*known, *sample], key=lambda x: x[1])

def processCards(cards):
    suits = ([],[],[],[])
    valueList = [0, 0, 0, 0, 0, 0, 0]

    # Starting with -1 eliminates the 'i - 1' operation in counts[i-1]
    curr_count = -1
    iters = -1
    last = -1

    # Tuples are faster but immutable
    counts = [0, 0, 0, 0]

    # Looping is time-equivalent to hardcoding lists/sets
    # We can save operations by combining the count and suit loop
    for card in cards:
        curr_count += 1
        iters += 1
        value = card[1]

        if iters == 0:
            curr_count = -1
        elif last != value:
            counts[curr_count] += 1
            curr_count = -1
        last = value

        suits[card[0]].append(value)
        valueList[iters] = value

    curr_count += 1
    counts[curr_count] += 1

    valueSet = set(valueList)

    return suits, list(valueSet), counts

def checkRoyalFlush(suits):
    # We can check the bounds since it is sorted, numbers are unique per suit, and
    # the royal flush is on the right
    if (len(suits[0]) > 4 and suits[0][-5] == 8 and suits[0][-1] == 12)\
    or (len(suits[1]) > 4 and suits[1][-5] == 8 and suits[1][-1] == 12)\
    or (len(suits[2]) > 4 and suits[2][-5] == 8 and suits[2][-1] == 12)\
    or (len(suits[3]) > 4 and suits[3][-5] == 8 and suits[3][-1] == 12):
        return True
    return False

def checkStraightFlush(suits):
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

def checkFourKind(count):
    if count[3] > 0:
        return True
    return False

def checkThreeKind(count):
    if count[2] > 0:
        return True
    return False

def check2Pair(count):
    if count[1] > 1:
        return True
    return False

def checkPair(count):
    if count[1] > 0:
        return True
    return False

def checkFullHouse(count):
    if count[1] > 0 and count[2] > 0:
        return True
    return False

def checkFlush(suits):
    if len(suits[0]) > 4\
    or len(suits[1]) > 4\
    or len(suits[2]) > 4\
    or len(suits[3]) > 4:
        return True
    return False

def checkStraight(values):
    len_values = len(values)
    if (len_values > 4 and values[0] == values[4] - 4)\
    or (len_values > 5 and values[1] == values[5] - 4)\
    or (len_values > 6 and values[2] == values[6] - 4):
            return True
    return False

def handDistribution(hole, community, ms_limit, max_iters, sim=False):
    # Track total time taken to run the script
    start = timeit.default_timer()

    # Prepare the deck and known cards only once
    known = convert_known(hole, community)
    deck = generateDeckTuple(known)

    if not sim:
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

    isFlush = False
    isThreeKind = False

    # Count the number of loops completed
    iters = 0
    while iters < max_iters + 1:
        # Track iterations
        iters += 1
    
        # Always finish prior to time-consuming operations
        if timeit.default_timer() - start > ms_limit / 1000:
            break

        # Get hand for simulation
        if sim:
            sample = sampleSortDeck(deck, known)
        else:
            sample = known
        suits, values, counts = processCards(sample)

        # save repeat operations
        len_Clubs = len(suits[0])
        len_Diamonds = len(suits[1])
        len_Hearts = len(suits[2])
        len_Spades = len(suits[3])
        num_unique_values = len(values)
        sample_pair_count = counts[1]

        isFlush = False

        # Check flushes
        if len_Clubs > 4\
        or len_Diamonds > 4\
        or len_Hearts > 4\
        or len_Spades > 4:
            
            # Checks these only if there is a flush
            if checkStraightFlush(suits) is True:
                if checkRoyalFlush(suits) is True:
                    royalFlush += 1
                    continue
                else:
                    straightFlush += 1
                    continue
            else:
                isFlush = True

        # Check 4-kind
        if counts[3] > 0:
            fourKind += 1
            continue

        # Checking full-house relation broke 3-kind :(
        if counts[2] > 0:
            if sample_pair_count > 0:
                fullHouse += 1
                continue
            else:
                isThreeKind = True

        # We already know the state of flushes
        if isFlush:
            flush += 1
            continue
        
        # Checking for straight vs straight flush is too different to relate
        if (num_unique_values > 4 and values[0] == values[4] - 4)\
        or (num_unique_values > 5 and values[1] == values[5] - 4)\
        or (num_unique_values > 6 and values[2] == values[6] - 4):
            straight += 1
            continue

        # Check 3-kind
        if isThreeKind:
            threeKind += 1
            continue

        # There can only be 2 pairs if there is 1 pair
        if sample_pair_count > 0:
            if sample_pair_count > 2:
                twoPair += 1
            else:
                pair += 1
            continue

        # High-card is the best you can do if you pass over the rest
        else:
            high += 1

    # Average the results to get a full distribution
    iters -= 1
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
    
    return return_obj

def getWinLossTieOddsNew(hole, community, ms_limit, iters):
    handDict = handDistribution(hole, community, ms_limit/2)
    oppHand = handDistribution(handDict['community'], [], ms_limit/2)
    oppHandList = [oppHand['with_hole'][key] for key in oppHand['with_hole'].keys()]
    oppHandList.reverse()
    playerHandList = [handDict['with_hole'][key] for key in handDict['with_hole'].keys()]
    playerHandList.reverse()
    #tempList = [0 for _ in range(len(playerHandList))]
    #for i in range(len(playerHandList)):
    #    tempList[i] = sum(playerHandList[0:i+1])
    #playerHandList = [*tempList]
    #for i in range(len(oppHandList)):
    #    tempList[i] = sum(oppHandList[0:i+1])
    #oppHandList = [*tempList]
    playerWins = 0
    playerLosses = 0
    playerTies = 0
    for _ in range(iters):
        playerHand = choice(HANDS, 1, p=playerHandList)
        oppHand = choice(HANDS, 1, p=oppHandList)

        if HANDS.index(playerHand) > HANDS.index(oppHand):
            playerWins += 1
        if HANDS.index(playerHand) < HANDS.index(oppHand):
            playerLosses += 1
        if HANDS.index(playerHand) == HANDS.index(oppHand):
            playerTies += 1
        #sample = random.uniform(0,1)
        #playerIndex = 0
        #oppIndex = 0
        #while playerHandList[playerIndex] <= sample:
        #    playerIndex += 1
        #    if playerIndex >= len(playerHandList):
        #        break
        #while oppHandList[oppIndex] <= sample:
        #    oppIndex += 1
        #    if oppIndex >= len(oppHandList):
        #        break
        #if playerIndex > oppIndex:
        #    playerWins += 1
        #if oppIndex > playerIndex:
        #    playerLosses += 1
        #if oppIndex == playerIndex:
        #    playerTies += 1

    toReturn = (playerWins/iters, playerLosses/iters, playerTies/iters)
    handDict.update({'WinLossTie': toReturn})
    return handDict

def getWinLossTieOdds(hole, community, ms_limit, iters):
    handDict = handDistribution(hole, community, ms_limit/2, iters)
    oppHand = handDistribution(handDict['community'], [], ms_limit/2, iters)
    oppHandList = [oppHand['with_hole'][key] for key in oppHand['with_hole'].keys()]
    oppHandList.reverse()
    playerHandList = [handDict['with_hole'][key] for key in handDict['with_hole'].keys()]
    playerHandList.reverse()
    tempList = [0 for _ in range(len(playerHandList))]
    for i in range(len(playerHandList)):
        tempList[i] = sum(playerHandList[0:i+1])
    playerHandList = [*tempList]
    for i in range(len(oppHandList)):
        tempList[i] = sum(oppHandList[0:i+1])
    oppHandList = [*tempList]
    playerWins = 0
    playerLosses = 0
    playerTies = 0
    for _ in range(iters):
        sample = random.uniform(0,1)
        playerIndex = 0
        oppIndex = 0
        while playerHandList[playerIndex] <= sample:
            playerIndex += 1
            if playerIndex >= len(playerHandList):
                break
        while oppHandList[oppIndex] <= sample:
            oppIndex += 1
            if oppIndex >= len(oppHandList):
                break
        if playerIndex > oppIndex:
            playerWins += 1
        if oppIndex > playerIndex:
            playerLosses += 1
        if oppIndex == playerIndex:
            playerTies += 1

    toReturn = (playerWins/iters, playerLosses/iters, playerTies/iters)
    handDict.update({'WinLossTie': toReturn})
    return handDict


if __name__ == '__main__':
    
    t = timeit.timeit(lambda: getWinLossTieOdds(['C6', 'DK'], [], 50, 3000), number=1, globals=globals())
    print(t)
    print(getWinLossTieOdds(['C6', 'DK'], [], 50, 3000)['WinLossTie'])
    print(getWinLossTieOdds(['C6', 'D6'], ['DQ', 'D7', 'S5'], 50, 3000)['WinLossTie'])
    #t = timeit.timeit(lambda: getWinLossTieOddsNew(['C6', 'DK'], [], 50, 3000), number=1, globals=globals())
    #print(t)
    #print(getWinLossTieOddsNew(['C6', 'DK'], [], 50, 3000)['WinLossTie'])
    #print(getWinLossTieOddsNew(['C6', 'DK'], [], 50, 3000)['WinLossTie'])