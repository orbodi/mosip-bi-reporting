# Image de DÉVELOPPEMENT du pipeline temps réel : job PySpark de l'enrôlement, simulateur MOSIP et outils.
# Construite par deploy/docker-compose.yml (profil temps-reel). Ne contient ni secret ni donnée.
FROM python:3.12-slim-bookworm

# Java 17 pour Spark ; openssl pour le certificat TLS de la base MOSIP simulée.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless openssl procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Connecteur Kafka de Spark (Maven Central) : téléchargé une fois ici, puis lu dans le cache au démarrage.
ENV SPARK_KAFKA_PAQUET=org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0 \
    SPARK_IVY=/opt/ivy
RUN python -c "from pyspark.sql import SparkSession; SparkSession.builder.master('local[1]').config('spark.jars.packages', '${SPARK_KAFKA_PAQUET}').config('spark.jars.ivy', '${SPARK_IVY}').getOrCreate().stop()"

COPY pyproject.toml .
COPY streaming/ streaming/
COPY simulateur/ simulateur/
COPY outils/ outils/

# Utilisateur sans privilège ; /donnees reçoit le checkpoint Spark (volume nommé).
RUN useradd --create-home --uid 1000 pipeline \
    && mkdir -p /donnees \
    && chown -R pipeline /donnees /opt/ivy
USER pipeline
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1
CMD ["python", "-m", "streaming.enrolement.job"]
