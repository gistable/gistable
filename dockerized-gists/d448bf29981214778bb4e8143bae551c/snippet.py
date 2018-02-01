def dropFrom(df, column_name, fields_to_drop):
  """ 
  Drops fields from column column_name in PySpark DataFrame.
  
  @tparam df pyspark.sql.DataFrame
  @tparam column_name str
  @tparam fields_to_drop list[str]
  """
  column_struct = [x for x in df.schema.fields if x.name == column_name][0]
  fields_names = [x.name for x in column_struct.dataType.fields]
  leave_fields = [f for f in fields_names if f not in fields_to_drop]
  leave_fields_full_names = [col("{}.{}".format(column_name, x)) for x in leave_fields]
  return df.withColumn(column_name, struct(leave_fields_full_names))