# This to illustrate the idea how deep BiRNN will be implemented in Blocks.

class RecurrentWithFork(Initializable):

    @lazy(allocation=['input_dim'])
    def __init__(self, recurrent, input_dim, **kwargs):
        super(RecurrentWithFork, self).__init__(**kwargs)
        self.recurrent = recurrent
        self.input_dim = input_dim
        self.fork = Fork(
            [name for name in self.recurrent.sequences
             if name != 'mask'],
             prototype=Linear())
        self.children = [recurrent.brick, self.fork]

    def _push_allocation_config(self):
        self.fork.input_dim = self.input_dim
        self.fork.output_dims = [self.recurrent.brick.get_dim(name)
                                 for name in self.fork.output_names]

    @application(inputs=['input_', 'mask'])
    def apply(self, input_, mask=None, **kwargs):
        return self.recurrent(
            mask=mask, **dict_union(self.fork.apply(input_, as_dict=True),
                                    kwargs))

    @apply.property('outputs')
    def apply_outputs(self):
        return self.recurrent.states


class Encoder(Initializable):

    def __init__(self, enc_transition, dim, dim_input, depth, **kwargs):
        super(Encoder, self).__init__(**kwargs)
        bidir = Bidirectional(
            RecurrentWithFork(
                enc_transition(dim=dim, activation=Tanh()).apply,
                dim_input,
                name='with_fork'),
            name='bidir0')

        self.children = [bidir]
        for layer in range(1, depth):
            self.children.append(copy.deepcopy(bidir))
            for child in self.children[-1].children:
                child.input_dim = 2 * dim
            self.children[-1].name = 'bidir{}'.format(layer)

    @application
    def apply(self, input_, mask=None):
        for bidir in self.children:
            input_ = bidir.apply(input_, mask)
        return input_
