q = {
  "query": {
    "function_score": {
      "boost_mode": "replace",
      "query": {
        "ids": {
          "values": [
            50,
            80,
            44,
            12
          ]
        }
      },
      "script_score": {
        "params": {
          "ids": [
              50,
              80,
              44,
              12
          ]
        },
        "script": """
          count = ids.size();
          id    = org.elasticsearch.index.mapper.Uid.idFromUid(doc['_uid'].value);
          for (i = 0; i < count; i++) {
            if (id == ids[i]) { return count - i; }
           }""",
      }
    }
  },
  "size": 20,
  "from": 0
}