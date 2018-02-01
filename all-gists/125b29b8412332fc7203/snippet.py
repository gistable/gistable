import re
import operator
import random


# Exception to throw if the algorithm breaks like a condom on prom night
class AlgorithmFailException(Exception):
    def __init__(self):
        Exception.__init__(self)


# The core class of this project, learns based off input of sentences, and can then obfuscate and deobfuscate data
class MarkovKeyState:
    def __init__(self):
        """
        It is a constructor that takes no arguments, why do you care about what it does???
        :return:
        """
        self.words = set()
        # Set the --terminate-- character (acts as the first and last character of a sentence)
        self.raw_scores = {"--terminate--": {}}

    def learn_sentence(self, sentence):
        """
        Learn based on the input sentence.

        :param sentence: Space separated sentence to apply to Markov model
        :return: No relevant return data
        """
        # Split the sentence into words/parts
        parts = re.findall(r"\w[\w']*", sentence.lower())
        if len(parts) == 0:
            return

        # This is a speed optimized method to increment the relation count between --terminate-- and the last part
        try:
            self.raw_scores[parts[-1]]["--terminate--"] += 1
        except KeyError:
            try:
                self.raw_scores[parts[-1]]["--terminate--"] = 1
            except KeyError:
                self.raw_scores[parts[-1]] = {"--terminate--": 1}

        # Iterate through all the parts, and increment the relation counts for all adjacent parts
        last = "--terminate--"
        for x in xrange(len(parts)):
            current = parts[x]
            try:
                self.raw_scores[last][current] += 1
            except KeyError:
                try:
                    self.raw_scores[last][current] = 1
                except KeyError:
                    self.raw_scores[last] = {current: 1}
            last = current

        # If any of the parts of this sentence don't end up in the database, something is broken in the code
        for part in parts:
            if part not in self.raw_scores:
                raise

    def print_most_likely_sentence(self):
        """
        This function is mostly for testing/fun.  It generates the most likely sentence from the Markov model
        :return: The sentence
        """
        last = "--terminate--"
        parts = []

        while True:
            # Get the most likely next word, and set as current
            current = sorted(self.raw_scores[last].items(), key=operator.itemgetter(1))[-1][0]

            # If the current value is --terminate--, we are done generating the sentence
            if current == "--terminate--":
                break

            parts.append(current)

            # Set current to last as we move into the next iteration
            last = current

        return " ".join(parts)

    def create_byte(self, last, byte_value):
        """
        Internal function to generate an obfuscated byte, which can be represented by multiple words/sentences

        :param last: The last word in the current obfuscated sentence
        :param byte_value: The byte value to append
        :return: A string of words to append
        """
        words = []
        # Do we need to use a long value or can we use a short value
        if len(self.raw_scores[last].items()) < 256:
            # It is feasible to fail to find a valid result, generally we just need to try again though
            try_again = True
            while try_again:
                try:
                    # We start with last in our word list since we care about the transition between words, not words
                    words_to_use = [last]

                    # Since we can potentially spread the value over various word transitions, we maintain a remaining
                    # value left to represent
                    remaining_value = byte_value

                    # Loop until we have our words, or we crap out
                    while True:
                        count = 0

                        # Get the total possibility count, the total needs to be over 256 to possibly represent our byte
                        for word in words_to_use:
                            count += len(self.raw_scores[word].items())

                        if count < 256:
                            # we need another word
                            current_list = sorted(
                                self.raw_scores[words_to_use[-1]].items(),
                                key=operator.itemgetter(1)
                            )[::-1]

                            # we need whichever is smaller, the remaining value or
                            # the length of values for the next word
                            upper_bound = remaining_value if remaining_value < len(current_list) - 1 else len(
                                current_list) - 1

                            # Pick a random word that does not result in us going over our remaining value
                            if upper_bound < 2:
                                index = 0
                            else:
                                index = random.randint(0, upper_bound)

                            # Decrement remaining value and push our word to our list of words
                            remaining_value -= index
                            words_to_use.append(current_list[index][0])
                        else:
                            # We have enough words
                            current_list = sorted(
                                self.raw_scores[words_to_use[-1]].items(),
                                key=operator.itemgetter(1)
                            )[::-1]

                            # If this is true, the algo has failed going down this random path
                            if len(current_list) < remaining_value + 1:
                                raise AlgorithmFailException()

                            # Push our most common last word to terminate our long value
                            words_to_use.append(current_list[remaining_value][0])

                            # Clean out the "last" argument from list
                            words = words_to_use[1:]
                            try_again = False
                            break
                except AlgorithmFailException:
                    try_again = True
        else:
            # w00t, we can use a short value!
            words.append(sorted(self.raw_scores[last].items(), key=operator.itemgetter(1))[::-1][byte_value][0])

        return words

    def obfuscate_string(self, s):
        """
        Obfuscate the input binary string with the Markov model

        :param s: Input string, can be binary string, we immediately convert to ints anyways
        :return: The obfuscated string
        """
        # Convert each byte of the string to an integer
        parts = map(ord, list(s))

        # Start off with a random first word (word following --terminate--)
        result = self.create_byte("--terminate--", random.randint(0, 256))
        last = result[-1]

        for x in parts:
            # This function is deceptively simple because 99% of the work is done in create_byte
            to_append = self.create_byte(last, x)

            for current in to_append:
                # If its a --terminate--, add in a period, else, add in the word
                if current != "--terminate--":
                    result.append(current)
                else:
                    result.append(". ")
                last = current

        # Join it all into a string
        return " ".join(result)

    def deobfuscate_string(self, s):
        """
        Well...now we need to be able to deobfuscate a string, right?

        :param s: The string to deobfuscate
        :return: The deobfuscated string
        """
        # Split it up by spaces into words
        parts = s.split(' ')

        # Start our loop out with last being the first word in the string
        last = parts.pop(0)
        # Get our last_list based on the words that can follow last
        last_list = sorted(self.raw_scores[last].items(), key=operator.itemgetter(1))[::-1]
        result = []

        running_values = None
        running_list_lengths = None
        running_value = None

        # Loop until we have no words left
        while len(parts) != 0:
            # Once you pop, you just can't stop
            current_word = parts.pop(0)

            # Convert .'s to --terminate--, as . is our terminator (I'll be back...)
            if current_word == ".":
                current_word = "--terminate--"

            # If it is an empty string, then we should just move on and pretend nothing happened here
            if current_word == "":
                continue

            # Grab the list of words that can follow our current word
            current_list = sorted(self.raw_scores[current_word].items(), key=operator.itemgetter(1))[::-1]
            current_value = None

            # We need the value of the current word
            for x in xrange(len(last_list)):
                if last_list[x][0] == current_word:
                    current_value = x
                    break

            # The multiple word transitions make everything way more complicated
            if running_values is not None:
                # Keep pushing lengths of potential values until we get over 256
                running_list_lengths.append(len(last_list))
                running_values.append(current_value)
                if sum(running_list_lengths) >= 256:
                    # We made it!  Now add the running value and start again
                    result.append(sum(running_values))
                    # running_value = sum(running_values)
                    running_list_lengths = None
                    running_values = None
            elif running_value is not None:
                # I think this is deprecated, but I wrote this a while ago
                result.append(current_value + running_value)
                running_value = None
            elif len(last_list) < 256:
                # Keep adding to the running values, we aren't home yet
                running_values = [current_value]
                running_list_lengths = [len(last_list)]
            else:
                # Good old simple single word transition byte, reminds me of a simpler time
                # Back before I decided to support Markov models which did not have sufficient relations between words
                result.append(current_value)

            last = current_word
            last_list = current_list

        # Shake out the remaining drop
        if running_value is not None:
            result.append(running_value)

        # Shake out the remaining drops
        if running_values is not None:
            result.append(sum(running_values))

        # Join the ints together as chrs, to live in harmony forevaaaa
        return "".join(map(chr, result))


if __name__ == "__main__":
    # Regular expression to split our training files on
    split_regex = r'\.'

    # File/book to read for training the Markov model (will be read into memory)
    training_file = "98.txt"

    # Obfuscating Markov engine
    m = MarkovKeyState()

    # Read the shared key into memory
    with open(training_file, "r") as f:
        text = f.read()

    # Split learning data into sentences, in this case, based on periods.
    map(m.learn_sentence, re.split(split_regex, text))

    # Our data to obfuscate
    test_string = "This is a test message to prove the concept."
    print "Original string: {0}".format(test_string)

    # Obfuscate the data
    s = m.obfuscate_string(test_string)
    print "Obfuscated string: {0}".format(s)

    # Other Markov engine
    m2 = MarkovKeyState()

    # Split learning data into sentences, in this case, based on periods.
    map(m2.learn_sentence, re.split(split_regex, text))

    # Print out the deobfuscated string
    print "Deobfuscated string: {0}".format(m2.deobfuscate_string(s))
