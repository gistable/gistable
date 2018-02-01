class iter_shuffle_batch_tensors(Iterator):
    """Combine `iter_tensors_slice` and `iter_shuffle_batch_range`.

    Args:
        See `iter_tensors_slice` and `iter_shuffle_batch_range`.

    Output:
        See `iter_shuffle_batch_range`.
    """

    def __init__(self, tensors, batch_size=None, shuffle=True,
                 allow_smaller_final_batch=False, num_cycles=1, axis=0):
        self.tensors = as_list(tensors)
        check_tensors_samesize(self.tensors, axis=axis)
        def reset(self):
            self._slices = iter_shuffle_batch_range(
                get_tensors_size(self.tensors, axis=axis),
                batch_size=batch_size,
                shuffle=shuffle,
                allow_smaller_final_batch=allow_smaller_final_batch,
                num_cycles=num_cycles)
            self._it = iter_tensors_slice(tensors, self._slices, axis=axis)
        self.reset = types.MethodType(reset, self)
        self.reset()

    def __next__(self):
        return next(self._it)

    @property
    def shuffle(self):
        return self._slices.shuffle

    @property
    def batch_size(self):
        return self._slices.batch_size

    @property
    def size(self):
        return self._slices.size

    @property
    def allow_smaller_final_batch(self):
        return self._slices.allow_smaller_final_batch

    @property
    def num_cycles(self):
        return self._slices.num_cycles

    def __len__(self):
        return len(self._slices)

    @property
    def steps_per_epoch(self):
        return self._slices.steps_per_epoch

    @property
    def epoch(self):
        return self._slices.epoch

    @property
    def step(self):
        return self._slices.step
