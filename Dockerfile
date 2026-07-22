FROM python:3.11.15-slim-bookworm@sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HOME="/home/tutorial" \
    PATH="/tutorial/.venv/bin:$PATH"
WORKDIR /tutorial

RUN python -m pip install --no-cache-dir uv==0.11.31 \
    && useradd --create-home --uid 1000 tutorial \
    && chown tutorial:tutorial /tutorial
USER tutorial

COPY --chown=tutorial:tutorial pyproject.toml uv.lock README.md LICENSE ./
COPY --chown=tutorial:tutorial src ./src
RUN uv sync --frozen --no-dev --extra tutorial

COPY --chown=tutorial:tutorial data ./data
COPY --chown=tutorial:tutorial notebooks ./notebooks
COPY --chown=tutorial:tutorial outputs ./outputs

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
