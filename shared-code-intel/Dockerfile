FROM node:20-bookworm-slim AS node-runtime
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet-runtime
FROM eclipse-temurin:17-jdk AS java-runtime

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/code-intel
ARG SCIP_VERSION=v0.9.0
ARG SCIP_JAVA_VERSION=0.12.3
ARG SCIP_DOTNET_VERSION=0.2.14

WORKDIR /opt/code-intel

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN OS="$(uname -s | tr '[:upper:]' '[:lower:]')" \
    && ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')" \
    && curl -fsSL "https://github.com/scip-code/scip/releases/download/${SCIP_VERSION}/scip-${OS}-${ARCH}.tar.gz" \
    | tar xzf - -C /usr/local/bin scip \
    && chmod +x /usr/local/bin/scip

RUN pip install --no-cache-dir -r requirements.txt ast-grep-cli \
    && scip --help >/dev/null \
    && ast-grep --version \
    && rg --version

COPY runtime ./runtime

ENTRYPOINT ["python", "-m", "runtime.cli"]

FROM runtime AS indexers

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules

RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && ln -sf ../lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack \
    && npm install -g @sourcegraph/scip-python @sourcegraph/scip-typescript \
    && node --version \
    && npm --version \
    && scip-python --help >/dev/null \
    && scip-typescript --help >/dev/null

FROM runtime AS indexers-jvm-dotnet

ARG SCIP_JAVA_VERSION=0.12.3
ARG SCIP_DOTNET_VERSION=0.2.14
ENV DOTNET_ROOT=/usr/share/dotnet \
    JAVA_HOME=/opt/java/openjdk \
    PATH="/root/.dotnet/tools:/usr/share/dotnet:/opt/java/openjdk/bin:${PATH}"

COPY --from=dotnet-runtime /usr/share/dotnet /usr/share/dotnet
COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk

RUN ln -sf /usr/share/dotnet/dotnet /usr/local/bin/dotnet \
    && apt-get update \
    && apt-get install -y --no-install-recommends libicu76 \
    && rm -rf /var/lib/apt/lists/* \
    && dotnet tool install --global scip-dotnet --version ${SCIP_DOTNET_VERSION} \
    && curl -fLo /usr/local/bin/coursier https://git.io/coursier-cli \
    && chmod +x /usr/local/bin/coursier \
    && /usr/local/bin/coursier bootstrap --standalone -o /usr/local/bin/scip-java com.sourcegraph:scip-java_2.13:${SCIP_JAVA_VERSION} --main com.sourcegraph.scip_java.ScipJava \
    && java -version \
    && dotnet --version \
    && scip-dotnet --version \
    && scip-java --help >/dev/null

FROM runtime
