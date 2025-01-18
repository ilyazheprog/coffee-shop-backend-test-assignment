ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

# Устанавливаем временную зону
ENV TZ=${TIMEZONE}

# Обновляем информацию о временных зонах
RUN apt-get update && apt-get install -y tzdata

# Устанавливаем временную зону
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata


RUN pip install --no-cache -U pip pdm==2.19.1

ARG USERNAME=python_user
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ENV USER_UID=${USER_UID}
ARG PATH_APP=/home/${USERNAME}/app/back
ENV PYTHONPATH=$PYTHONPATH:${PATH_APP}
ARG PATH_VENVS=/home/${USERNAME}/.local/share/pdm/venvs

RUN apt purge -y curl gnupg && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    mkdir -p ${PATH_APP} && \
    mkdir -p ${PATH_VENVS} && \
    chown -R ${USER_UID}:${USER_GID} /home/${USERNAME} && \
    chown -R ${USER_UID}:${USER_GID} ${PATH_APP} && \
    chown -R ${USER_UID}:${USER_GID} ${PATH_VENVS} && \
    chsh -s /bin/bash ${USERNAME}

USER ${USERNAME}
