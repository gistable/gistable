"""Implement a memorable ID string.

The original idea for this comes from Asana where it is documented on their
blog:
    http://blog.asana.com/2011/09/6-sad-squid-snuggle-softly/

There are other partial implementations of this and can be found here:
    Node.js: https://github.com/linus/greg
    Java: https://github.com/PerWiklander/IdentifierSentence

In this module you will find:

    IdSentence: The base class for all ID sentences.
    IntSentence: An implementation of IdSentence for 32 bit integers.
"""

import math
import random


class IdSentence(object):
    """The base class for all ID sentences.

    This provides all of the necessary helper functionality to turn IDs into
    sentences and sentences into IDs.
    """

    __id_generator__ = None
    """The generator to use to generate new IDs.
    The implementer needs to provide this."""

    __sentence__ = None
    """The sentence structure to be generated.
    The implementer needs to provide this."""

    __sentence_words__ = None
    """The mapping between the sentence parts and the words to use.
    The implementer needs to provide this."""

    def __init__(self):
        self._part_n_words = dict()
        self._part_bits = dict()
        for part in self.__sentence__:
            n_words = len(self.__sentence_words__[part])
            self._part_n_words[part] = n_words
            if not (n_words > 0 and ((n_words & (n_words - 1)) == 0)):
                raise ValueError(
                    "{} part has {} words, which is not a power of 2".\
                        format(part, n_words))
            self._part_bits[part] = int(math.log(self._part_n_words[part], 2))
        self.__total_bits__ = \
            sum([v for v in self._part_bits.values()])

    def sentence_to_id(self, sentence):
        """Take the sentence and convert it the ID.

        Args:
            sentence: The sentence to convert into an ID
        Returns:
            The ID represented by the sentence
        """
        idxs = self._sentence_to_idxs(sentence)
        id = 0
        for i in range(len(idxs)):
            part = self.__sentence__[i]
            id = (id << self._part_bits[part]) + idxs[i]
        return id

    def id_to_sentence(self, id):
        """Take the ID and convert it a sentence.

        Args:
            id: The ID to convert into a sentence
        Returns:
            The sentence represented by the ID
        """
        idxs = self._id_to_idxs(id)
        sentence = []
        for i in range(len(self.__sentence__)):
            part = self.__sentence__[i]
            values = self.__sentence_words__[part]
            sentence.append(str(values[idxs[i]]))
        return ' '.join(sentence)

    def generate(self):
        """Generate an ID and the corresponding sentence.

        Args:
            None
        Returns:
            A tuple containing the id and the sentence
        """
        id = self.__id_generator__()
        sentence = self.id_to_sentence(id)
        return (id, sentence)

    def _id_to_idxs(self, id):
        """Take the ID and convert it to indices into the sentence words.

        Args:
            id: The ID to convert into indices
        Returns:
            A list of indices into the sentence words
        """
        shift = self.__total_bits__
        idxs = []
        for part in self.__sentence__:
            shift -= self._part_bits[part]
            mask = (self._part_n_words[part] - 1) << shift
            idxs.append((id & mask) >> shift)
        return idxs

    def _sentence_to_idxs(self, sentence):
        """Take the sentence and convert it to indices into the sentence words.

        Args:
            sentence: The sentence to convert into indices
        Returns:
            A list of indices into the sentence words
        """
        split_sentence = sentence.split(u" ")
        if len(split_sentence) != len(self.__sentence__):
            raise ValueError((
                "The sentence must have {} parts and be of the form {}").\
                    format(len(self.__sentence__), self.__sentence__))
        idxs = []
        for i in range(len(self.__sentence__)):
            part = self.__sentence__[i]
            idxs.append(self.__sentence_words__[part].index(split_sentence[i]))
        return idxs


