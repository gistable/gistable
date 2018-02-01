MEMORY = '<memory>'
class FuckItEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except RuntimeError:
            return '<recur>'
        except MemoryError:
            return MEMORY
        except TypeError:
            if hasattr(obj, '__dict__'):
              return obj.__dict__
            else:
              return repr(obj)
              
json.dump(config, open('config.json', 'wb'), cls=FuckItEncoder, indent=2)