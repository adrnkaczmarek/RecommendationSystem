import numpy as np
import math

#data loading functions
def loadFromFile(file_name):
    file = open(file_name, 'r')
    content = file.read()
    content_array = content.split('\n')
    return content_array

def loadUData():
    content_array = loadFromFile('../u2.data')
    content_array_toreturn = []

    for elem in content_array:
        row = elem.split("\t")
        if len(row) > 1:
            content_array_toreturn.append(row)

    return content_array_toreturn

def getUsersIds(udata):
    users_ids = set()

    for elem in udata:
        users_ids.add(elem[0])

    return users_ids

def getMoviesIds(udata):
    movies_ids = set()

    for elem in udata:
        movies_ids.add(elem[1])

    return movies_ids

def loadUUser():
    content_array = loadFromFile('../u.user')
    content_array_toreturn = []

    for elem in content_array:
        row = elem.split("|")
        if len(row) > 1:
            content_array_toreturn.append(row)

    return content_array_toreturn

def commonIndexes(first, second):
    first_to_return = []
    second_to_return = []

    for index in range(len(first)):
        if first[index] > 0 and second[index] > 0:
            first_to_return.append(first[index])
            second_to_return.append(second[index])

    return first_to_return, second_to_return

def cosineSimilarity(first, second):

    first, second = commonIndexes(first, second)
    numerator = 0
    denominator1 = 0
    denominator2 = 0

    for index in range(len(first)):
        numerator += first[index]*second[index]
        denominator1 += math.pow(first[index], 2)
        denominator2 += math.pow(second[index], 2)

    denominator = (math.sqrt(denominator1)*math.sqrt(denominator2))
    return numerator/denominator

def ratingsMatrix(udata):
    users = getUsersIds(udata)
    movies = getMoviesIds(udata)
    ratings_matrix = np.zeros((len(movies), len(users)))

    for row in udata:
        ratings_matrix[int(row[1]) - 1, int(row[0]) - 1] = row[2]

    return ratings_matrix

def itemsGenresMatrix():
    content_array = loadFromFile('../u.item')
    genres_array = loadFromFile('../u.genre')
    array = [[0 for x in range(len(genres_array))] for y in range(len(content_array))]

    for elem in content_array:
        row = elem.split("|")
        if len(row) > 1:
            length = len(row)
            for num in range(5, length):
                rownmb = int(row[0]) - 1
                clmnmb = num - 5
                array[int(row[0])-1][num-5] = row[num]

    content_array_to_return = np.matrix(array)
    return content_array_to_return

def getPredictions(matrix, user):
    not_rated = []
    rated = []
    predictions = []

    for index in range(len(matrix)):
        if matrix[index][user] == 0:
            not_rated.append([index, matrix[index]])
        else:
            rated.append([index, matrix[index]])

    counter = 0.0
    denominator = 0.0

    for item in not_rated:
        similarities = []

        for item_rated in rated:
            similarities.append(cosineSimilarity(item[1], item_rated[1]))

        for index in range(len(similarities)):
            counter += similarities[index] * rated[index][1][user]
            denominator += math.fabs(similarities[index])

        predictions.append({'id': item[0], 'value': counter/denominator})

    return predictions

def recommend(predictions):
    recommended = []
    sum = 0
    counter = 0

    for row in predictions:
        sum += row['value']
        counter += 1

    average = sum/counter

    for row in predictions:
        if row['value'] > average:
            recommended.append(row['id'])

    return recommended

if __name__ == "__main__":
    users_data = loadUUser()
    items_to_genres_matrix = itemsGenresMatrix()
    ratings_matrix = ratingsMatrix(loadUData())
    predictions = getPredictions(ratings_matrix, 3)
    print predictions
    print recommend(predictions)
