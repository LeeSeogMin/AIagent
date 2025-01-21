FROM python:3.9-bullseye

# 기본 빌드 도구 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        g++ \
        make

# Node.js 설치
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        nodejs \
        openjdk-11-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g nodemon

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

WORKDIR /app

# Python 패키지 설치를 위한 기본 도구 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["nodemon", "--exec", "python", "main.py", "--legacy-watch"]