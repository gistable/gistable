
class SecretFirst(object):
    def __secret(self):
        print('__secret')

    def _SecretFirst__secret(self):
        print('_SecretFirst__secret')

class SecretSecond(object):
    def _SecretSecond__secret(self):
        print('_SecretSecond__secret')

    def __secret(self):
        print('__secret')

if __name__ == '__main__':
    sf = SecretFirst()
    print(dir(sf))
    sf._SecretFirst__secret() # -> _SecretFirst__secret

    ss = SecretSecond()
    print(dir(ss))
    ss._SecretSecond__secret() # -> __secret
