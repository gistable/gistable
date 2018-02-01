# A simple cheat sheet of Spark Dataframe syntax
# Current for Spark 1.6.1

# import statements
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *

#creating dataframes
df = sqlContext.createDataFrame([(1, 4), (2, 5), (3, 6)], ["A", "B"]) # from manual data
df = sqlContext.read.format('com.databricks.spark.csv') \
  .options(delimiter=';',header='true', inferschema='true',mode="FAILFAST") \
  .load('csv_file_name_or_*_reference')

# adding columns and keeping existing ones
df.withColumn('zero', F.lit(0))
df.withColumn('A_times_two', df.A * 2)

# selecting columns, and creating new ones
df.select(
    'A' # most of the time it's sufficient to just use the column name
  , col('A').alias('new_name_for_A') # in other cases the col method is nice for referring to columnswithout having to repeat the dataframe name
  , ( col('B') > 0 ).alias('is_B_greater_than_zero')
  , unix_timestamp('A','dd.MM.yyyy HH:mm:ss').alias('A_in_unix_time') # convert to unix time from text
  )

# filtering
df.filter('A_in_unix_time > 946684800')

# grouping and aggregating
df.groupBy("A").agg(
     first("B").alias("my first")
   , last("B").alias("my last")
   , sum("B").alias("my everything")
)

# pivoting
df.groupBy('A','B').pivot('C').agg(first('D')).orderBy(['A','B']) # first could be any aggregate function

# inspecting dataframes
display(df) # table in notebook at least
df.show() # text table

######################################### Date time manipulation ################################
# Casting to timestamp from string with format 2015-01-01 23:59:59
df.select( df.start_time.cast("timestamp").alias("start_time") )
 
# Get all records that have a start_time and end_time in the same day, and the difference between the end_time and start_time is less or equal to 1 hour.
condition = \
  (to_date(df.start_time) == to_date(df.end_time)) & \
  (df.start_time + expr("INTERVAL 1 HOUR") >= df.end_time)
df.filter(condition).show()

############### WRITING TO AMAZON REDSHIFT ###############

REDSHIFT_JDBC_URL = "jdbc:redshift://%s:5439/%s" % (REDSHIFT_SERVER,DATABASE)

df.write \
  .format("com.databricks.spark.redshift") \
  .option("url", REDSHIFT_JDBC_URL) \
  .option("dbtable", TABLE_NAME) \
  .option("tempdir", "s3n://%s:%s@%s" % (ACCESS_KEY,SECRET, S3_BUCKET_PATH)) \
  .mode("overwrite") \
  .save()


######################### REFERENCE #########################

# aggregate functions
approxCountDistinct, avg, count, countDistinct, first, last, max, mean, min, sum, sumDistinct

# window functions
cumeDist, denseRank, lag, lead, ntile, percentRank, rank, rowNumber

# string functions
ascii, base64, concat, concat_ws, decode, encode, format_number, format_string, get_json_object, initcap, instr, length, levenshtein, locate, lower, lpad, ltrim, printf, regexp_extract, regexp_replace, repeat, reverse, rpad, rtrim, soundex, space, split, substring, substring_index, translate, trim, unbase64, upper

# null and nan functions
isNaN, isnotnull, isnull

# misc functions
array, bitwiseNOT, callUDF, coalesce, crc32, greatest, if, inputFileName, least, lit, md5, monotonicallyIncreasingId, nanvl, negate, not, rand, randn, sha, sha1, sparkPartitionId, struct, when

# datetime
current_date, current_timestamp, trunc, date_format
datediff, date_add, date_sub, add_months, last_day, next_day, months_between
year, month, dayofmonth, hour, minute, second
unix_timestamp, from_unixtime, to_date, quarter, day, dayofyear, weekofyear, from_utc_timestamp, to_utc_timestamp
