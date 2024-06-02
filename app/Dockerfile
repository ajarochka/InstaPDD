FROM archlinux:base-devel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pacman -Syy
RUN pacman -Syu --noconfirm
RUN pacman -S --noconfirm nginx
RUN pacman -S --noconfirm python python-pip python-wheel vim
RUN pacman -S --noconfirm postgresql postgresql-libs geos gdal proj
RUN pacman -S --noconfirm postgis
RUN pacman -S --noconfirm supervisor
RUN python -m venv /venv
RUN /venv/bin/python -m pip install -U pip
RUN /venv/bin/python -m pip install -U setuptools
COPY ./requirements.txt /app/
COPY ./entrypoint.sh /app/
COPY ./service.conf /app/
RUN /venv/bin/python -m pip install -r requirements.txt
RUN mkdir -p /app/media/uploads
