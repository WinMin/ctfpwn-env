FROM ubuntu:22.04

#RUN  sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list
#RUN  apt-get clean

# Apt packages
RUN dpkg --add-architecture i386 && apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qy \
    sudo \
    git nasm  python3 \
    build-essential \
    python3-dev python3-pip python3-setuptools \
    libc6-dbg \
    libc6-dbg:i386 \
    gcc-multilib \
    gdb-multiarch \
    zsh \
    qemu-user \
    qemu-system \
    gcc \
    wget \
    curl \
    vim \
    glibc-source \
    cmake \
    python3-capstone \
    socat \
    netcat \
    ruby-dev \
    cpio \
    liblzo2-dev \
    telnet \
    file \
    squashfs-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    cd ~ && tar -xf /usr/src/glibc/glib*.tar.xz 

# python/ruby packages & gdb-plugin
RUN pip3 install --upgrade pip
RUN python3 -m pip install --ignore-installed pwntools
RUN pip3 install --no-cache-dir ropper ropgadget ancypatch python-lzo && \
    gem install one_gadget seccomp-tools && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install binwalk
RUN cd ~ && git clone https://github.com/ReFirmLabs/binwalk.git && \
    cd ~/binwalk && \
    python3 setup.py install

# install ubi_reader
RUN cd ~ && git clone https://github.com/jrspruitt/ubi_reader.git && \
    cd ubi_reader && python3 setup.py install


# install gdb plugin
RUN cd ~/ && \
    git clone https://github.com/pwndbg/pwndbg.git && \
    cd ~/pwndbg/ && ./setup.sh && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN cd ~ && \
    git clone https://github.com/scwuaptx/Pwngdb.git && \
    cp ~/Pwngdb/.gdbinit ~/

# gef 
RUN cd ~ && \
	wget -O ~/.gdbinit-gef.py -q http://gef.blah.cat/py

# build radare2
RUN git clone https://github.com/radareorg/radare2  && \
    sh -c radare2/sys/install.sh

# install oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" && \
    sed -i 's/robbyrussell/ys/g' /root/.zshrc


RUN sed -i "1c source /root/pwndbg/gdbinit.py" /root/.gdbinit

ENV LANG C.UTF-8

VOLUME ["/pwn"]
WORKDIR /pwn
CMD ["/bin/zsh"]