class IntIdSentence(IdSentence):
    """An implementation of IdSentence for 32 bit integers."""

    __id_generator__ = lambda self: int(random.getrandbits(32))
    __sentence__ = ('number', 'adjective', 'noun', 'verb', 'adverb')
    __sentence_words__ = dict(
        number=[str(x) for x in range(2, 34)],
        adjective=('adorable', 'adventurous', 'alluring', 'amazing',
            'ambitious', 'amusing', 'astonishing', 'attractive', 'awesome',
            'bashful', 'bawdy', 'beautiful', 'bewildered', 'bizarre', 'bouncy',
            'brainy', 'brave', 'brawny', 'burly', 'capricious', 'careful',
            'caring', 'cautious', 'charming', 'cheerful', 'chivalrous',
            'classy', 'clever', 'clumsy', 'colossal', 'cool', 'coordinated',
            'courageous', 'cuddly', 'curious', 'cute', 'daffy', 'dapper',
            'dashing', 'dazzling', 'delicate', 'delightful', 'determined',
            'eager', 'embarrassed', 'enchanted', 'energetic', 'enormous',
            'entertaining', 'enthralling', 'enthusiastic', 'evanescent',
            'excited', 'exotic', 'exuberant', 'exultant', 'fabulous', 'fancy',
            'festive', 'finicky', 'flashy', 'flippant', 'fluffy', 'fluttering',
            'funny', 'furry', 'fuzzy', 'gaudy', 'gentle', 'giddy', 'glamorous',
            'gleaming', 'goofy', 'gorgeous', 'graceful', 'grandiose', 'groovy',
            'handsome', 'happy', 'hilarious', 'honorable', 'hulking',
            'humorous', 'industrious', 'incredible', 'intelligent', 'jazzy',
            'jolly', 'joyous', 'kind', 'macho', 'magnificent', 'majestic',
            'marvelous', 'mighty', 'mysterious', 'naughty', 'nimble', 'nutty',
            'oafish', 'obnoxious', 'outrageous', 'pretty', 'psychedelic',
            'psychotic', 'puzzled', 'quirky', 'quizzical', 'rambunctious',
            'remarkable', 'sassy', 'shaggy', 'smelly', 'sneaky', 'spiffy',
            'swanky', 'sweet', 'swift', 'talented', 'thundering', 'unkempt',
            'upbeat', 'uppity', 'wacky', 'waggish', 'whimsical', 'wiggly',
            'zany'),
        noun=('aardvarks', 'alligators', 'alpacas', 'anteaters', 'antelopes',
            'armadillos', 'baboons', 'badgers', 'bears', 'beavers',
            'boars', 'buffalos', 'bulls', 'bunnies', 'camels', 'cats',
            'chameleons', 'cheetahs', 'centaurs', 'chickens', 'chimpanzees',
            'chinchillas', 'chipmunks', 'cougars', 'cows', 'coyotes', 'cranes',
            'crickets', 'crocodiles', 'deers', 'dinasaurs', 'dingos', 'dogs',
            'donkeys', 'dragons', 'elephants', 'elves', 'ferrets', 'flamingos',
            'foxes', 'frogs', 'gazelles', 'giraffes', 'gnomes', 'gnus', 'goats',
            'gophers', 'gorillas', 'hamsters', 'hedgehogs', 'hippopotamus',
            'hobbits', 'hogs', 'horses', 'hyenas', 'ibexes', 'iguanas',
            'impalas', 'jackals', 'jackalopes', 'jaguars', 'kangaroos',
            'kittens', 'koalas', 'lambs', 'lemmings', 'leopards', 'lions',
            'ligers', 'lizards', 'llamas', 'lynxes', 'meerkat', 'moles',
            'mongooses', 'monkeys', 'moose', 'mules', 'newts', 'okapis',
            'orangutans', 'ostriches', 'otters', 'oxes', 'pandas', 'panthers',
            'peacocks', 'pegasuses', 'phoenixes', 'pigeons', 'pigs',
            'platypuses', 'ponies', 'porcupines', 'porpoises', 'pumas',
            'pythons', 'rabbits', 'raccoons', 'rams', 'reindeers',
            'rhinoceroses', 'salamanders', 'seals', 'sheep', 'skunks',
            'sloths', 'slugs', 'snails', 'snakes', 'sphinxes', 'sprites',
            'squirrels', 'takins', 'tigers', 'toads', 'trolls', 'turtles',
            'unicorns', 'walruses', 'warthogs', 'weasels', 'wolves',
            'wolverines', 'wombats', 'woodchucks', 'yaks', 'zebras'),
        verb=('ambled', 'assembled', 'burst', 'babbled', 'charged', 'chewed',
            'clamored', 'coasted', 'crawled', 'crept', 'danced', 'dashed',
            'drove', 'flopped', 'galloped', 'gathered', 'glided', 'hobbled',
            'hopped', 'hurried', 'hustled', 'jogged', 'juggled', 'jumped',
            'laughed', 'marched', 'meandered', 'munched', 'passed', 'plodded',
            'pranced', 'ran', 'raced', 'rushed', 'sailed', 'sang', 'sauntered',
            'scampered', 'scurried', 'skipped', 'slogged', 'slurped', 'spied',
            'sprinted', 'spurted', 'squiggled', 'squirmed', 'stretched',
            'strode', 'strut', 'swam', 'swung', 'traveled', 'trudged',
            'tumbled', 'twisted', 'wade', 'wandered', 'whistled', 'wiggled',
            'wobbled', 'yawned', 'zipped', 'zoomed'),
        adverb=('absentmindedly', 'adventurously', 'angrily', 'anxiously',
            'awkwardly', 'bashfully', 'beautifully', 'bleakly', 'blissfully',
            'boastfully', 'boldly', 'bravely', 'briskly', 'calmly',
            'carefully', 'cautiously', 'cheerfully', 'cleverly', 'cluelessly',
            'clumsily', 'coaxingly', 'colorfully', 'coolly', 'courageously',
            'curiously', 'daintily', 'defiantly', 'deliberately',
            'delightfully', 'diligently', 'dreamily', 'drudgingly', 'eagerly',
            'effortlessly', 'elegantly', 'energetically', 'enthusiastically',
            'excitedly', 'fervently', 'foolishly', 'furiously', 'gallantly',
            'gently', 'gladly', 'gleefully', 'gracefully', 'gratefully',
            'happily', 'hastily', 'haphazardly', 'hungrily', 'innocently',
            'inquisitively', 'intensely', 'jokingly', 'joshingly', 'joyously',
            'jovially', 'jubilantly', 'kiddingly', 'knavishly', 'knottily',
            'kookily', 'lazily', 'loftily', 'longingly', 'lovingly', 'loudly',
            'loyally', 'madly', 'majestically', 'merrily', 'mockingly',
            'mysteriously', 'nervously', 'noisily', 'obnoxiously', 'oddly',
            'optimistically', 'overconfidently', 'outside', 'owlishly',
            'patiently', 'playfully', 'politely', 'powerfully', 'purposefully',
            'quaintly', 'quarrelsomely', 'queasily', 'quickly', 'quietly',
            'quirkily', 'quizzically', 'rapidly', 'reassuringly', 'recklessly',
            'reluctantly', 'reproachfully', 'sadly', 'scarily', 'seriously',
            'shakily', 'sheepishly', 'shyly', 'silently', 'sillily',
            'sleepily', 'slowly', 'speedily', 'stealthily', 'sternly',
            'suspiciously', 'sweetly', 'tenderly', 'tensely', 'thoughtfully',
            'triumphantly', 'unabashedly', 'unaccountably', 'urgently',
            'vainly', 'valiantly', 'victoriously', 'warmly', 'wearily',
            'youthfully', 'zestfully'))
    