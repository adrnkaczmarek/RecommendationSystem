import numpy as np
import math
from LoadingData import Loader

class RecSystem(object):

    def __init__(self, trainSet):
        self.predictor = CollaborativeFiltering(trainSet)

    def getQueryFloatResult(self, queryTuple):
        user = int(queryTuple[0])
        item = int(queryTuple[1])
        return self.processedDataRepresentation[item][user]

    def getMultiQueryFloatResults(self, queryTuplesList):
        multiQueryFloatResults = {}
        for tempQueryTuple in queryTuplesList:
            multiQueryFloatResults[tempQueryTuple] = self.getQueryFloatResult(tempQueryTuple)
        return multiQueryFloatResults

    def processInputArray(self):
        self.processedDataRepresentation = self.predictor.getPredictions()
        self.inputDataProcessed = True

class CollaborativeFiltering(object):

    loader = Loader()

    def __init__(self, trainSet):
        self.trainSet = trainSet

    def getUsersIds(self, udata):
        users_ids = set()

        for elem in udata:
            users_ids.add(elem[0])

        return users_ids

    def getMoviesIds(self, udata):
        movies_ids = set()

        for elem in udata:
            movies_ids.add(elem[1])

        return movies_ids

    def commonIndexes(self, first, second):
        first_to_return = []
        second_to_return = []

        for index in range(len(first)):
            if first[index] != 0 and second[index] != 0:
                if math.fabs(first[index]) <= 5 and math.fabs(second[index]) <= 5:
                    first_to_return.append(first[index])
                    second_to_return.append(second[index])

        return first_to_return, second_to_return

    def getMostSimilar(self, vector):
        sum = 0

        for (id, similarity) in vector:
            sum += similarity

        avg = float(sum)/len(vector)
        toReturn = []

        for (id, similarity) in vector:
            if similarity >= avg:
                toReturn.append((id, similarity))

        return toReturn

    def cosineSimilarity(self, first, second):

        first_common, second_common = self.commonIndexes(first, second)
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

    def ratingsMatrix(self, udata):
        users = self.getUsersIds(udata)
        movies = self.getMoviesIds(udata)
        ratings_matrix = np.zeros((len(movies), len(users)))

        for row in udata:
            ratings_matrix[int(row[1]) - 1, int(row[0]) - 1] = row[2]

        return ratings_matrix

    def getPrediction(self, userId, itemId):
        rated = []
        item = self.trainSet[itemId]

        for index in range(len(self.trainSet)):
            if self.trainSet[index][userId] != 0:
                rated.append((index, self.trainSet[index]))

        counter = 0.0
        denominator = 0.0

        similarities = []

        for item_rated in rated:
            similarities.append((item_rated[0], self.cosineSimilarity(item, item_rated[1])))

        similarities = self.getMostSimilar(similarities)

        for index in range(len(similarities)):
            counter += similarities[index][1] * rated[index][1][userId]
            denominator += math.fabs(similarities[index][1])

        return counter / denominator

    def getPredictionsForUser(self, matrix, user):
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

        #neighbours = int(math.ceil(float(len(rated))/1.5))

        for item in not_rated:
            similarities = []

            for item_rated in rated:
                similarities.append((item_rated[0], self.cosineSimilarity(item[1], item_rated[1])))

            similarities = self.getMostSimilar(similarities)

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
            predictions = self.getPredictionsForUser(self.trainSet, userId)

            for j in range(len(predictions)):
                movieId = predictions[j]['id']
                result[movieId][userId] = predictions[j]['value']

        return result
