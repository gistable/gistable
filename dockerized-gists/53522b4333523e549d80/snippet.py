#!/usr/bin/env python

import bigml
from bigml.api import BigML

# You need to define BIGML_USERNAME and BIGML_API_KEY in your environment, or 
# add them here:
#api = BigML(username, api_key, dev_mode=True)

api = BigML(dev_mode=True)

# Create the source from S3
source = api.create_source("s3://bigml-public/csv/us_primary_interstates.csv", { 
    "name": "US Primary Interstates"
})

# Wait for it to be ready
api.ok(source)

# Create a 1-click dataaet, and wait
dataset_by_num = api.create_dataset(source)
api.ok(dataset_by_num)

# Create a model to predict Direction, excluding Is Long
model_by_num = api.create_model(dataset_by_num, {
    "name": "US Primary Interstates - by Number",
    "excluded_fields": [ "Is Long" ],
    "objective_field": "Direction"
})

# Create a new dataset by adding a field isEven, using a json s-expression
dataset_by_even = api.create_dataset(dataset_by_num, { 
    "new_fields": [ { 
        "field": '[ "=", 0, [ "mod", [ "field", "Highway Number" ], 2 ]]',
        "name": "isEven"
    } ], 
    "name": "US Primary Interstates - by isEven"
})

api.ok(dataset_by_even)

# Model this new dataset, letting it choose between HIghway Number and isEven
model_by_even = api.create_model(dataset_by_even, {
    "name": "US Primary Interstates - by isEven",
    "excluded_fields": [ "Is Long" ]
})