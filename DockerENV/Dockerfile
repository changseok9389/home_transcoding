FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y git vim htop tmux python3 python3-pip ffmpeg

# 레포 클론
RUN mkdir /workspace
WORKDIR /workspace
RUN git clone http://github.com/changseok9389/home_transcoding
WORKDIR /workspace/home_transcoding
RUN git switch master

# 빌드 프로젝트
RUN python3 -m pip install -r requirements
RUN pip3 install --upgrade protobuf
RUN python3 -m grpc_tools.protoc -I ./proto --python_out=. --grpc_python_out=. ./proto/transcoder.proto

# 사용자 생성
RUN groupadd -g 999 tcserver
RUN useradd -r -u 999 -g tcserver tcserver


# 파일구조 생성
RUN mkdir /workspace/before_encoding
RUN mkdir /workspace/after_encoding

# 서버 오픈
USER tcserver
ENTRYPOINT ["python3", "server.py"]

