import pandas as pd


class mvlogic(object):

    def __init__(self, userInput):
        self.userInput = userInput
        self.movies_df = pd.read_csv('flaskblog/utils/movies_df.csv')
        self.moviesWithGenres_df = pd.read_csv(
            'flaskblog/utils/moviesWithGenres_df.csv')

    def getrecommendations(self):
        inputMovies = pd.DataFrame(self.userInput)
        inputId = self.movies_df[self.movies_df[
            'title'].isin(inputMovies['title'].tolist())]
        inputMovies = pd.merge(inputId, inputMovies)
        inputMovies = inputMovies.drop('genres', 1).drop('year', 1)

        userMovies = self.moviesWithGenres_df[self.moviesWithGenres_df['movieId'].isin(
            inputMovies['movieId'].tolist())]
        userMovies = userMovies.reset_index(drop=True)
        userGenreTable = userMovies.drop('movieId', 1).drop(
            'title', 1).drop('genres', 1).drop('year', 1)

        userProfile = userGenreTable.transpose().dot(inputMovies['rating'])

        genreTable = self.moviesWithGenres_df.set_index(
            self.moviesWithGenres_df['movieId'])
        genreTable = genreTable.drop('movieId', 1).drop(
            'title', 1).drop('genres', 1).drop('year', 1)

        recommendationTable_df = ((genreTable * userProfile).sum(axis=1) /
                                  (userProfile.sum())).sort_values(ascending=False)
        return recommendationTable_df.head(10).index.values.tolist()
