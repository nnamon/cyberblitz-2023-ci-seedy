FROM ubuntu:jammy

# Global Constants
ENV BASE_DIR=/opt/ciseedy
ENV LISTEN_PORT=31337
ENV PROCESS_LIMIT=100
ENV USER1=seedy
ENV DEBIAN_FRONTEND="noninteractive"

# Some protections
RUN echo "$USER1     hard    nproc       $PROCESS_LIMIT" >> /etc/security/limits.conf

# Global Dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN apt-get install -y net-tools
RUN apt-get install -y build-essential
RUN apt-get install -y xinetd
RUN apt-get install -y openjdk-11-jdk-headless
RUN apt-get install -y unzip

# Some cool tools for hackers.
RUN apt-get install -y curl netcat wget tmux vim

# Setup the users.
RUN useradd -m $USER1

# Create and setup the base directory containing the vulnerable services.
RUN mkdir -p $BASE_DIR
ADD ciseedy $BASE_DIR/ciseedy
ADD utils $BASE_DIR/utils
RUN chmod +x $BASE_DIR/utils/*
WORKDIR $BASE_DIR
RUN chown -R root:root $BASE_DIR
RUN chmod -R 755 $BASE_DIR
RUN chmod +x $BASE_DIR/utils/*

# Setup the ciseedy service.
RUN chmod +x $BASE_DIR/ciseedy/ciseedy.py
RUN pip install -r $BASE_DIR/ciseedy/requirements.txt

# Setup the flag.
COPY flag /flag
RUN chown root:root /flag
RUN chmod 440 /flag
RUN chown -R root:$USER1 /home/
RUN chmod -R 440 /home/*

# Setup the SUID binary to read the flag.
RUN printf '#include<stdio.h>\n#include <stdlib.h>\n\n \
void main() \n \
{ \n \
FILE *f = fopen("/flag", "rb"); \n \
fseek(f, 0, SEEK_END); \n \
long fsize = ftell(f); \n \
fseek(f, 0, SEEK_SET); \n \
char *string = malloc(fsize + 1); \n \
fread(string, 1, fsize, f); \n \
fclose(f); \n \
string[fsize] = 0; \n \
puts(string); \n \
}' | gcc -o /readflag -xc -
RUN chown root:root /readflag
RUN chmod 755 /readflag
RUN chmod g+s /readflag

# Setup xinetd services.
COPY ./xinetd-services/* /etc/xinetd.d/

# Create a directory for user defined builds.
RUN mkdir -p /tmp/builds
RUN chmod 773 /tmp/builds

# Prevent user accounts from invoking some tools.
RUN chmod 500 /usr/bin/ps /bin/ps

# Expose the listening port
EXPOSE $LISTEN_PORT

# Finally run the services.
ENTRYPOINT ["/opt/ciseedy/utils/main.sh"]
