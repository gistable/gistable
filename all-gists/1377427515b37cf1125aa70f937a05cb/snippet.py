"""
A basic Shopware 5 API client I threw together for a project. There's a few gotchas in here that
I thought are useful enough to others to publish it. But please take it as is - it works for my
purpose (processing Shopware articles daily), I make no claims beyond that.
"""

import os
import requests
from requests.auth import HTTPDigestAuth

# This is a Shopware constant, mapping to 'Deutsch' root category
ROOT_ID = 3


def client_from_env():
    """
    Returns an APIClient instance constructed from settings in the environment variables.
    """
    api_credentials = os.environ.get('SHOPWARE_API_CREDENTIALS')
    api_base_url = os.environ.get('SHOPWARE_API_URL')
    if not api_credentials or not api_base_url:
        raise ValueError(
            'You need to set SHOPWARE_API_CREDENTIALS to the format username:password and '
            'SHOPWARE_API_URL to the base API URL.')
    return APIClient(api_base_url, *api_credentials.split(':', 1))


class APIClient:

    def __init__(self, base_url, username, token):
        self.base_url = base_url
        self.auth = HTTPDigestAuth(username, token)

    def _make_request(self, method, url, payload=None):
        response = requests.request(method, self.base_url + url, auth=self.auth, json=payload)
        try:
            json_response = response.json()
        except ValueError:
            return response
        else:
            if not json_response['success']:
                raise ValueError('Failed response: %s' % json_response)
            return json_response

    def get(self, url):
        return self._make_request('get', url)

    def post(self, url, data):
        return self._make_request('post', url, payload=data)

    def put(self, url, data):
        return self._make_request('put', url, payload=data)

    def delete(self, url, data=None):
        return self._make_request('delete', url, data)

    # Articles

    def get_article(self, article_id):
        return self.get('/articles/%s' % article_id)['data']

    def get_articles(self):
        limit = 100000
        response = self.get('/articles?limit=%s' % limit)
        if response['total'] >= limit:
            # Sorry for being lazy. Use the start= query kwarg for pagination.
            # https://forum.shopware.com/discussion/10484/geloest-mehr-als-1000-artikel-mit-rest-api-laden
            raise ValueError(
                'You have more than %s articles. You need to implement pagination in the '
                'get_articles method.')
        return response['data']

    def delete_article(self, article_id):
        return self.delete('/articles/%s' % article_id)

    def create_article(self, *args, **kwargs):
        if 'article_id' in kwargs:
            raise TypeError('article_id must not be included')
        return self._update_or_create_article(*args, **kwargs)

    def update_article(self, article_id, *args, **kwargs):
        kwargs['article_id'] = article_id
        return self._update_or_create_article(*args, **kwargs)

    def _update_or_create_article(
            self, description, sku, price, category_ids, supplier, name=None,
            image_urls=None, active=None, tax=19, num_in_stock=1, purchase_price=None,
            article_id=None, price_group_id=None, last_stock=False, supplier_sku=None,
            shipping_time_days=None):
        """
        Updates if article ID is given, creates otherwise.
        """
        # http://forum.shopware.com/discussion/8497/rest-api-artikelbilder-setzen
        categories = [{'id': category_id} for category_id in category_ids]
        data = {
            'tax': tax,
            'descriptionLong': description,
            'lastStock': last_stock,  # "Abverkauf"
            'mainDetail': {
                'number': sku,  # "Artikelnummer"
                'inStock': num_in_stock,
                'prices': [
                    {
                        'price': price,
                    }
                ],
                'purchasePrice': purchase_price or '0',
            },
            'categories': categories,
            'supplier': supplier,
        }
        if name is None:
            if not article_id:
                raise ValueError("A product name is needed when creating.")
        else:
            data['name'] = name
        if active is not None:
            # No idea why we need to double this, but we do. A kingdom for good API docs.
            data['active'] = data['mainDetail']['active'] = active
        if image_urls:
            data['images'] = [{'link': url} for url in image_urls]
        if price_group_id is not None:
            data['priceGroupActive'] = True
            data['priceGroupId'] = price_group_id
        if supplier_sku is not None:
            # "Herstellernummer"
            data['mainDetail']['supplierNumber'] = supplier_sku
        if shipping_time_days:
            data['mainDetail']['shippingTime'] = shipping_time_days
        if article_id:
            # Updating
            return self.put('/articles/%s' % article_id, data)['data']['id']
        else:
            # Creating
            return self.post('/articles', data)['data']['id']

    def delete_all_articles(self, ):
        articles = self.get_articles()
        for article in articles:
            self.delete_article(article['id'])
        return articles

    # Categories

    def get_categories(self):
        """
        Returns the tree of categories.
        :return:
        """
        limit = 100000
        response = self.get('/categories?limit=%s' % limit)
        if response['total'] >= limit:
            # Sorry for being lazy. Use the start= query kwarg for pagination.
            # https://forum.shopware.com/discussion/10484/geloest-mehr-als-1000-artikel-mit-rest-api-laden
            raise ValueError(
                'You have more than %s categories. You need to implement pagination in the '
                'get_categories method.')
        return response['data']

    def get_category(self, category_id):
        return self.get('/categories/%s' % category_id)['data']

    def find_category_ids(self, name, parent_id=None):
        """
        Returns all categories matching the name. Optionally also matches on parent_id. If not
        given, all name matches are returned.
        """
        matches = []
        categories = self.get_categories()
        for category in categories:
            if category['name'] == name:
                if parent_id is None or category['parentId'] == parent_id:
                    matches.append(category['id'])
        return matches

    def create_category(self, name, parent_id):
        """
        Creates a category. Use ROOT_ID for parent_id if creating a root category.
        """
        created = self.post('/categories', {
            'name': name,
            'parentId': parent_id,
        })
        return created['data']['id']

    def get_or_create_category(self, name, parent_id):
        """
        Returns category ID of category with supplied name. Created if necessary.
        """
        matches = self.find_category_ids(name, parent_id)
        if len(matches) > 1:
            raise ValueError(
                "There are %s categories with name '%s', expected only 1 or less." %
                (len(matches), name)
            )
        elif len(matches) == 1:
            return matches[0]
        else:
            self.create_category(name, parent_id)

    def update_category_title(self, category_id, new_title):
        return self.put('/categories/%s' % category_id, {'name': new_title})

    def delete_category(self, category_id):
        return self.delete('/categories/%s' % category_id)

    # Misc

    def get_customer_groups(self):
        # TODO: Check for limit
        return self.get('/customerGroups')['data']