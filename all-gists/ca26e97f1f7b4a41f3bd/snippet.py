# This pipeline sums up a bunch of values. That simple.
class SumPipeline(pipeline.Pipeline):
    def run(self, *values):
        return sum(values)

# This pipeline takes care of computing the score of one specific player
class PlayerScorePipeline(pipeline.Pipeline):
    def run(self, player, level):
        # Let's call our remote REST API to return the score
        # of this player on the supplied level.
        return remote_api.get_score(player, level)

# This pipeline takes care of computing the score for one specific level
class LevelScorePipeline(pipeline.Pipeline):
    def run(self, level):
        results = []
        for player in level.players:
            # Let's compute the score for this specific player by using
            # another pipeline.
            results.append((yield PlayerScorePipeline(player, level)))

        # Whenever we finish computing the score for all the players, we
        # can then sum up all the values and return the score for this 
        # specific level.
        yield SumPipeline(*results)

# This pipeline takes care of computing the score for one specific game
class GameScorePipeline(pipeline.Pipeline):
    def run(self, game):
        results = []
        for level in game.levels:
            # Let's compute the score for this specific level by using
            # another pipeline.
            results.append((yield LevelScorePipeline(level)))

        # Whenever we finish computing the score for all the levels, we
        # can then sum up all the values and return the score for this 
        # specific game.
        yield SumPipeline(*results)

# This is our first pipeline, which receives a list of games and computes
# the overall score.
class ScorePipeline(pipeline.Pipeline):
    def run(self, *games):
        results = []
        for game in games:
            # Let's compute the score for this specific game by using
            # another pipeline.
            results.append((yield GameScorePipeline(game)))

        # Whenever we finish computing the score for all the games,
        # we can then sum up all the values and return the final score.    
        yield SumPipeline(*results)

# Everything starts here, where we magically pass the entire list of games
# to our initial pipeline.
games = ...   # full list of games
pipeline = ScorePipeline(games)
pipeline.start()