FROM fedora:31
MAINTAINER Ramon Moraes <ramon@vyscond.io>
RUN dnf install -y \
    firefox \
    gcc \
    cairo-devel \
    python3 \
    python3-devel \
    gtk3 \
    python3-pip \
    gobject-introspection-devel \
    cairo-gobject-devel
ADD python-harvest /tmp/python-harvest
RUN cd /tmp/python-harvest/ && pip install .
ADD requirements.txt /tmp/requirements.txt
RUN cd /tmp/ && pip install -r requirements.txt
# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer
WORKDIR /usr/src/app
USER developer
ENV HOME /home/developer
CMD bash
