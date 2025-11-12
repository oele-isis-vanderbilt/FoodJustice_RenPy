FROM python:3.12 AS renpybuilder

ARG RENPY_GAME_DIR="SciStoryPollinators"

WORKDIR /game

COPY ${RENPY_GAME_DIR} /game/${RENPY_GAME_DIR}

ENV SERVICE_URL=""

RUN apt-get update && apt-get install -y libgl1 && \
    wget https://www.renpy.org/dl/8.3.2/renpy-8.3.2-sdk.tar.bz2 && \
    tar -xf renpy-8.3.2-sdk.tar.bz2 && \
    mv renpy-8.3.2-sdk renpy && \
    rm renpy-8.3.2-sdk.tar.bz2 && \
    cd renpy && wget https://www.renpy.org/dl/8.3.2/renpy-8.3.2-web.zip && unzip renpy-8.3.2-web.zip && rm renpy-8.3.2-web.zip && \
    ./renpy.sh launcher web_build ../${RENPY_GAME_DIR} --dest ../${RENPY_GAME_DIR}1.0-dists 

FROM node:20 AS controlbuilder

WORKDIR /control

COPY control-dashboard /control/control-dashboard

RUN cd control-dashboard && npm install && npm run build

FROM python:3.12

ARG RENPY_GAME_DIR="SciStoryTeacherDemo"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN git clone https://github.com/oele-isis-vanderbilt/syncflow-python-client.git && cd syncflow-python-client && pip install .

COPY --from=renpybuilder /game/${RENPY_GAME_DIR}1.0-dists /code/${RENPY_GAME_DIR}

COPY --from=controlbuilder /control/control-dashboard/build /code/ControlDashboard

COPY ./service /code/app

COPY ./syncflow/index.html /code/${RENPY_GAME_DIR}/index.html

COPY ./syncflow/livekit-client.umd.min.js /code/${RENPY_GAME_DIR}/livekit-client.umd.min.js

COPY ./syncflow/syncflow-publisher.js /code/${RENPY_GAME_DIR}/syncflow-publisher.js

COPY ./syncflow/livekit-client.umd.min.js /code/${RENPY_GAME_DIR}/azuretts.js

COPY ./syncflow/livekit-client.umd.min.js /code/${RENPY_GAME_DIR}/microphoneUtility.js

COPY ./syncflow/livekit-client.umd.min.js /code/${RENPY_GAME_DIR}/microphoneUtility.js

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]