FROM python:3.10-slim
LABEL org.opencontainers.image.source="https://github.com/mbovo/pixiefairy"
LABEL org.opencontainers.image.authors="Manuel Bovo"
LABEL org.opencontainers.image.maintainers="Manuel Bovo"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"
LABEL org.opencontainers.image.title="pixiefairy"

RUN groupadd --gid 1000 user && useradd --uid 1000 --gid 1000 -m user
WORKDIR /app
# COPY --from=builder /app/dist/*.whl /app
COPY ./dist/*.whl /app
RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir /app/pixiefairy-*.whl>=0.1.0
RUN mkdir /app/templates && chown -R user:user /app/
USER user
EXPOSE 5000
ENTRYPOINT ["pixiefairy"]
CMD ["start", "--help"]
