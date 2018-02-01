from pyspark import SparkContext


def main():
    sc = SparkContext(appName="Test Compression")
    # RDD has to be key, value pairs
    data = sc.parallelize([
        ("key1", "value1"),
        ("key2", "value2"),
        ("key3", "value3"),
    ])

    data.saveAsHadoopFile("/tmp/spark_compressed",
                          "org.apache.hadoop.mapred.TextOutputFormat",
                          compressionCodecClass="org.apache.hadoop.io.compress.GzipCodec")
    sc.stop()


if __name__ == "__main__":
    main()
