from math import pow, sqrt

def cosine(ratings1, ratings2):
    norm1 = sum([pow(rating,2) for rating in ratings1.values()])
    norm2 = sum([pow(rating,2) for rating in ratings2.values()])
    intersect_keys = filter(lambda x: x in ratings1.keys(), ratings2.keys())
    dot_product = sum([ratings1[key]*ratings2[key] for key in intersect_keys])
    cosine_distance = dot_product/(sqrt(norm1*norm2))
    return cosine_distance


class recommenderSystem:
    #Inititalizes all the constants
    def __init__(self,data, k=3, metric=cosine, n = 2):

    	self.k = k
    	self.n = n
    	self.metric = metric
        self.data = data

    #Computes the distance between a user and all other users in the database
    def computeNeighbor(self, user):

        distances = {}
        for person in self.data.keys():
            if person != user:
                distances[person] = self.metric(self.data[user],self.data[person])
        return distances

    #Recommends movies that a user has not seen based on his similarity with other users
    def recommend(self, user):
        
        distances = self.computeNeighbor(user) #Returns sets of distances from user to each other user in the dataset
        KnearestNeighbors = sorted(distances,key=distances.get, reverse=True)[:self.k] #Find K-nearest neighbors

        totalWeight = sum([distances[neighbor] for neighbor in KnearestNeighbors]) 
        recommendations = {}
        userInfo = self.data[user]
        for neighbor in KnearestNeighbors:
            neighborInfo = self.data[neighbor] 
            neighborWeight = (1.0*distances[neighbor])/totalWeight #Assigns each neighbor a proportional weight
            newMovieRecommendations = filter(lambda x: x not in userInfo.keys(), neighborInfo.keys()) #Finds movies that the user has not seen
            for newMovie in newMovieRecommendations:
                if newMovie in recommendations.keys():
                    recommendations[newMovie] += neighborInfo[newMovie]*neighborWeight
                else:
                    recommendations[newMovie] = neighborInfo[newMovie]*neighborWeight
        topMovies = sorted(recommendations, key=recommendations.get, reverse=True)[:self.n]
        return [(movie, "%0.3f" % recommendations[movie]) for movie in topMovies]  #Returns a list of tuples (Movie Name, predicted rating) 