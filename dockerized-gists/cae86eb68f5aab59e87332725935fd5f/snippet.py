# Copyright (C) 2016 Martina Pugliese

from boto3 import resource
from boto3.dynamodb.conditions import Key

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')


def get_table_metadata(table_name):
    """
    Get some metadata about chosen table.
    """
    table = dynamodb_resource.Table(table_name)

    return {
        'num_items': table.item_count,
        'primary_key_name': table.key_schema[0],
        'status': table.table_status,
        'bytes_size': table.table_size_bytes,
        'global_secondary_indices': table.global_secondary_indexes
    }


def read_table_item(table_name, pk_name, pk_value):
    """
    Return item read by primary key.
    """
    table = dynamodb_resource.Table(table_name)
    response = table.get_item(Key={pk_name: pk_value})

    return response


def add_item(table_name, col_dict):
    """
    Add one item (row) to table. col_dict is a dictionary {col_name: value}.
    """
    table = dynamodb_resource.Table(table_name)
    response = table.put_item(Item=col_dict)

    return response


def delete_item(table_name, pk_name, pk_value):
    """
    Delete an item (row) in table from its primary key.
    """
    table = dynamodb_resource.Table(table_name)
    response = table.delete_item(Key={pk_name: pk_value})

    return


def scan_table_firstpage(table_name, filter_key=None, filter_value=None):
    """
    Perform a scan operation on table. Can specify filter_key (col name) and its value to be filtered. This gets only first page of results in pagination. Returns the response.
    """
    table = dynamodb_resource.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.scan(FilterExpression=filtering_exp)
    else:
        response = table.scan()

    return response


def scan_table_allpages(table_name, filter_key=None, filter_value=None):
    """
    Perform a scan operation on table. Can specify filter_key (col name) and its value to be filtered. This gets all pages of results.
    Returns list of items.
    """
    table = dynamodb_resource.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.scan(FilterExpression=filtering_exp)
    else:
        response = table.scan()

    items = response['Items']
    while True:
        print len(response['Items'])
        if response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items += response['Items']
        else:
            break

    return items


def query_table(table_name, filter_key=None, filter_value=None):
    """
    Perform a query operation on the table. Can specify filter_key (col name) and its value to be filtered. Returns the response.
    """
    table = dynamodb_resource.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response