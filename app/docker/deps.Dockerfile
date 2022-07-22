FROM nvcr.io/nvidia/deepstream:6.0.1-devel

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ARG DEBIAN_FRONTEND=noninteractive
ENV FORCE_CUDA="1"
ENV CUDA_HOME="/usr/local/cuda"
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV NVIDIA_VISIBLE_DEVICES=all

WORKDIR /

# Install build dependencies
RUN rm /etc/apt/sources.list.d/cuda.list
RUN apt update \
    && apt install -y \
        autoconf \
        automake \
        build-essential \
        cmake \
        cpio \
        curl \
        g++ \
        gcc \
        git \
        gosu \
        libcurl4-openssl-dev \
        libglib2.0 \
        libglib2.0-dev \
        libglib2.0-dev-bin \
        liblapack-dev \
        liblapacke-dev \
        libpng-dev \
        libpython3-all-dev \
        libpython3-dev \
        libspdlog-dev \
        libssl-dev \
        libtool \
        m4 \
        make \
        nano \
        nlohmann-json-dev \
        pciutils \ 
        pkg-config \
        python-dev \
        python-gi-dev \
        python3 \
        python3.6-dev \
        python3-mock \
        python3-numpy \
        python3-opencv \
        python3-pip \
        swig \
        unzip \
        uuid-dev \
        wget \
        xz-utils \
        zip \
        zlib1g-dev
        
RUN python3 -m pip install --upgrade pip

# Install DeepStream Python bindings
RUN python3 -m pip install https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/download/v1.1.1/pyds-1.1.1-py3-none-linux_x86_64.whl
