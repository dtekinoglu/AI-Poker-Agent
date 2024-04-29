import handprobability as handprob
import timeit
import random as rand

SUIT = ['C', 'D', 'H', 'S']
CARD = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

VALUE_CONVERSIONS = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, '10': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12} # Map strings to numbers (Abstraction)
VALUE_RANGE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] # Pre-written range array for speed

def printHandDictObserved(handDict, atLeast):
    count = 0
    print("-----------------HAND DICT-----------------------")
    for key in handDict.keys():
        if handDict[key]['observed'] > atLeast and len(handDict[key]['hole']) == 2:
            print(key,":", handDict[key])
            count += 1
            print()
    print("-----------------END-----------------------")
    return

def convert_hand(hand):
    return [(card[0], VALUE_CONVERSIONS[card[1:]]) for card in [*hand]]

def handAbstraction(hand):
    hand = convert_hand(hand)
    clubs = 0
    diamonds = 0
    hearts = 0
    spades = 0
    mults = [0 for _ in range(len(hand)+1)]
    for card in hand:
        suit = card[0]
        if suit == 'C':
            clubs += 1
        elif suit == 'D':
            diamonds += 1
        elif suit == 'H':
            hearts += 1
        else:
            spades += 1
    mults[clubs] += 1
    mults[diamonds] += 1
    mults[hearts] += 1
    mults[spades] += 1
    
    hand = [hand[i][1] for i in range(len(hand))]
    hand.sort()
    return (tuple(hand), tuple(mults[2:]))

def handDistribution(hole, community, ms_limit, handDict, iter_limit=1000000, suit=SUIT, card=CARD):
    # Track total time taken to run the script
    start = timeit.default_timer()

    # Prepare the deck and known cards only once
    known = handprob.convert_known(hole, community)
    deck = handprob.generateDeckTuple(suit, card, known)

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
        # Track iterations
        iters += 1
        # Always finish at the end if over-time or over limit of simulations
        if timeit.default_timer() - start > ms_limit / 1000 or iter_limit < iters:
            break
        # Get hand for simulation
        sample = handprob.sampleSortDeck(deck, known)
        cardData = handprob.processCards(sample)

        isFlush = False

        # Check flushes
        if handprob.checkFlush(cardData) is True:
            # Checks these only if there is a flush
            if handprob.checkStraightFlush(cardData) is True:
                if handprob.checkRoyalFlush(cardData) is True:
                    royalFlush += 1
                    continue
                else:
                    straightFlush += 1
                    continue
            else:
                isFlush = True

        # 4-kind has no relations
        if handprob.checkFourKind(cardData) is True:
            fourKind += 1
            continue

        # Checking full-house relation broke 3-kind :(
        if handprob.checkFullHouse(cardData) is True:
            fullHouse += 1
            continue

        # We already know the state of flushes
        if isFlush:
            flush += 1
            continue
        
        # Checking for straight vs straight flush is too different to relate
        if handprob.checkStraight(cardData) is True:
            straight += 1
            continue

        # Already checked 3-kind
        if handprob.checkThreeKind(cardData) is True:
        # elif isThreeKind is True:
            threeKind += 1
            continue

        # There can only be 2 pairs if there is 1 pair
        if handprob.checkPair(cardData) is True:
            if handprob.check2Pair(cardData) is True:
                twoPair += 1
            else:
                pair += 1
            continue

        # High-card is the best you can do if you pass over the rest
        else:
            high += 1

        
    
    # Average the results to get a full distribution
    abs = handAbstraction(hole + community)
    if abs in handDict.keys():
        results = {'Royal Flush': royalFlush + handDict[abs]['with_hole']['Royal Flush'],
                'Straight Flush':straightFlush + handDict[abs]['with_hole']['Straight Flush'],
                'Four Kind':fourKind + handDict[abs]['with_hole']['Four Kind'],
                'Full House':fullHouse + handDict[abs]['with_hole']['Full House'],
                'Flush':flush + handDict[abs]['with_hole']['Flush'],
                'Straight':straight + handDict[abs]['with_hole']['Straight'],
                'Three Kind':threeKind + handDict[abs]['with_hole']['Three Kind'],
                'Two Pair':twoPair + handDict[abs]['with_hole']['Two Pair'],
                'Pair':pair + handDict[abs]['with_hole']['Pair'],
                'High':high + handDict[abs]['with_hole']['High']}
        return_obj = {'observed': handDict[abs]['observed'] + 1,
                    'hole': hole, # Return the hole cards used in the calculation
                    'community': community, # Same with community cards
                    'iterations': (iters + handDict[abs]['iterations']), # Return iteration count to get how effective it was
                    'with_hole': results}
    else:
        results = {'Royal Flush': royalFlush,
                    'Straight Flush':straightFlush,
                    'Four Kind':fourKind,
                    'Full House':fullHouse,
                    'Flush':flush,
                    'Straight':straight,
                    'Three Kind':threeKind,
                    'Two Pair':twoPair,
                    'Pair':pair,
                    'High':high}

        return_obj = {'observed': 1,
                        'hole': hole, # Return the hole cards used in the calculation
                        'community': community, # Same with community cards
                        'iterations': iters, # Return iteration count to get how effective it was
                        'with_hole': results}
    #print(iters)
    handDict[abs] = return_obj
    return handDict

