class Backend(object):
  """Allows access to backend and removes logic from handlers"""
  
  def __init__(self):
    """Inititalize with the variables you need"""
    self.__users_data = None
    self.db = Connection(
      options.db_host,
      options.db,
      user=options.db_user,
      password=options.db_password)

  @classmethod
  def instance(cls):
    """We only access one instance of backend"""
    if not hasattr(cls, "_instance"):
      cls._instance = cls()
    return cls._instance

  def __getattr__(self, name):
    """
    A very simple read-only ORM-like blanket method:
    Automatically associated methods with form:
      get_{entity}, get_{entity}s,
      get_{entity}_by_{column} and get_{entity}s_by_{column}
      
    eg get_user(id), get_users([id1, id2]), get_post_by_title("America, America")
      
    If no column is specified, it uses id by default.
    
    You may also pass in a fields **kwargs to determine which columns
    should be returned in the query.
    
    eg get_user_by_email("dlc@dlc.com", fields=["id","first_name"])
    """
    tokens = name.split("_")
    token_count = len(tokens)
    
    if token_count > 1 and tokens[0] == "get":
      entity, column_name, singular = (tokens[1], "id", False)
      if not entity.endswith("s"):
        singular = True
        entity = "%ss" % entity #tables are plural
      if token_count == 4 and tokens[2] == "by":
        column_name = tokens[3]

      def template_get_query(*args, **kwargs):
        if singular and not args[0]:
          """ If there was no parameter, return None"""
          return None

        if not singular and len(args[0]) == 0:
          """
          A set of entities was requested, but no parameters were given so
          return an empty list
          """
          return {}

        params_count = len(args[0]) if not singular else 1
        params = args[0] if not singular else [ args[0] ]
        fields = ["*"]

        if "fields" in kwargs:
          if not "*" in kwargs["fields"]:
            fields = set(kwargs["fields"] + [ column_name ])
        
        sql = """SELECT {0} FROM {1}
              WHERE {2} IN ({3})""".format(
                  ",".join(fields),
                  entity,
                  column_name,
                  ",".join(["%s"] * params_count))
        
        entities = self.db.query(sql, *params)
        
        mapped_by_column = { entity[column_name]: entity for entity in entities }
        
        return mapped_by_column if not singular \
              else mapped_by_column.get(args[0])
      
      return template_get_query
    else:
      raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))