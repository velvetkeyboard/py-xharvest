FROM fedora:31
MAINTAINER Ramon Moraes <ramonmoraes8080@gmail>
RUN dnf install -y \
        fedora-packager \
        @development-tools \
        python \
        python-devel
RUN pip install wheel
RUN useradd -m xharvest
USER xharvest
WORKDIR /home/xharvest/
CMD bash