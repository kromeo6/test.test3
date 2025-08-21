FROM docker.io/library/spark:3.5.5-java17-python3

USER root

# Download Spark Connect JARs for Spark 3.5.5
RUN curl -L https://repo1.maven.org/maven2/org/apache/spark/spark-connect_2.12/3.5.5/spark-connect_2.12-3.5.5.jar \
    -o /opt/spark/jars/spark-connect_2.12-3.5.5.jar

# Essential S3 dependencies (compatible with Hadoop 3.3.4 in base image)
# Download Hadoop AWS 3.3.4 (matches base image Hadoop version)
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -o /opt/spark/jars/hadoop-aws-3.3.4.jar

# Download AWS SDK v1 (better MinIO compatibility)
RUN curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-s3/1.12.261/aws-java-sdk-s3-1.12.261.jar \
    -o /opt/spark/jars/aws-java-sdk-s3-1.12.261.jar

RUN curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.12.261/aws-java-sdk-core-1.12.261.jar \
    -o /opt/spark/jars/aws-java-sdk-core-1.12.261.jar

RUN curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-dynamodb/1.12.261/aws-java-sdk-dynamodb-1.12.261.jar \
    -o /opt/spark/jars/aws-java-sdk-dynamodb-1.12.261.jar

# DynamoDB JAR removed for testing - let's see if it's actually needed

RUN chown -R spark:spark /opt/spark/jars/

USER 185 


- spark-connect_2.12-3.5.5.jar
- hadoop-aws-3.3.4.jar  
- aws-java-sdk-s3-1.12.261.jar
- aws-java-sdk-core-1.12.261.jar
- aws-java-sdk-dynamodb-1.12.261.jar 
