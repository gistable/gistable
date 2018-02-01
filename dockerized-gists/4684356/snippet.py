"""
Demonstration of ways to implement this API:
    sanitize(user_input, stop_words)

Related discussions:
    - Modifying a list while looping over it:
        - http://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating-in-python

    - Remove all occurences of a value in a list:
        - http://stackoverflow.com/questions/1157106/remove-all-occurences-of-a-value-from-a-python-list
"""
import sys
from timeit import timeit
from functools import partial
from collections import deque


def sanitize_1(user_input, stop_words):
    """Sanitize using set subtraction then wrapped in list()"""

    # Downsides:
    #   - Sets are unordered so if user_input was a sentence we lose the
    #     ordering because set difference will create a new set and not
    #     maintain ordering.

    return list(set(user_input) - set(stop_words))


def sanitize_2(user_input, stop_words):
    """Sanitize using intersection and list.remove()"""
    # Downsides:
    #   - Looping over list while removing from it?
    #     http://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating-in-python

    stop_words = set(stop_words)
    for sw in stop_words.intersection(user_input):
        while sw in user_input:
            user_input.remove(sw)

    return user_input


def sanitize_3(user_input, stop_words):
    """Sanitize using standard lists"""
    new_list = []
    for w in user_input:
        if w not in stop_words:
            new_list.append(w)
    return new_list


def sanitize_4(user_input, stop_words):
    """Sanitize using standard list comprehension"""
    return [w for w in user_input if w not in stop_words]


def sanitize_5(user_input, stop_words):
    """Sanitize using collection.deque and list comprehension"""
    user_input = deque(user_input)
    stop_words = deque(stop_words)
    return [w for w in user_input if w not in stop_words]


def _sanitize_funcs():
    """Get all the sanitize functions in scope"""
    module = sys.modules[__name__]

    for obj in sorted(vars(module).values()):
        if callable(obj) and obj.__name__.startswith('sanitize_'):
            yield obj


def get_functions(user_input, stop_words):
    """Build a list of the sanitize functions with parameters"""
    functions = []

    for f in _sanitize_funcs():
        functions.append(partial(f, user_input, stop_words))

    return functions



def check_results(functions):
    """Test the results of each function"""
    for f in functions:
        print '%s - %s' % (f.func.__name__, f())


def check_performance(functions, number=1000000):
    """Test the performance of each function"""
    for f in functions:
        print '%s [%f] %s' % (f.func.__name__, timeit(f, number=number), f.func.__doc__)


def main():
    # number of iterations for timeit
    # timeit defaults to 1,000,000 but change this number
    # to see different variations
    number = 10000

    # a list of stop words to be removed
    stop_words = ['the', 'that', 'to', 'as', 'there', 'has', 'and', 'or', 'is', 'not', 'a', 'of', 'but', 'in', 'by', 'on', 'are', 'it', 'if']

    user_input = 'the cat walked down the road.'.split()
    functions = get_functions(user_input, stop_words)

    print 'Timing with %d iterations' % number

    print '----- Function Results -----'
    check_results(functions)

    print '----- Function Performance -----'
    check_performance(functions, number)

    print '-' * 10

    user_input = """
        Proficient reading depends on the ability to recognize words quickly and effortlessly.[2] If word recognition is difficult, students use too much of their processing capacity to read individual words, which interferes with their ability to comprehend what is read.
        Many educators in the USA believe that students need to learn to analyze text (comprehend it) even before they can read it on their own, and comprehension instruction generally begins in pre-Kindergarten or Kindergarten. But other US educators consider this reading approach to be completely backward for very young children, arguing that the children must learn how to decode the words in a story through phonics before they can analyze the story itself.
        During the last century comprehension lesson/s usually comprised students answering teachers' questions, writing responses to questions on their own, or both.[citation needed] The whole group version of this practice also often included "Round-robin reading", wherein teachers called on individual students to read a portion of the text (and sometimes following a set order). In the last quarter of the 20th century, evidence accumulated that the read-test methods assessed comprehension more than they taught it. The associated practice of "round robin" reading has also been questioned and eliminated by many educators.
        Instead of using the prior read-test method, research studies have concluded that there are much more effective ways to teach comprehension. Much work has been done in the area of teaching novice readers a bank of "reading strategies," or tools to interpret and analyze text.[3] There is not a definitive set of strategies, but common ones include summarizing what you have read, monitoring your reading to make sure it is still making sense, and analyzing the structure of the text (e.g., the use of headings in science text). Some programs teach students how to self monitor whether they are understanding and provide students with tools for fixing comprehension problems.
        Instruction in comprehension strategy use often involves the gradual release of responsibility, wherein teachers initially explain and model strategies. Over time, they give students more and more responsibility for using the strategies until they can use them independently. This technique is generally associated with the idea of self-regulation and reflects social cognitive theory, originally conceptualized by
    """.lower().split()
    functions = get_functions(user_input, stop_words)   

    print '----- Function Results -----'
    check_results(functions)

    print '----- Function Performance -----'
    check_performance(functions, number)


if __name__ == "__main__":
    main()