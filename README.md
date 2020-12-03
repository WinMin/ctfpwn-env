# ctfpwn-env



## introduction

A tool for managing glibc pwn environments using containers.

It uses docker to manage the tools you might need, so you have separete environment, and you do all the debugging with the shared folder.

## swpwn

This is a simplified version of [ancypwn](https://github.com/Escapingbug/ancypwn)
Contains only the container management parts.
- run     
  run a pwn environments using containers.  
  usage:  `swpwn run --ubutnu 20.04 --priv .`
- list    
  list all runing container.                
  usage:  `swpwn list`
- attach  
  attach a running containers.              
  usage:  `swpwn attach`
- end     
  stop and delete a running container.      
  usage:  `swpwn end` 

## build

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

