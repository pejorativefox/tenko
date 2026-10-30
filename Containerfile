FROM scratch
ADD build/browneye-rootfs.tar.gz /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV container=podman
WORKDIR /build
CMD ["/bin/bash"]
