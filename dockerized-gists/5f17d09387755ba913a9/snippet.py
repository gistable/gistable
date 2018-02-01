from hashlib import sha1


class YandexMoheyHash:
    """
    Integrity check for Yandex.Money HTTP-notifications
    Usage example:

    yahash = YandexMoheyHash(request.POST, settings.YANDEX_MONEY_SECRET)
    if yahash.check(request.POST['sha1_hash']):
        # process invoice
    """

    def __init__(self, query, secret):
        self.secret = secret
        self.hash_str = self.make_hash_str(query)

    def make_hash_str(self, query):
        hash_str = ''
        keys = ['notification_type', 'operation_id', 'amount',
                'currency', 'datetime', 'sender', 'codepro', 'label']
        for key in keys:
            value = query[key]
            if key == 'label':
                hash_str += self.secret + '&' + value
                continue
            hash_str += value + '&'
        return hash_str

    def make(self):
        return sha1(bytes(self.hash_str, 'utf-8')).hexdigest()

    def check(self, check):
        return self.make(query, secret) == check
