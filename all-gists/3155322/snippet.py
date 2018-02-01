# flask-restless.views.API
class API(ModelView):
  def get(self, instid, **kwargs):
    <...>
    self._search(**kwargs)
    <...>

  def _search(self, **kwargs):
    <...>
    self._before_search(data, **kwargs)
    <...>

# Extending class
class ItemAPI(API):
  def _before_search(data, user_id, **kwargs):
    data['filters'].append({
                               'name': 'owner_id',
                               'op': 'equals',
                               'val': user_id
                               })
    return True

# Actual API
manager.create_api(
                   Item, 
                   methods=['GET', 'POST', 'PUT', 'DELETE'], 
                   api_class=ItemAPI,
                   collection_name='/user/<int:user_id>/items')