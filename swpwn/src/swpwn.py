#!/bin/python
import argparse
import os
import os.path
import docker
import sys
import json
import socket
import fcntl
import platform
import struct
import signal
import subprocess as sp
import logging

from distutils.dir_util import mkpath

APPNAME = 'swpwn'
APPAUTHOR = 'swpwn'

EXIST_FLAG = '/tmp/swpwn.id'
DAEMON_PID = '/tmp/swpwn.daemon.pid'

SUPPORTED_UBUNTU_VERSION = [
#    '14.04', Still many issues to be solved (version problems mostly)
    '16.04',
    '18.04',
    '19.04',
    '20.04'
]

client = docker.from_env()
container = client.containers
image = client.images

class SetupError(Exception):
    pass

class InstallationError(Exception):
    pass

class AlreadyRuningException(Exception):
    pass

class NotRunningException(Exception):
    pass

class ColorWrite(object):
    COLOR_SET = {
            'END': '\033[0m',
            'yellow': '\033[38;5;226m',
            'red': '\033[31m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
    }

    @staticmethod
    def color_write(content, color):
        print(ColorWrite.COLOR_SET[color] + content + ColorWrite.COLOR_SET['END'])

def colorwrite_init():
    for color in ColorWrite.COLOR_SET:
        # Use default value for lambda to avoid lazy capture of closure
        setattr(ColorWrite, color, staticmethod(lambda x, color=color: ColorWrite.color_write(x, color)))

# Static initialize ColorWrite
colorwrite_init()

