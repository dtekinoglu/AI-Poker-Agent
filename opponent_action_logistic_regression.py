import math

# Uses three features to determine opponent action
# 1. The private cards visible to the player.
# 3. The current bet placed by you and
# 4. The current bet placed by the opponent.

# Given the features, output a probability for each of the arcs in a three tuple (raise, call, fold) where raise + call + fold = 1
c = 0
class OpponentAction:
    def __init__(self):
        self.n_classes = 3
        self.n_features = 3
        self.weights = [
            # comcrds | my bet | op bet
            [0,         0,          0],  # Raise weights
            [0,         0,          0],  # Call weights
            [0,         0,          0]   # Fold weights
        ]
        self.biases = [0, 0, 0]  # Initial biases
        self.learning_rate = .01
        self.correct_count = 0
        self.guessed_count = 0
        
    def softmax(self, z):
        # Softmax function
        exp_scores = [math.exp(score) for score in z]
        sum_exp_scores = sum(exp_scores)
        return [score / sum_exp_scores for score in exp_scores]
    
    # Gametree calls this function when the opponent makes a move with the CURRENT state info and the action
    # INPUT: array of actual probability
    # e.g. If the action is raise, input action = [1, 0, 0]
    def update(self, community_cards, my_bet, op_bet, action):
        # Convert action to numeric label
        labels = {
            'fold': 0,
            'call': 1,
            'raise': 2
        }

        # Feature vector
        features = [community_cards, my_bet, op_bet]

        # STEP 1: For each class 
        # compute a linear combination of the input features and the weight vector of class,
        # that is, for each training example compute a score for each class.
        scores = [sum(features[i] * self.weights[j][i] + self.biases[j] for i in range(len(features))) for j in range(self.n_classes)]
        predicted_probs = self.softmax(scores)

        for i in range(len(action)):
            if action[i] == 1 and predicted_probs[i] == max(predicted_probs):
                self.correct_count += 1
        self.guessed_count += 1

        # Update weights and biases using gradient descent
        for i in range(self.n_classes):
            for j in range(len(features)):
                self.weights[i][j] = self.weights[i][j] - self.learning_rate * (predicted_probs[i] - action[i]) * features[j]
            self.biases[i] = self.biases[i] - self.learning_rate * (predicted_probs[i] - action[i]) * 1

    # Gametree should call this function to predict probabilities with the CURRENT state info and the action
    def predict(self, community_cards, my_bet, op_bet):
        features = [community_cards, my_bet, op_bet]
        scores = [sum(features[i] * self.weights[j][i] + self.biases[j] for i in range(len(features))) for j in range(self.n_classes)]
        predicted_probs = self.softmax(scores)
        return predicted_probs
    
    # Helper function
    def _calc_prediction_accuracy(self):
        print("Guessed {} out of {} times correct".format(self.correct_count, self.guessed_count))
        return self.correct_count / self.guessed_count
    
# How to use: initiate an OpponentAction object at the start of the game, 
# call OpponentAction.update every time the opponent makes a move
# call predict when needing to know the probability of the next move