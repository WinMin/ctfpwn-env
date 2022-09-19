# ctfpwn-env
## introduction
A project that uses containers to manage linux pwn environments.

## docker images

Store dockerfile for some versions of ubuntu.
Build and push a docker image using GitHub action.

All image can be found here: [beswing/swpwn](https://hub.docker.com/repository/docker/beswing/swpwn)

provided tools

- pwndbg
- pwntools
- keystone assmebler
- capstone disassembler
- glibc source and debug version glibc(so we can debug libc with source)
- Ropper
- ROPGadgets
- one_gadget
- seccomp-tools
...

### pull
sample：

```bash
docker pull beswing/swpwn:22.04
```

## swpwn
A tool for managing glibc pwn environments using containers. This is a simplified version of [ancypwn](https://github.com/Escapingbug/ancypwn)

It uses docker to manage the tools you might need, so you have separete environment, and you do all the debugging with the shared folder.


### install

`python3 -m pip install swpwn` 

### usage

Contains only the container management parts.
- run     
  run a pwn environments using containers.  
  usage:  `swpwn run --ubuntu 20.04 --priv --dir .` 
- list    
  list all runing container.                
  usage:  `swpwn list`
- attach  
  attach a running containers.              
  usage:  `swpwn attach [container-name]` 
- end     
  stop and delete a running container.      
  usage:  `swpwn end [container-name]`  

## MSL (MacOS subsystem for Linux power by Docker)
Inspired by WSL, running a persistent container on MacOS via Docker

### usage
```bash
$ msl --help
usage: msl [-h] [--ubuntu UBUNTU] [--name NAME] [--priv] [--dir DIRECTORY] [--run RUN [RUN ...]] [--commit] [--loglevel LOGLEVEL]

MacOS subsystem for Linux power by Docker

optional arguments:
  -h, --help           show this help message and exit
  --ubuntu UBUNTU      choice ubuntu version
  --name NAME          container name
  --priv               privileged boot , so you can use something like kvm
  --dir DIRECTORY      shared directory to be mounted at /workhub
  --run RUN [RUN ...]  run command
  --commit             commit container to image
  --loglevel LOGLEVEL  log level

```

Run a shell in the current directory
```bash
# swing @ WorkMac in ~/Desktop/ctfpwn-env on git:main x [0:52:28]
$ msl
[check_container() - msl:93 ] Container status: running
[main() - msl:139 ] Running command: bash -c "cd '/workhub/Desktop/ctfpwn-env' ; zsh"

__________               .__  .__  _____
\______   \__  _  ______ |  | |__|/ ____\____
 |     ___/\ \/ \/ /    \|  | |  \   __\/ __ \
 |    |     \     /   |  \  |_|  ||  | \  ___/
 |____|      \/\_/|___|  /____/__||__|  \___  >
                       \/                   \/
                                 no pwn no life

docker-desktop# pwd
/workhub/Desktop/ctfpwn-env
docker-desktop#
```
Execute a command in the current directory, for example binwalk
```
# swing @ swingdeiMac in ~/Downloads/_a4bdea30bfcb8fbe6b1c159bf0a996d7_EG_RGOS11.9_6_B13P1T2,Release_09132119_.bin.extracted [0:53:39]
$ msl --run binwalk 960.gz
[check_container() - msl:93 ] Container status: running
[main() - msl:139 ] Running command: bash -c "cd '/workhub/Downloads/_a4bdea30bfcb8fbe6b1c159bf0a996d7_EG_RGOS11.9_6_B13P1T2,Release_09132119_.bin.extracted' ; binwalk 960.gz"

__________               .__  .__  _____
\______   \__  _  ______ |  | |__|/ ____\____
 |     ___/\ \/ \/ /    \|  | |  \   __\/ __ \
 |    |     \     /   |  \  |_|  ||  | \  ___/
 |____|      \/\_/|___|  /____/__||__|  \___  >
                       \/                   \/
                                 no pwn no life


DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             gzip compressed data, maximum compression, from Unix, last modified: 1970-01-01 00:00:00 (null date)
8357269       0x7F8595        Zip archive data, at least v2.0 to extract, compressed size: 1365, uncompressed size: 2795, name: keepon.html
8358675       0x7F8B13        Zip archive data, at least v2.0 to extract, compressed size: 3489, uncompressed size: 9623, name: login.html
8362204       0x7F98DC        Zip archive data, at least v2.0 to extract, compressed size: 6865, uncompressed size: 7919, name: login_image.jpg
8430923       0x80A54B        Zip archive data, at least v2.0 to extract, compressed size: 20302, uncompressed size: 20373, name: style/logo.png
8503960       0x81C298        Zip archive data, at least v2.0 to extract, compressed size: 4258, uncompressed size: 15874, name: online_mobile.htm
8508265       0x81D369        Zip archive data, at least v2.0 to extract, compressed size: 2733, uncompressed size: 6624, name: offline.htm
8511039       0x81DE3F        Zip archive data, at least v2.0 to extract, compressed size: 4524, uncompressed size: 15206, name: online.htm
```

