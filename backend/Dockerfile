# Image de l'API. Construire d'abord le jar : mvn -B package -DskipTests
FROM eclipse-temurin:21-jre
RUN useradd --system --uid 10001 bi
WORKDIR /app
COPY target/bi-anid-api-*.jar /app/api.jar
USER bi
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "/app/api.jar"]
