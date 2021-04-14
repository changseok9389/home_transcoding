from __future__ import print_function

import os
import grpc
from glob import glob
import socket
import wget
import argparse

import transcoder_pb2
import transcoder_pb2_grpc

parser = argparse.ArgumentParser()

parser.add_argument("--in_dir", help="path of files before encoding", )
parser.add_argument("--out_dir", help="path of files after encoding")
parser.add_argument("--ip", help="ip address of server machine", default='localhost')
parser.add_argument("--port", help="port number refers to host ip address", default=50051)

args = parser.parse_args()


def find_path(file_path):
    files = glob('{}/**/*'.format(file_path), recursive=True)

    valid_files = [file for file in files
                   if file.split('.')[-1] in ['mkv', 'mp4', 'wmv', 'avi', 'mov']]

    print(valid_files)

    return valid_files


def create_request_form(filename):
    name = ''.join(filename.split('/')[-1].split('.')[0:-1])
    format = filename.split('/')[-1].split('.')[-1]
    file_size = os.stat(filename).st_size
    ip_address = str(socket.gethostbyname(socket.gethostname()))
    url = 'http://{}:8000/{}'.format(ip_address, filename)

    return transcoder_pb2.videoBlob(name=name,
                                         format=format,
                                         size=file_size,
                                         ip_address=ip_address,
                                         url=url)


def run():
    src_dir = args.in_dir
    dst_dir = args.out_dir
    for file in find_path(src_dir):
        print('current file name is : {}'.format(file))
        with grpc.insecure_channel('{}:{}'.format(args.ip, args.port)) as channel:
            stub = transcoder_pb2_grpc.transcoderTestStub(channel)
            response = stub.videoEncodingRequest(create_request_form(file))
            print(response)
            wget.download(response.url, '{}/{}.{}'.format(dst_dir, response.name, response.format))
            os.remove(file)


if __name__ == '__main__':
    run()
