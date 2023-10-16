FROM python:3.11

# install all packages for chromedriver: https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79
RUN apt-get update
RUN apt-get -y install lsb-release libappindicator3-1 xvfb
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || true
RUN apt-get -fy install

# System deps
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

# Poetry
ENV POETRY_VERSION=1.6.1
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN apt-get update && apt-get install -y libpcre3 libpcre3-dev 

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY . .

EXPOSE 5000
# CMD cd ade_feed_url && poetry run uwsgi --http 0.0.0.0:8080 --master -p 1 -w server:app
CMD cd ade_feed_url && poetry run flask --app server run --host 0.0.0.0 --port 5000
