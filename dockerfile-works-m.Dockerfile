FROM docker.io/library/spark:3.5.5-scala2.12-java17-python3-ubuntu

USER root

# Download Spark Connect JARs for Spark 3.5.5
RUN curl -L https://repo1.maven.org/maven2/org/apache/spark/spark-connect_2.12/3.5.5/spark-connect_2.12-3.5.5.jar \
    -o /opt/spark/jars/spark-connect_2.12-3.5.5.jar

# Download AWS SDK Bundle 1.12.599 (better MinIO compatibility)
RUN curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.599/aws-java-sdk-bundle-1.12.599.jar \
    -o /opt/spark/jars/aws-java-sdk-bundle-1.12.599.jar

# Download Hadoop AWS 3.3.4 (matching base image Hadoop version)
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -o /opt/spark/jars/hadoop-aws-3.3.4.jar

# Download Hadoop Client API 3.3.4
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar \
    -o /opt/spark/jars/hadoop-client-api-3.3.4.jar

# Download Hadoop Client Runtime 3.3.4
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar \
    -o /opt/spark/jars/hadoop-client-runtime-3.3.4.jar

# Download Apache Commons Pool (often needed for connection pooling)
RUN curl -L https://repo1.maven.org/maven2/org/apache/commons/commons-pool/1.6/commons-pool-1.6.jar \
    -o /opt/spark/jars/commons-pool-1.6.jar

# Download Apache Commons Pool2 (newer version, might be needed)
RUN curl -L https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar \
    -o /opt/spark/jars/commons-pool2-2.11.1.jar

RUN chown -R spark:spark /opt/spark/jars/

USER 185 
