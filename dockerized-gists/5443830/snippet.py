import pickle

def testpickle(klass):
    for x in klass.objects.all():
        try:
            y = pickle.dumps(x)
            assert(x == pickle.loads(y))
            print "Successfully pickled %r" % x
        except AssertionError as ex:
            print 'Assertion error on unpickling: %s' % ex
        except pickle.PickleError as ex:
            print 'Unable to pickle / unpickle object %s:\n%s' % (x, ex)
