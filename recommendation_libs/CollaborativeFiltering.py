import numpy as np
import math

class CollaborativeFiltering(object):

    def __init__(self, trainSet):
        self.trainSet = trainSet

    def __commonIndexes(self, first, second):
        first_to_return = []
        second_to_return = []

        for index in range(len(first)):
            if first[index] != 0 and second[index] != 0:
                if math.fabs(first[index]) <= 5 and math.fabs(second[index]) <= 5:
                    first_to_return.append(first[index])
                    second_to_return.append(second[index])

        return first_to_return, second_to_return

    def __getMostSimilar(self, vector):
        sum = 0

        for (id, similarity) in vector:
            sum += similarity

        avg = float(sum)/len(vector)
        toReturn = []

        for (id, similarity) in vector:
            if similarity >= avg:
                toReturn.append((id, similarity))

        return toReturn

    def __cosineSimilarity(self, first, second):

        first_common, second_common = self.__commonIndexes(first, second)
        numerator = 0
        denominator1 = 0
        denominator2 = 0
        result = -1

        if len(first_common) > 0 and len(second_common) > 0:
            for index in range(len(first_common)):
                numerator += first_common[index] * second_common[index]
                denominator1 += math.pow(first_common[index], 2)
                denominator2 += math.pow(second_common[index], 2)

            denominator = (math.sqrt(denominator1) * math.sqrt(denominator2))
            result = numerator / denominator

        return result

    def __getPredictionsForUser(self, matrix, user):
        not_rated = []
        rated = []
        predictions = []

        for index in range(len(matrix)):
            if matrix[index][user] == 0:
                not_rated.append((index, matrix[index]))
            else:
                rated.append((index, matrix[index]))

        counter = 0.0
        denominator = 0.0

        for item in not_rated:
            similarities = []

            for item_rated in rated:
                similarities.append((item_rated[0], self.__cosineSimilarity(item[1], item_rated[1])))

            similarities = self.__getMostSimilar(similarities)

            for index in range(len(similarities)):
                counter += similarities[index][1] * rated[index][1][user]
                denominator += math.fabs(similarities[index][1])

            predictions.append({'id': item[0], 'value': counter / denominator})

        return predictions

    def getPredictions(self):
        self.trainSet = self.trainSet[1:, 1:]
        result = np.array(self.trainSet)

        for i in range(len(self.trainSet[0])):
            userId = i
            predictions = self.__getPredictionsForUser(self.trainSet, userId)

            for j in range(len(predictions)):
                movieId = predictions[j]['id']
                result[movieId][userId] = predictions[j]['value']

        return result

    def getPredictionsWithVotesCounter(self):
        self.trainSet = self.trainSet[1:, 1:]
        result = np.array(self.trainSet)
        vote_count, min, max, avg = self.__getVoteCountsForDataSet()
        mid = max - min
        max -= mid
        min -= mid

        for i in range(len(self.trainSet[0])):
            userId = i
            predictions = self.__getPredictionsForUser(self.trainSet, userId)
            predictions = self.__addVoteCountModifierLogFunc(predictions, vote_count, min, max)

            for j in range(len(predictions)):
                movieId = predictions[j]['id']
                result[movieId][userId] = predictions[j]['value']

        return result

    def getPredictionsWithVotesCounterSimpleScale(self):
        self.trainSet = self.trainSet[1:, 1:]
        result = np.array(self.trainSet)
        vote_count, min, max, avg = self.__getVoteCountsForDataSet()
        mid = max - min
        max -= mid
        min -= mid

        for i in range(len(self.trainSet[0])):
            userId = i
            predictions = self.__getPredictionsForUser(self.trainSet, userId)
            predictions = self.__addVoteCountModifierSimple(predictions, vote_count, min, max)

            for j in range(len(predictions)):
                movieId = predictions[j]['id']
                result[movieId][userId] = predictions[j]['value']

        return result

    def __addVoteCountModifierLogFunc(self, predictions, vote_count, min, max):
        for index in range(len(predictions)):
            toAdd = self.__sigmoid(self.__rescaleValueForExpFunc(min, max, vote_count[predictions[index]['id']])) - 0.5
            predictions[index]['value'] += toAdd/10

        return predictions

    def __addVoteCountModifierSimple(self, predictions, vote_count, min, max):
        for index in range(len(predictions)):
            toAdd = self.__simpleRescale(min, max, vote_count[predictions[index]['id']]) - 0.5
            predictions[index]['value'] += toAdd/10

        return predictions

    def __simpleRescale(self, min, max, value):
        return 1.0/(max-min) * (value - max) + 1

    def __rescaleValueForExpFunc(self, min, max, value):
        return 10.0/(max-min) * (value - max) + 5

    def __getVoteCountsForDataSet(self):
        vote_count = []
        max = 0
        sum = 0
        avg = 0

        for item in self.trainSet:
            counter = 0
            for val in item:
                if val != 0:
                    counter += 1

            if counter > max:
                max = counter

            vote_count.append(counter)

        min = vote_count[0]

        for vote in vote_count:
            if vote < min:
                min = vote
            sum += vote

        avg = float(sum)/len(vote_count)

        return vote_count, min, max, avg

    def __sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
