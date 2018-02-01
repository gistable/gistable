# coding: utf-8


def dict_to_format(log_dict):
    u"""
    辞書型のデータを、ロギングできるフォーマットに変更する

    >>> dict_to_format({"foo": 1, "bar": 2})
    'foo:1\\tbar:2'
    """
    return  "\t".join(
        ["%s:%s" % (k, v)for k, v in log_dict.items()])


def closure_logging(logger, name, **default_args):
    def _logging(**log_dict):
        merged_dict = dict(
            [("module", name), ] +
            default_args.items() +
            log_dict.items())
        logger.info(dict_to_format(merged_dict))
    return _logging


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    print dict_to_format({"foo": "bar"})
    _test()