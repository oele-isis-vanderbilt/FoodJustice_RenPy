FROM python:3.9 AS renpybuilder

WORKDIR /game

COPY SciStoryPollinators /game/SciStoryPollinators

RUN apt-get update && apt-get install -y libgl1-mesa-glx && \
    wget https://www.renpy.org/dl/8.3.2/renpy-8.3.2-sdk.tar.bz2 && \
    tar -xf renpy-8.3.2-sdk.tar.bz2 && \
    mv renpy-8.3.2-sdk renpy && \
    rm renpy-8.3.2-sdk.tar.bz2 && \
    cd renpy && wget https://www.renpy.org/dl/8.3.2/renpy-8.3.2-web.zip && unzip renpy-8.3.2-web.zip && rm renpy-8.3.2-web.zip && \
    ./renpy.sh launcher web_build ../SciStoryPollinators --dest ../SciStoryPollinators1.0-dists --launch

FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY --from=renpybuilder /game/SciStoryPollinators1.0-dists /code/SciStoryPollinators

COPY ./service /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
