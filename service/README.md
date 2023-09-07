# CI/Seedy Services

This README contains quick start instructions for setting up the challenge and running it, as well
as general information about each of the services.

## Setup

### Requirements

1. Docker
2. Make

### Quick Setup of Ubuntu 20.04 Docker Host

Some quick commands to get a standard Ubuntu 20.04 LTS server on Digital Ocean up and running to run
Docker:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release make unzip
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io
```

Though, you might want to run 22.04 LTS instead with pretty much the same instructions.

### Updates to the Codebase

1. Update the flag in `service/flag` if you require it.

2. Check that the process limits in `service/Dockerfile` are suitable for the CTF load. A lower
   number helps to prevent resource exhaustion attacks by annoying players but may interfere with
   the number of concurrent users supported.

```dockerfile
# Some protections
RUN echo "$USER1     hard    nproc       50" >> /etc/security/limits.conf
```

3. The default entry port is set to `31337`. To change this, the host bind port in
`service/Makefile` can be changed. The tag can be changed here as well.

```makefile
tag = cyberblitz-2023-ci-seedy
port = <port>
```

### Building the Container

To build the Docker container hosting the service run the following in the `service` directory:

```shell
$ make build
```

The default tag of the image is `cyberblitz-2023-ci-seedy`.

## Running

### Running for Production

To run the container in the background.

```shell
$ make daemon
```

To run the container in the foreground:

```shell
$ make run
```

The service should now be available at `0.0.0.0:31337` (by default).

### Running for Development

If a development session is required, the following command will drop you into a `/bin/bash` root
shell with the `services` directory mounted so that edits to the files will be reflected in the
container:

```shell
$ make dev
```

To run the service, run the following command in the root shell:

```shell
root@1e96ab81dc2f:/opt/ciseedy# ./utils/main.sh
```

### Quick Caveats to Note

* The `/bin/ps` and `/usr/bin/ps` tool has been disabled to non-root users on the Docker container
    to make it more difficult for players to view other player activity.
* The player should never be expected to escalate to root and especially not with a kernel exploit.
    Please ensure that the host kernel is up to date and hardened.
* Some files in the container such as `/unlock_code.txt` are generated at Docker container start up
    time. Exploits should be written to take into account the unknowability of these files.
* If a user gets past the first step to leak `/unlock_code.txt`, they can gain the ability to unzip
    arbitrary files. An annoying player might try to zip bomb the temp directory. Please watch out
    for this.

## Services

This directory is structured like the following:

* `ciseedy/` - The CI/Seedy Service: Provides entry point for the challenge. Written in Python.
* `utils/` - Contains the utility scripts used by the Docker container at runtime.
* `xinetd-services/` - Contains the xinetd service definitions used in the Docker container.