def tupleToCard(cardTuple):
    return cardTuple[0]+list(VALUE_CONVERSIONS.keys())[list(VALUE_CONVERSIONS.values()).index(cardTuple[1])]

#
def sampleHolesAndComs():
    deck = handprob.generateDeckTuple(SUIT,CARD, [])
    sample = handprob.sampleSortDeck(deck, [])
    int = rand.randint(2,7)
    sample = [tupleToCard(card) for card in sample]
    return ((sample[0:2]), (sample[2:int]))

#Converts raw number of observations into probability for each hand abstraction
#Called by getDelta() :)
def toProbDict(handDict):
    for key in handDict.keys():
        iters = handDict[key]['iterations']
        handDict[key]['with_hole']['Royal Flush'] = handDict[key]['with_hole']['Royal Flush']/iters
        handDict[key]['with_hole']['Straight Flush'] = handDict[key]['with_hole']['Straight Flush']/iters
        handDict[key]['with_hole']['Four Kind'] = handDict[key]['with_hole']['Four Kind']/iters
        handDict[key]['with_hole']['Full House'] = handDict[key]['with_hole']['Full House']/iters
        handDict[key]['with_hole']['Flush'] = handDict[key]['with_hole']['Flush']/iters
        handDict[key]['with_hole']['Straight'] = handDict[key]['with_hole']['Straight']/iters
        handDict[key]['with_hole']['Three Kind'] = handDict[key]['with_hole']['Three Kind']/iters
        handDict[key]['with_hole']['Two Pair'] = handDict[key]['with_hole']['Two Pair']/iters
        handDict[key]['with_hole']['Pair'] = handDict[key]['with_hole']['Pair']/iters
        handDict[key]['with_hole']['High'] = handDict[key]['with_hole']['High']/iters
    return handDict

#Finds the difference in the probability of getting each hand given the hole cards, for each hand abstraction
def getDelta(handDict):
    handDict = toProbDict(handDict)
    for key in handDict.keys():
        if key != ((), ()):
            handDict[key].update({'delta':{'Royal Flush': handDict[key]['with_hole']['Royal Flush'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Royal Flush'],
                        'Straight Flush': handDict[key]['with_hole']['Straight Flush'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Straight Flush'],
                        'Four Kind': handDict[key]['with_hole']['Four Kind'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Four Kind'],
                        'Full House': handDict[key]['with_hole']['Full House'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Full House'],
                        'Flush': handDict[key]['with_hole']['Flush'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Flush'],
                        'Straight': handDict[key]['with_hole']['Straight'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Straight'],
                        'Three Kind': handDict[key]['with_hole']['Three Kind'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Three Kind'],
                        'Two Pair': handDict[key]['with_hole']['Two Pair'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Two Pair'],
                        'Pair': handDict[key]['with_hole']['Pair'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['Pair'],
                        'High': handDict[key]['with_hole']['High'] - handDict[handAbstraction(handDict[key]['community'])]['with_hole']['High']}})
            
    return handDict

def getWinLossOdds(handDict, iters):
    for key in handDict:
        myHandOdds = handDict[key]['with_hole']
        myHandOddsList = [myHandOdds[hand] for hand in handDict[key]['with_hole'].keys()]
        myHandOddsList.reverse()
        oppHandOdds = handDict[handAbstraction(handDict[key]['community'])]['with_hole']
        oppHandOddsList = [oppHandOdds[hand] for hand in handDict[handAbstraction(handDict[key]['community'])]['with_hole'].keys()]
        oppHandOddsList.reverse()
        myWins = 0
        oppWins = 0
        noWins = 0
        for i in range(iters):
            print(i)
            handIndex = rand.uniform(0,1)
            myIndex = 0
            myOddsCumulative = 0
            while myOddsCumulative + myHandOddsList[myIndex] < handIndex:
                myOddsCumulative += myHandOddsList[myIndex]
                myIndex += 1
                if myIndex > 9:
                    break
            oppIndex = 0
            oppOddsCumulative = 0
            while oppOddsCumulative + oppHandOddsList[oppIndex] < handIndex:
                oppOddsCumulative += oppHandOddsList[oppIndex]
                oppIndex += 1
                if oppIndex > 9:
                    break
            
            if oppIndex > myIndex:
                oppWins += 1
            if myIndex > oppIndex:
                myWins += 1
            if myIndex == oppIndex:
                noWins += 1
        handDict[key].update({'win_chance': myWins/iters})
        handDict[key].update({'loss_chance': oppWins/iters})
        handDict[key].update({'tie_chance': noWins/iters})
    return handDict




if __name__ == '__main__':
    handDict = dict({})
    handDict = handDistribution([], [], 1000, handDict)
    for i in range(10):
        sample = sampleHolesAndComs()
        handDict = handDistribution(sample[1], [], 10, handDict)
        handDict = handDistribution(sample[0], sample[1], 10, handDict)
    handDict = getDelta(handDict)
    handDict = getWinLossOdds(handDict, 1000)
    printHandDictObserved(handDict, 0)
