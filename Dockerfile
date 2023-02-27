# modified from fmriprep
FROM python:slim AS src
RUN pip install build
RUN apt-get update && \
    apt-get install -y --no-install-recommends git
COPY . /src/RestingfMRI_Denoise
RUN python -m build /src/RestingfMRI_Denoise

# Use Ubuntu 20.04 LTS
FROM ubuntu:focal-20210416
# Prepare environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    apt-utils \
                    autoconf \
                    build-essential \
                    bzip2 \
                    ca-certificates \
                    curl \
                    git \
                    libtool \
                    lsb-release \
                    netbase \
                    pkg-config \
                    unzip \
                    xvfb && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
ENV DEBIAN_FRONTEND="noninteractive" \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"  

# nipreps/miniconda:py39_4.12.0rc0
COPY --from=nipreps/miniconda:latest /opt/conda /opt/conda

RUN ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# Set CPATH for packages relying on compiled libs (e.g. indexed_gzip)
ENV PATH="/opt/conda/bin:$PATH" \
    CPATH="/opt/conda/include:$CPATH" \
    LD_LIBRARY_PATH="/opt/conda/lib:$LD_LIBRARY_PATH" \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PYTHONNOUSERSITE=1
    
# Create a shared $HOME directory
RUN useradd -m -s /bin/bash -G users RestingfMRI_Denoise
WORKDIR /home/RestingfMRI_Denoise
ENV HOME="/home/RestingfMRI_Denoise" \
    LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> $HOME/.bashrc && \
    echo "conda activate base" >> $HOME/.bashrc

# Installing RestingfMRI_Denoise
COPY --from=src /src/RestingfMRI_Denoise/dist/*.whl .
RUN /opt/conda/bin/python -m pip install --no-cache-dir $( ls *.whl )[all]

RUN find $HOME -type d -exec chmod go=u {} + && \
    find $HOME -type f -exec chmod go=u {} + && \
    rm -rf $HOME/.npm $HOME/.conda $HOME/.empty

ENV IS_DOCKER_8395080871=1

ENTRYPOINT ["/opt/conda/bin/RestingfMRI_Denoise"]
