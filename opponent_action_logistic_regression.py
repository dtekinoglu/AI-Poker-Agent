import math

# The agent’s action,
# denoted by a, is determined by the current round state. Each state of the game
# consists of four components:
# 1. The private cards visible to the player.
# 2. The community cards visible to both player and opponent.
# 3. The current bet placed by you and
# 4. The current bet placed by the opponent.
# 5. This one is not listed in the instruction but also should be considered: how much money the opponent have (sum to 20000)

# Given the features, output a probability for each of the arcs in a three tuple (raise, call, fold) where raise + call + fold = 1

class OpponentAction:
    def __init__(self):
        self.states = {} 
        self.weights = [
            0.25, # community cards weight
            0.25, # player bet weight
            0.25, # opponent bet wegith
        ]  # Initial weights for features
        self.learning_rate = .1
        self.time_step = 1

    def softmax(self, z):
        # Softmax function
        exp_scores = [math.exp(score) for score in z]
        sum_exp_scores = sum(exp_scores)
        return [score / sum_exp_scores for score in exp_scores]
    
    # Gametree calls this function when the opponent makes a move with the CURRENT state info and the action
    def update(self, community_cards, my_bet, op_bet, action):
        # Conv ert action to numeric label
        labels = {
            'raise': 0,
            'call': 1,
            'fold': 2
        }

        # Feature vector
        x = [1, # Bias term
             community_cards, my_bet, op_bet
        ]

        # Calculate predicted probabilities using softmax
        scores = [sum([x[i] * self.weights[i - 1] for i in range(1, len(x))]) for _ in range(3)]
        print(scores)
        predicted_probs = self.softmax(scores)
        print(predicted_probs)
        print()

        # Update weights using gradient descent
        for i in range(len(self.weights)):
            for j in range(3):
                self.weights[i] = (self.weights[i]*self.time_step) + self.learning_rate * (labels[action] == round(j - predicted_probs[j])) * x[i]
                self.weights[i] = (self.weights[i]/(self.time_step + 1))
        self.time_step += 1

    # Gametree should call this function to predict probabilities with the CURRENT state info and the action
    def predict(self, community_cards, my_bet, op_bet):
        # Feature vector
        x = [1, community_cards, my_bet, op_bet]

        # Calculate predicted probabilities using softmax
        scores = [0, 0, 0]
        for i in range(3):
            scores[i] += sum([x[j] * self.weights[j - 1] for j in range(1, len(x))])
        # scores = [sum([x[i] * self.weights[i - 1] for i in range(1, len(x))]) for _ in range(3)]
        predicted_probs = self.softmax(scores)

        # Return predicted probabilities for each action
        return predicted_probs
    
# How to use: initiate an OpponentAction object at the start of the game, 
# call OpponentAction.update every time the opponent makes a move
# call predict when needing to know the probability of the next move