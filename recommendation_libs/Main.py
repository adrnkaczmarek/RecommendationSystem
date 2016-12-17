from LoadingData import Loader
from CollaborativeFiltering import CollaborativeFiltering


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
    loader = Loader()
    collFiltering = CollaborativeFiltering()

    users_data = loader.loadUUser()
    items_to_genres_matrix = collFiltering.itemsGenresMatrix()
    ratings_matrix = collFiltering.ratingsMatrix(loader.loadUData())
    predictions = collFiltering.getPredictionsForUser(ratings_matrix, 3)
    print predictions
    print recommend(predictions)
