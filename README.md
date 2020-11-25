# swpwn-env



## introduction

A tool for managing glibc pwn environments using containers.

It uses docker to manage the tools you might need, so you have separete environment, and you do all the debugging with the shared folder.

## swpwn

This is a simplified version of [ancypwn](https://github.com/Escapingbug/ancypwn)

## build

Store dockerfile for some versions of ubuntu.

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

