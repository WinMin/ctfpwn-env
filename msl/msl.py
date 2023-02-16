#!/usr/bin/env  python3
import docker
import os
import platform
import logging
import argparse

from distutils.dir_util import mkpath


APPNAME = 'msl'
APPAUTHOR = 'swing'

SUPPORTED_UBUNTU_VERSION_LTS = [
#    '14.04', Still many issues to be solved (version problems mostly)
    '16.04',
    '18.04',
    '20.04',
    '22.04',
]

client = docker.from_env()
container = client.containers
image = client.images

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

def run_container(args):

    if not args.ubuntu:
        ubuntu = SUPPORTED_UBUNTU_VERSION_LTS[-1]
    elif args.ubuntu in SUPPORTED_UBUNTU_VERSION_LTS:
        ubuntu = args.ubuntu


    if not args.directory:
        args.directory = os.getenv('HOME')

    if platform.system() == 'Darwin':
        volumes = {
            os.path.expanduser(args.directory) :{
                'bind':'/workhub',
                'mode':'rw'
            }
        }

    privileged = True if args.priv else False
    print(privileged)
    try:
        running_container = container.run(
            'beswing/swpwn:{}'.format(ubuntu),
            '/bin/zsh',
            cap_add=['SYS_ADMIN','SYS_PTRACE'],
            security_opt=['seccomp:unconfined'],
            detach=True,
            tty=True,
            volumes=volumes,
            privileged=privileged,
            network_mode = 'host',
            name=args.name,
            # remove=True,
        )

    except Exception as e:
        logging.error('Failed to run : {}'.format(e))


def check_container(args):
    try:
        container_status = container.get(args.name).status
        if container_status != 'running':
            container.get(args.name).start()
        logging.info('Container status: {}'.format(container.get(args.name).status))
        return True
    except Exception as e:
        logging.error('some error: {}'.format(e))
        return False


def commit_container(args):
    if args.commit_tag is None:
        logging.error('must set commit tag use [--commit-tag]')
        exit(0)
    try:
        if check_container():
            msl_container = container.get(args.name)
            msl_container.commit(repository='beswing/swpwn',tag='22.04')
            msl_container.stop()
            msl_container.remove()
    except Exception as e:
        logging.error('some error: {}'.format(e))
        return False
    
def remove_container(args):
    try:
        sub_container = container.get(args.name)
        sub_container.stop()
        sub_container.remove()
    except Exception as e:
        logging.error('some error: {}'.format(e))
        return False
    
def _attach_interactive(name,command):

    cmd = "docker exec -it {} {}".format(
            name,command
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


def run_command(args):

    mslCmd = ' '.join(args.run)
    print(args.directory)
    if args.directory == None:
        command = 'bash -c "cd \'{}\' ; {}"'.format(PATH, mslCmd)
    else:
        command = 'bash -c "cd \'{}\' ; {}"'.format('/workhub', mslCmd)
    logging.info('Running command: {}'.format(command))
    _attach_interactive(args.name, command)

def main(args):

    if args.commit ==True:
        commit_container(args)
    elif args.priv == True or args.directory or args.restart:
        remove_container(args)

    if check_container(args) == False:
        run_container(args)

    run_command(args)



def parse_args():
    parser = argparse.ArgumentParser(description='MacOS subsystem Linux power by Docker')
    parser.add_argument('--ubuntu', default='22.04',type=str, help='choice ubuntu version')
    parser.add_argument('--name', default='msl', type=str, help='container name')
    parser.add_argument('--priv', action='store_true', help='privileged boot , so you can use something like kvm')
    parser.add_argument('--dir', dest='directory',type=str, help='shared directory to be mounted at /workhub')
    parser.add_argument('--run', default=['zsh'], dest='run', type=str, help='run command', nargs='+')
    parser.add_argument('--commit',action='store_true', help='commit container to image')
    parser.add_argument('--commit-name',default='beswing/swpwn', type=str, help='commint name' )
    parser.add_argument('--commit-tag',type=str,help='commit tag')
    parser.add_argument('--restart', action='store_true', default=False, help='restart')
    parser.add_argument('--loglevel', default='INFO', type=str, help='log level')
    args = parser.parse_args()
    # run_container(args)
    LOGFORMAT = "[%(funcName)s() - %(filename)s:%(lineno)s ] %(message)s"
    logging.basicConfig(level=args.loglevel, format=LOGFORMAT)

    main(args)

if __name__ == '__main__':
    PWD = os.getenv('PWD')
    HOME = os.getenv('HOME')
    PATH = PWD.replace(HOME, '/workhub')
    parse_args()
