FROM ubuntu:24.04

# Factorio only renders in the full client, so the container runs it against a
# virtual X display. Mesa provides OpenGL: hardware through /dev/dri when the
# device is passed in, llvmpipe otherwise.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb \
        x11vnc \
        novnc \
        websockify \
        libgl1-mesa-dri \
        libglx-mesa0 \
        libegl-mesa0 \
        mesa-utils \
        mesa-utils-extra \
        libsdl2-2.0-0 \
        libturbojpeg \
        python3 \
        python3-venv \
        python3-dev \
        build-essential \
        ca-certificates \
        curl \
        gawk \
        xz-utils \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Xvfb has no DRI, so GLX inside it always lands on llvmpipe. VirtualGL renders
# through the GPU with EGL and blits the result back to the virtual display.
ARG VIRTUALGL_VERSION=3.1.1
RUN arch="$(dpkg --print-architecture)" \
    && curl -fsSL -o /tmp/virtualgl.deb \
        "https://github.com/VirtualGL/virtualgl/releases/download/${VIRTUALGL_VERSION}/virtualgl_${VIRTUALGL_VERSION}_${arch}.deb" \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/virtualgl.deb \
    && rm -f /tmp/virtualgl.deb && rm -rf /var/lib/apt/lists/*

# python dependencies live in a venv so the image works on distros that mark
# the system python as externally managed
COPY requirements.txt /opt/factoriomaps/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r /opt/factoriomaps/requirements.txt \
    && apt-get purge -y build-essential python3-dev && apt-get autoremove -y

COPY . /opt/factoriomaps/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# The viewer's javascript and css are fetched from a CDN. Doing that here rather
# than per render means a render never depends on jsdelivr being reachable, and
# never has to write into this directory — which the chmod below makes read only
# for everyone but root, and the container is documented to run as the host user.
# Called through -c because updateLib waits on stdin when run as __main__.
RUN /opt/venv/bin/python -c "import sys; sys.path.insert(0, '/opt/factoriomaps'); import updateLib; updateLib.update(True)"

RUN chmod +x /usr/local/bin/entrypoint.sh \
    && rm -rf /opt/factoriomaps/.git /opt/factoriomaps/.venv \
    && chmod -R a+rX /opt/factoriomaps \
    # the script rewrites autorun.lua on every capture, so it must stay writable
    # even when the container runs as an unprivileged host user
    && : > /opt/factoriomaps/autorun.lua \
    && chmod a+w /opt/factoriomaps/autorun.lua

# factorio user data: saves, mods and script-output are mounted here
# HOME must be writable when the container runs as an unprivileged host user
ENV HOME=/tmp \
    FACTORIO_DIR=/factorio \
    FACTORIO_BINARY=/factorio/bin/x64/factorio \
    FACTORIO_USER_DIR=/data \
    DISPLAY=:99 \
    SCREEN_SIZE=1920x1080x24 \
    ENABLE_VNC=0 \
    VNC_PORT=5900 \
    NOVNC_PORT=6080 \
    LIBGL_ALWAYS_SOFTWARE=0

VOLUME ["/factorio", "/data"]
EXPOSE 5900 6080

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["--help"]