def parse_args():
    """Parses commandline arguments
    Returns:
        args -- argparse namespace, contains the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="swpwn's pwn environment"
    )
    subparsers = parser.add_subparsers(
        help='Actions you can take'
    )

    run_parser = subparsers.add_parser(
        'run',
        help='run a pwn thread'
    )
    run_parser.add_argument(
        '--dir',
        dest='directory',
        type=str,
        default = '.',
        help='The directory which contains your pwn challenge'
    )
    run_parser.add_argument(
        '--ubuntu',
        type=str,
        help='The version of ubuntu to open'
    )

    run_parser.add_argument(
        '--priv',
        action='store_true',
        help='privileged boot, so you can use something like kvm'
    )
    run_parser.add_argument(
        '--name',
        type=str,
        default = None,
        help='Set the name of the container'
    )
    run_parser.set_defaults(func=run_pwn)

    attach_parser = subparsers.add_parser(
        'attach',
        help ='attach to container by name (or default)'
    )

    attach_parser.add_argument(
        'attach',
        type=str,
        help ='attach to container by name (or default)'
    )
    attach_parser.set_defaults(func=attach_pwn)
    
    end_parser = subparsers.add_parser(
        'end',
        help = 'end container by name (or all)'
    )

    end_parser.add_argument(
        'end',
        default=None,
        nargs='+',
    )
    end_parser.set_defaults(func=end_pwn)

    list_parser = subparsers.add_parser(
        'list',
        help='list all runing container'
    )
    list_parser.set_defaults(func=list_pwn)

    image_parser = subparsers.add_parser(
        'image',
        help='list all images'
    )
    image_parser.set_defaults(func=image_pwn)

    args = parser.parse_args()
    if vars(args) != {}:
        args.func(args)
    else:
        parser.print_usage()



def _read_container_name():
    if not os.path.exists(EXIST_FLAG):
        raise Exception('swpwn is not running, consider use swpwn run first')

    container_name = ''
    with open(EXIST_FLAG, 'r') as flag:
        container_name = flag.read()

    if container_name == '':
        os.remove(EXIST_FLAG)
        raise Exception('swpwn id file is  corrupted, or unable to read saved id file. ' + \
                'Cleaning corrupted id file, please shutdown the container manually')

    return container_name

def _attach_interactive(name):

    cmd = "docker exec -it {} '/bin/zsh'".format(
            name,
        )
    ColorWrite.yellow(
        r'''
__________               .__  .__  _____       
\______   \__  _  ______ |  | |__|/ ____\____  
 |     ___/\ \/ \/ /    \|  | |  \   __\/ __ \ 
 |    |     \     /   |  \  |_|  ||  | \  ___/ 
 |____|      \/\_/|___|  /____/__||__|  \___  >
                       \/                   \/ 
                                 no pwn no life 
'''
    )
    os.system(cmd)

def _remove_container_name(end_name):
    if not os.path.exists(EXIST_FLAG):
        raise Exception('swpwn is not running, consider use swpwn run first')

    container_name = ''
    with open(EXIST_FLAG, 'r+') as flag:
        container_name = flag.read()
        # print(container_name)
        if container_name == '':
            os.remove(EXIST_FLAG)
            # raise Exception('swpwn id file is  corrupted, or unable to read saved id file. ' + \
            #         'Cleaning corrupted id file, please shutdown the container manually')
        if end_name in container_name:
            sub_name = container_name.replace(end_name, '')
            flag.write(sub_name)
    return container_name

def run_pwn(args):
    """Runs a pwn thread
    Just sets needed docker arguments and run it
    """
    # port = args.port if not args.port is None else 15111

    if not args.ubuntu:
        ubuntu = '18.04'
    else:
        # check for unsupported ubuntu version
        if args.ubuntu not in SUPPORTED_UBUNTU_VERSION:
            print('you are using ubuntu version %s' % args.ubuntu)
            print('this version may not be officially supported')
        ubuntu = args.ubuntu
    if not args.directory.startswith('~') and \
            not args.directory.startswith('/'):
                # relative path
        args.directory = os.path.abspath(args.directory)

    if not os.path.exists(args.directory):
        raise IOError('No such directory')


    privileged = True if args.priv else False

    # First we need a running thread in the background, to hold existence
    try:
        if platform.system() != 'Darwin':
            # os.system('xhost +')
            volumes = {
                os.path.expanduser(args.directory) : {
                    'bind': '/pwn',
                    'mode': 'rw'
                },
                os.path.expanduser('~/.Xauthority') : {
                    'bind': '/root/.Xauthority',
                    'mode': 'rw'
                },
                os.path.expanduser('/tmp/.X11-unix') : {
                    'bind': '/tmp/.X11-unix',
                    'mode': 'rw'
                }
            }
        else:
            volumes = {
                os.path.expanduser(args.directory) : {
                    'bind': '/pwn',
                    'mode': 'rw'
                }
            }
        running_container = container.run(
            'beswing/swpwn:{}'.format(ubuntu),
            '/bin/zsh',
            cap_add=['SYS_ADMIN', 'SYS_PTRACE'],
            security_opt=['seccomp:unconfined'],
            detach=True,
            tty=True,
            volumes=volumes,
            privileged=privileged,
            network_mode='host',
            name=args.name,
            #environment={
            #    'DISPLAY': os.environ['DISPLAY']
            #},
            remove=True, # This is important, or else we will have many stopped containers
        )
    except Exception as e:
        print('swpwn unable to run docker container')
        print('please refer to documentation to correctly setup your environment')
        print()
        raise e

    # Set flag, save the container id
    with open(EXIST_FLAG, 'a+') as flag:
        flag.write(running_container.name + '\n')


    # Then attach to it, needs to do it in shell since we need
    # shell to do the input and output part(interactive part)
    _attach_interactive(running_container.name)
    

def attach_pwn(args):
    """Attaches to a pwn thread
    Just sets needed docker arguments and run it as well
    """
    all_container_name = _read_container_name().split()
    if args.attach.isdigit():
        conts = container.list()
        _attach_interactive(conts[int(args.attach)].name) # now args.attach is index of container
        return
    container_name = args.attach
    if container_name not in all_container_name:
        print('There is no container with this name, please re-enter')
        return 

    # FIXME Is it better that we just exec it with given name?
    conts = container.list(filters={'name':container_name})
    _attach_interactive(conts[0].name)
    

def list_pwn(args):
    """List all running container
    """
    # containers_header = ['CONTAINER ID','IMAGE','STATUS','PORTS']
    # containers_data = []
    # for containers in container.list():
    #     print(containers.name)
    os.system('docker ps -a')


def image_pwn(args):
    """List all image
    """
    all_img = image.list()
    for img in all_img:
        print('{} {}'.format(img.tags[0], img.id[:20]))

def end_pwn(args):
    """Ends a running thread
    """
    conts = container.list()
    if len(conts) < 1:
        os.remove(EXIST_FLAG)
        raise NotRunningException('No pwn thread running, corrupted meta info file, deleted')
    if 'all' in args.end:
        conts = container.list()
        for i in range(len(conts)):
            conts[i].stop() 
        # conts[0].stop()
        os.remove(EXIST_FLAG)
    else:
        for name in args.end:
            conts = container.list(filters={'name': name})
            if len(conts) < 1:
                print('No contianer name of {}'.format(name))
                return 0
            conts[0].stop()
            _remove_container_name(name)



def main():
    parse_args()


if __name__ == "__main__":
    main()
