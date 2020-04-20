FROM fedora:31
MAINTAINER Ramon Moraes <ramonmoraes8080@gmail.com>
RUN dnf install -y \
    gcc \
    cairo-devel \
    python3 \
    python3-devel \
    gtk3 \
    python3-pip \
    gobject-introspection-devel \
    cairo-gobject-devel
RUN dnf install -y webkit2gtk3
ADD . /tmp/xharvest
RUN cd /tmp/xharvest/ && pip install .
RUN rm -rf /tmp/xharvest
#ADD requirements.txt /tmp/requirements.txt
#RUN cd /tmp/ && pip install -r requirements.txt
# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/harvest && \
    echo "harvest:x:${uid}:${gid}:Harvest,,,:/home/harvest:/bin/bash" >> /etc/passwd && \
    echo "harvest:x:${uid}:" >> /etc/group && \
    echo "harvest ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/harvest && \
    chmod 0440 /etc/sudoers.d/harvest && \
    chown ${uid}:${gid} -R /home/harvest
WORKDIR /home/harvest
USER harvest
ENV HOME /home/harvest
CMD xharvest
