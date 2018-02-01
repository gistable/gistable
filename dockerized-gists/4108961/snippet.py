# -*- coding: utf-8 -*-
"""
This is an example of a basic optical character recognition system.
Some components, such as the featurizer, are missing, and have been replaced
with data that I made up.

This system recognizes words produced from an alphabet of 2 letters: 'l' and 'o'.
Words that can be recognized include, 'lol', 'lolol', 'and loooooll'.
We'll assume that this system is used to digitize hand-written notes by Redditors,
or something. 

"""

'''
The possible hidden states.
That is, each letter we are trying to recognize could be an 'l' or an 'o'.
'''
states = ('l', 'o',)

'''
Let's say that you have a featurizer (I don't) that creates a feature
vector from a black-and-white input image of a character.
This simple, imaginary featurizer samples 3 one-pixel-wide, vertical strips 
of the character image at fixed x positions. 

For example, the featurizer might look at the left-most column of the image, 
the right-most column, and the center column.
If the featurizer finds black pixels in the strip, it sets that element in the
feature vector to 1; otherwise, the element is set to zero. If many different
images for each character are examined, the featurizer may produce many different
feature vectors, as the images may use different fonts, font sizes, or may be
aligned differently. However, some feature vectors should be produced more
frequently for certain characters. For example, lower-case 'i's should 
infrequently have pixels in the left- or right-most columns, while 'o's should.

After examining many annotated images for each character in the lexicon, 
the featurizer can assign the probabilities of each feature vector corresponding
to each character.

The following are the probabilities that a hidden state emitted an observed state.
That is, these are the probabilities that each possible feature vector 
corresponds to 'l' or 'o'. The presence of black pixels in all three columns indicates
and 'o', but never an 'l'; the presence of black pixels in the last two columns could
indicate either an 'l' or an 'o'; etc.
'''
emission_probability = {
    'l': {000:0.2, 001:0.0, 010:0.4, 011:0.2, 100:0.1, 101:0.0, 110:0.1, 111:0.0},
    'o': {000:0.0, 001:0.05, 010:0.1, 011:0.25, 100:0.05, 101:0.0, 110:0.25, 111:0.3},
}

'''
The sequence of observations. That is, a sequence of one feature vector
produced for each input image of a character.
'''
observations = (010, 011, 011, 010, 111, 111, 011, 011, 111, 010)

'''
The probabilites of a hidden sequence beginning with each state. In this case,
we know that words begin with 'l' more frequently than with 'o'.
'''
start_probability = {'l': 0.9, 'o': 0.1}

'''
We know the probabilities of each state transitioning to each state.
Perhaps we sampled a Reddit comment thread, and found words including
'lol', 'lolol', and 'loloooool'.

Using these samples, we found that 'l' was usually followed by 'o', and
that 'o' was usually followed by 'o'.
'''
transition_probability = {
    'l': {'l':0.33, 'o':0.67},
    'o': {'l':0.40, 'o':0.60},
}

def viterbi(observations, states, start_probability, transition_probability, emission_probability):
    # The trellis consists of nodes for each possible state at each step in the hidden sequence.
    # Each node has a probability.
    # The edges connecting the nodes are transitions between states.
    trellis = [{}]
    # The current path through the trellis.
    path = {}

    # Add the probabilities of beginning the sequence with each possible state
    for state in states:
        trellis[0][state] = start_probability[state] * emission_probability[state][observations[0]]
        path[state] = [state]

    # Add probabilities for each subsequent state transitioning to each state.
    for observations_index in range(1,len(observations)):
        # Add a new path for the added step in the sequence.
        trellis.append({})
        new_path = {}
        # For each possible state,
        for state in states:
            # Find the most probable state of:
            # The previous most probable state's probability *
            # the probability of the previous most probable state transitioning to the predicted state *
            # The probability that the current observation corresponds to the predicted state
            (probability, possible_state) = max(
            [(trellis[observations_index-1][y0] * transition_probability[y0][state] 
            * emission_probability[state][observations[observations_index]], y0) for y0 in states])

            # Add the probability of the state occuring at this step of the sequence to the trellis.
            trellis[observations_index][state] = probability
            # Add the state to the current path
            new_path[state] = path[possible_state] + [state]

        path = new_path

    # Make a list of the paths that traverse the entire observation sequence and their probabilities,
    # and select the most probable.
    (probability, state) = max([(trellis[len(observations) - 1][state], state) for state in states])
    # The most probable path, and its probability.    
    return (probability, path[state])

print viterbi(observations, states, start_probability, transition_probability, emission_probability)

'''
Output:
(3.3929083008000003e-08, ['l', 'o', 'o', 'l', 'o', 'o', 'o', 'o', 'o', 'l'])
The most probable state for this sequence of observations is the word 'looloooool'.
'''