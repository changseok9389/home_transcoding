import threading
import http.server
import socket
import functools
from http.server import HTTPServer, SimpleHTTPRequestHandler

from concurrent import futures

import os
import grpc
import wget
import subprocess
import socket

import transcoder_pb2
import transcoder_pb2_grpc

class transcoderTest(transcoder_pb2_grpc.transcoderTestServicer):
    def __init__(self):
        self.call_counter = 1
        # total, used, free = shutil.disk_usage("/")
        # free_in_GiB = free // (2**30)

    def encode(self, source, destination):
        subprocess.call(['ffmpeg', '-y'
                            , '-i', source
                            , '-c:v', 'libx264'
                            , '-preset', 'ultrafast'
                            , '-crf', '22'
                            , '-c:a', 'aac'
                            , '-hide_banner'
                         # , '-loglevel panic'
                            , destination])

    def create_response_form(self, filename):
        name = filename.split('/')[-1].split('.')[0]
        format = filename.split('/')[-1].split('.')[-1]
        file_size = os.stat(filename).st_size
        ip_address = str(socket.gethostbyname(socket.gethostname()))
        url = 'http://{}:8000/{}'.format(ip_address, filename)

        return transcoder_pb2.videoBlob(name=name,
                                             format=format,
                                             size=file_size,
                                             ip_address=ip_address,
                                             url=url)

    def videoEncodingRequest(self, videoBlob, context):
        print('[[ video info ]]\nname : {}\nformat : {}\nsize : {}\nip_address : {}\nurl : {}\n'.format(videoBlob.name,
                                                                                                        videoBlob.format,
                                                                                                        videoBlob.size,
                                                                                                        videoBlob.ip_address,
                                                                                                        videoBlob.url))

        download_path_prefix = '/workspace/before_encoding'
        encoding_path_prefix = '/workspace/after_encoding'
        download_path = '{}/{}.{}'.format(download_path_prefix, videoBlob.name, videoBlob.format)
        encoding_path = '{}/{}.{}'.format(encoding_path_prefix, videoBlob.name, 'mp4')
        wget.download(videoBlob.url, download_path)

        self.encode(download_path, encoding_path)
        os.remove(download_path)

        return self.create_response_form(encoding_path)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=12))
    transcoder_pb2_grpc.add_transcoderTestServicer_to_server(transcoderTest(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    debug = True
    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory='/')
    server = http.server.ThreadingHTTPServer((socket.gethostname(), 8000), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    serve()





