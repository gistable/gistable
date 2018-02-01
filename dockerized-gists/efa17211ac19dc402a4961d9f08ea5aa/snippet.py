"""Count words."""

def count_words(s, n):
    """Return the n most frequently occuring words in s."""
    
    # TODO: Count the number of occurences of each word in s
    words = s.split(" ")
    # set comprehension so we only have unique values
    word_frequencies = {word: words.count(word) for word in words}
    word_frequency_tuples = [(word, count) for word, count in word_frequencies.items()]
    
    # TODO: Sort the occurences in descending order (alphabetically in case of ties)
    word_frequency_tuples.sort(key=lambda tup: (-tup[1], tup[0]))
    
    # TODO: Return the top n words as a list of tuples (<word>, <count>)
    top_n = word_frequency_tuples[:n]
    return top_n


def test_run():
    """Test count_words() with some inputs."""
    print count_words("cat bat mat cat bat cat", 3)
    print count_words("betty bought a bit of butter but the butter was bitter", 3)


if __name__ == '__main__':
    test_run()
