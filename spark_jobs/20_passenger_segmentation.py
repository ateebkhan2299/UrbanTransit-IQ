from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler

def run():
    spark = SparkSession.builder.appName("PassengerSegmentation").getOrCreate()
    df = spark.createDataFrame([(1, 10, 2), (2, 2, 0)], ["user_id", "trips", "complaints"])
    vec = VectorAssembler(inputCols=["trips", "complaints"], outputCol="features")
    kmeans = KMeans(k=2, seed=1)
    kmeans.fit(vec.transform(df)).save("./models/passenger_segments_kmeans")
    spark.stop()

if __name__ == "__main__":
    run()
