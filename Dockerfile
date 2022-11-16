FROM python:3.6-alpine
ADD . /RestingfMRI_Denoise
WORKDIR /RestingfMRI_Denoise
RUN pip install -r requirements.txt
