from pymongo import Connection

if __name__ == '__main__':
  
  # Connect to mongo
  conn = Connection()
  db = conn['canepi']
  
  # Set the search term
  term = 'foo'
  
  # Run the search
  results = db.command('text', 'healthmap', search=term)
  
  # Print the results
  print(results)
