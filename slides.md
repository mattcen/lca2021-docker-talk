# Getting started with Docker and Swarm

Prepared by Matthew Cengia

* Email: mattcen@mattcen.com
* Twitter: [@mattcen](https://twitter.com/mattcen)
* Mastodon: [@mattcen@aus.social](https://aus.social/@mattcen)
* Matrix: [mattcen:matrix.org](https://matrix.to/#/@mattcen:matrix.org)

License: [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

Note:
Hi everyone, my name's Matt, my pronouns are he, him, and his, and I'm here to give a quick introduction to Docker and Swarm. If you'd like to find me later, you can reach me as mattcen (that's M A T T C E N) on either Twitter, the aus.social Mastodon instance, or matrix.org, as well as my email, mattcen@mattcen.com. Also, please feel free to tweet about this talk using the #lca2021 and #dockerintro hash tags.

---

## Acknowledgement of Country

Note:
In the spirit of reconciliation I'd like to acknowledge the Traditional Custodians of country throughout Australia and their connections to land, sea and community.

I pay my respect to their elders past and present and extend that respect to all Aboriginal and Torres Strait Islander peoples today.

---

## Why are we talking about Docker?

Note:
I only started playing with Docker last year,  and almost immediately regretted not having used it earlier, because it's a really powerful tool that can benefit devs and sysadmins alike, and I want to evangelise it a bit to anyone who hasn't taken a bit of time to appreciate it yet. I'll go through a really fast tutorial of some of the features I think are most beneficial, glossing over a bunch of small details.

There are plenty of excellent tutorials and online courses for Docker, and the documentation is really good, so you shouldn't struggle to find more information if what I show you piques your interest.

---

## What is Docker?

Note:
Docker is a "container runtime", which enables building, deploying, and managing Linux and Windows containers; I'll be focusing on Linux containers today.

---

## Wait, what are containers?

* Not virtual machines, but similar in some ways
* A combination of:
  * A disk image/filesystem chroot
  * Namespaces (what you can see, e.g. filesystem, processes)
  * Cgroups (what you can do, e.g. access to system resources like devices)
* Can be created with a handful of standard Linux commands

More detail in Liz Rice's talk "*Building a container from scratch in Go*": https://youtu.be/Utf-A4rODH8

Note:
Containers are very vaguely similar to virtual machines in that they create a generally isolated environment inside which you can run software. That's about where the similarity ends. A container is actually a disk image (a chroot) and collection of "namespaces" (what you can see) and "cgroups" (what resources you can use). There's a great explanation of this by [Liz Rice](https://www.youtube.com/watch?v=Utf-A4rODH8) (and its [sequel](https://www.youtube.com/watch?v=_TsSmSu57Zo)) (and another [possible reference](https://www.youtube.com/watch?v=sK5i-N34im8) with a huge amount of detail). The important points, though, are that for given processes (and their children) you can limit what they can see, and what they can do, so that they can't see or make changes to most of the host operating system.

You can actually create containers with a bunch of standard Linux commands, but it's rather clunky, and Docker abstracts all this away so you don't have to think about it, and makes it really easy.

---

## How can Docker and containers help?

* Consistent environment
* Segregation between apps
* Sandboxing and limiting privileges
* Isolating code and data
* Simplify deployment
* Note: "containerising" apps needn't be a big unmanageable project

---

## Huh?

Note:

OK, let's take a look at a slightly round-about example, from the ground up.

---

## Installing Docker

On most Redhat- or Debian-based systems, you can do this:

```sh
$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh
$ sudo usermod -aG docker "$USER
```

Remember to log out and back in for the user group change to take effect

Note:
Installing Docker is also really easy and [well documented](https://docs.docker.com/engine/install/); on most popular Linux distros it amounts to adding the Docker package repos and installing a couple of packages. Docker also have a "[convenience script](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script)" ([source code](https://github.com/docker/docker-install)) that does this for you. The alternative is that some distros have their own packages for Docker, but Docker recommend using the upstream packages because they're more likely to have updated security patches etc.

---

## If you want to play along

1. Create a Docker ID at https://hub.docker.com/signup
2. Browse to https://labs.play-with-docker.com/ and start a session
3. Click "Add new instance"
4. `git clone https://github.com/mattcen/lca2021-docker-talk`
5. `cd lca2021-docker-talk/demos`

---

## Running our first container

Once Docker is running, we can do something like this:

```sh
$ docker run --rm -it ubuntu bash
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
da7391352a9b: Pull complete
14428a6d4bcd: Pull complete
2c2d948710f2: Pull complete
Digest: sha256:c95a8e48bf88e9849f3e0f723d9f49fa12c5a00cfc6e60d2bc99d87555295e4c
Status: Downloaded newer image for ubuntu:latest
root@6e4f7117321d:/# ps -efa
UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  0 02:13 pts/0    00:00:00 bash
root         8     1  0 02:13 pts/0    00:00:00 ps -efa
root@6e4f7117321d:/# exit
$
```

Note:

This pulls down a tarball of an official minimal Ubuntu root filesystem from Docker Hub (Docker's container image repository or "registry"). It then creates an overlay copy-on-write filesystem over the top of that (read-only) image, chroots into it, sets up all our namespaces and cgroups to limit what we can see and do, and gives us that bash shell that we requested on the command line.

The `--rm` option tells Docker to delete the container once we're done with it, and the `-i` and `-t` options give us an interactive shell and a TTY. If we hadn't specified `bash` at the end, the container would've run the image's default command, which in this case happens to be `bash` anyway.

We can see from running `ps` within the container that it can't see any processes outside the container.

Not a particularly useful container, but bear with me.

---

## How are container images created?

* Filesystems that are usually built using a `Dockerfile`
* Can be based off other images
  * Creates "layers"
  * encouraging reusability
* Some images, like Ubuntu, aren't based off other images, but built from scratch

Note:

Some container images are root filesystems that have been built from scratch and aren't based on any other image. We won't talk too much about these except to say that there are a bunch of ""[Docker Official Images](https://docs.docker.com/docker-hub/official_images/)" on [Docker Hub](https://hub.docker.com/search?q=&type=image&image_filter=official) that can be considered trustworthy to use as base images for your applications.

Most other images are based off these using `Dockerfile`s.

A `Dockerfile` is a config that provides instructions on how to build an image. Each line in the file constitutes a "layer" of the image. Basically the upshot of this is that after every line, a snapshot of that image's filesystem is created such that it can be reused by this image or other images without having to rebuild it used without having to allocate more space (because copy-on-write).

Let's take a look:

---

## Dockerfile
A basic `Dockerfile` might be:

```docker
FROM ubuntu:20.04
CMD echo "Hello World!"
```

`docker build` looks for files called `Dockerfile` by default:

```sh
$ cd ~/lca2021-docker-talk/demos/docker_file
$ ls -l
total 4
-rw-r--r--    1 docker   staff           43 Jan 20 02:38 Dockerfile
$
```

---

## Building a Docker Image

The `-t` option to `docker build` 'tags' the image with the name 'helloworld'
```sh
$ docker build . -t helloworld
Sending build context to Docker daemon  25.09kB
Step 1/2 : FROM ubuntu:20.04
 ---> f643c72bc252
Step 2/2 : CMD echo "Hello World!"
 ---> Running in aca2515e7c8a
Removing intermediate container aca2515e7c8a
 ---> 2e1213f6db18
Successfully built 2e1213f6db18
Successfully tagged helloworld:latest
```
We then run a container based on that image with `docker run` again
```sh
$ docker run --rm -it helloworld
Hello World!
$
```

---

## Another Dockerfile

A more useful container might be:

```sh
$ cd ~/lca2021-docker-talk/demos/another_docker_file
$ ls -l
total 12
-rw-r--r--    1 docker   staff           70 Jan 20 02:57 Dockerfile
-rw-r--r--    1 docker   staff           25 Jan 20 02:46 index.html
-rw-r--r--    1 docker   staff          243 Jan 20 02:52 webserver.py
```

---

`Dockerfile`:
```docker
FROM python:3.9.1-buster
COPY . .
EXPOSE 8000
CMD python webserver.py
```

`index.html`:
```html
<!DOCTYPE html>
<html><body>
<p>Hello World from Python!</p>
</body></html>
```

`webserver.py`:
```python
import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
```

Note:

* Base image built `FROM` the official Docker Python image
* `COPY` everything from the current directory into the default directory inside the image
* `EXPOSE` port 8000 for access from the host operating system
* Set the container's defailt `CMD` to `python webserver.py`

---

We can put all this together into an image called 'hellopython' with:

```sh
$ docker build . -t hellopython
Sending build context to Docker daemon  4.096kB
Step 1/4 : FROM python:3.9.1-buster
 ---> da24d18bf4bf
Step 2/4 : COPY . .
 ---> 2e0b56c961fb
Step 3/4 : EXPOSE 8000
 ---> Running in 3e08636e7cb6
Removing intermediate container 3e08636e7cb6
 ---> c4079aa09149
Step 4/4 : CMD python webserver.py
 ---> Running in e4fb064f6438
Removing intermediate container e4fb064f6438
 ---> 74fb999e2f10
Successfully built 74fb999e2f10
Successfully tagged hellopython:latest
```

---

And then when we run it:
```sh
$ docker run --rm -d -p 8000:8000 hellopython
a2c890dd24c63852d373598ed934fca0f66b4605f8b8e19a244f2011925d3016
```
And test it:
```sh
$ curl http://localhost:8000
<!DOCTYPE html>
<html><body>
<p>Hello World from Python!</p>
</body></html>
```
And then we can stop (and, because of `--rm` above, remove) the container:
```sh
$ docker container ls
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
a2c890dd24c6        hellopython         "/bin/sh -c 'python …"   15 seconds ago      Up 15 seconds       0.0.0.0:8000->8000/tcp   silly_galois
$ docker container stop a2c
a2c
$ docker container ls -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
$
```

Note:

* `-d`  backgrounds the container
* `-p 8000:8000` forwards the host's port `8000` to the container's port `8000`
* We do a `curl` to confirm we can access the website
* Then we list running containers with `docker container ls`
* `docker container stop` our container. Note we can specify start of Container ID, or all of its randomly chosen name
* `docker container ls -a` to list all containers (running or not) to see it's gone

---

## Docker Summary

* Runs application in environment with known disk image
* Consistent between development, testing, and production environments
* Keeps app separate and "contained" so it doesn't affect host OS
* Makes management, upgrading, and removal trivial

---

## Running multi-container applications

* Multiple services, e.g. a web app + database?
* We can group these together
* Can be done manually with Docker, but Docker Compose is more elegant

---

## Installing `docker-compose`

```sh
$ sudo curl -L \
  "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   651  100   651    0     0    698      0 --:--:-- --:--:-- --:--:--   697
100 11.6M  100 11.6M    0     0  2231k      0  0:00:05  0:00:05 --:--:-- 3433k
$ sudo chmod +x /usr/local/bin/docker-compose
```

Note:
* Single-binary app
* Docker recommends this install process

---

## Using `docker-compose`

* Docker Compose looks for files called `docker-compose.yml` in current directory
* YAML file containing configurations for groups of related containers
* We'll make a simple web app that stores data in Redis

---

## Really simple web app
```sh
$ cd ~/lca2021-docker-talk/demos/simple_web_app
$ ls -l
total 16
-rw-r--r--    1 docker   staff          507 Jan 20 04:34 Dockerfile
-rw-r--r--    1 docker   staff          111 Jan 20 04:35 docker-compose.yml
-rw-r--r--    1 docker   staff           12 Jan 20 04:35 requirements.txt
-rw-r--r--    1 docker   staff          277 Jan 20 04:35 webapp.py
```

---

`webapp.py`:
```python
import redis
from flask import Flask

hello = Flask(__name__)
cache = redis.Redis(host='redis')

def refresh_count():
    while True:
        return cache.incr('refresh_count')

@hello.route('/')
def hi():
    return 'Hello Flask! Refresh count: {}.\n'.format(refresh_count())
```

`requirements.txt`:
```
flask
redis
```

Note:

* `webapp.py` runs a web server showing a dynamic count of page loads
* Count is stored in database on a host called `redis`
* `requirements.txt` are our Python dependencies for this app

---

`Dockerfile`:
```docker
FROM python:3.7-alpine
WORKDIR /app
ENV FLASK_APP=webapp.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
```

`docker-compose.yml`:
```yaml
version: "3.1"
services:
  web:
    build: .
    image: mattcen/simplewebapp
    ports:
      - "5000:5000"
  redis:
    image: "redis:alpine"
```

Note:

Dockerfile:
* Alpine is a minimal Linux distro optimised for containers
* `apk` is Alpine's package manager
* Base image `FROM` minimal Python image built on Alpine Linux
* Set our `WORKDIR` to `/app`
* Set a couple of environment variables
* Use `RUN` to install some dependencies within the container
* `COPY` in our `requirements.txt`
* `RUN pip install` to install dependencies
* `EXPOSE` our web server's port
* `COPY` in other files
* **IMPORTANT** We didn't do this earlier because then if we changed our files, Docker couldn't use it's cached image to speed up building
* Set default `CMD` to run our web app

docker-compose.yml:
* Set up a couple of services called `web` and `redis` (containers will use these like hostnames)
* `web` builds an image tagged `mattcen/simplewebapp` from the `Dockerfile` in the current directory
* Also forward port `5000` into container
* `redis` is a standard unmodified `redis` container from Docker Hub

---

## Let's run it!

```sh
$ docker-compose up -d
Creating network "simple_web_app_default" with the default driver
Building web
Step 1/10 : FROM python:3.7-alpine
 ---> 72e4ef8abf8e
[...]
Step 8/10 : EXPOSE 5000
 ---> Running in b86b56ac23cd
Removing intermediate container b86b56ac23cd
 ---> 71041c9a3620
Step 9/10 : COPY . .
 ---> d5a38cf1e575
Step 10/10 : CMD ["flask", "run"]
 ---> Running in b8fcb16313bd
Removing intermediate container b8fcb16313bd
 ---> 9f793cb0105a

Successfully built 9f793cb0105a
Successfully tagged mattcen/simplewebapp:latest
WARNING: Image for service web was built because it did not already exist. To rebuild this image you must use `docker-compose build` or `docker-compose up --build`.
Creating simple_web_app_web_1   ... done
Creating simple_web_app_redis_1 ... done
```

Note:

* `docker-compose up -d` starts up all services specified in the Compose file, and `-d` backgrounds it all
* Shows build process of each layer of the image
* **IMPORTANT** See here why we copied all our files at the end

---

## And test it

```sh
$ for redo in x y z; do curl http://localhost:5000; done
Hello Flask! Refresh count: 1.
Hello Flask! Refresh count: 2.
Hello Flask! Refresh count: 3.
```

Check it's actually modifying Redis:
```sh
$ docker-compose exec redis redis-cli get refresh_count
"3"
```

Note:

* Quick shell script to show that count increases on each request
* See it's modifying the Redis database using `docker-compose exec` to query `redis` container

---

## And clean up

```sh
$ docker-compose down
Stopping simple_web_app_redis_1 ... done
Stopping simple_web_app_web_1   ... done
Removing simple_web_app_redis_1 ... done
Removing simple_web_app_web_1   ... done
Removing network simple_web_app_default
```

---

## Pushing a Docker Image

* If you have a Docker Hub account, you can store images there
* … after authenticating to your Docker Engine with `docker login`
* These images can then be used by you or others
* I'll push this `mattcen/simplewebapp` image now for later use

```sh
$ docker push mattcen/simplewebapp
The push refers to repository [docker.io/mattcen/simplewebapp]
2c4609c155a4: Pushed
5cf997de0e7c: Pushed
43be206b777e: Pushed
0f309bc31411: Pushed
072957566e0f: Pushed
e2e42bb5b297: Mounted from library/python
e8f104f729a5: Mounted from library/python
5b2ca0c5db87: Mounted from library/python
b688d33030ff: Mounted from library/python
777b2c648970: Mounted from library/redis
latest: digest: sha256:abbd355bf17a52e2fc2df75374fa5642309a50f8e988b888b506ffc649c99e6d size: 2412
```

---

## Docker Compose summary

* Abstracts away Docker's functionality
* Automates creation, config, and management, of groups of containers

---

## Scaling with Docker Swarm

* Swarm mode is built into Docker Engine
* A Container Orchestrator (like Kubernetes, but easier)
* Can control Docker Engines on multiple machines
* Suitable for runnning redundant containers in production
* Swarm "Stacks" are groups of related containers
* "Stack" files are the same format as `docker-compose.yml`. Yay reuse!

Note:

Docker Compose isn't ideal for production; it's more useful for development and testing environments, but is missing a bunch of monitoring and other features that you'd typically want in a production environment.

Enter Docker Swarm. Docker Swarm is a container orchestrator. If you're aware of Kubernetes, Kubernetes is another container orchestrator, but Docker Swarm is simpler and more prescriptive, so may be more ideal for smaller workloads and environments.

Swarm is designed to manage multiple hosts which are running Docker, to distribute your workload 

Docker Swarm has the notion of "Stacks" which are logical groups of containers that form an app. Sound familiar? Yup, these are the same type of things as we just discussed regarding Docker Compose. Docker Swarm expects these container groups to be defined in a "Stack file", which, conveniently, is exactly the same format as a `docker-compose.yml`, with some extra features. If Docker Compose encounters any of the Swarm-specific features in a `docker-compose.yml` file, it'll just ignore them, meaning you can use the same file for both `docker-compose` and Docker Swarm.

[Swarm mode overview](https://docs.docker.com/engine/swarm/)

---

## Creating a Docker Swarm

Swarm is build directly into the standard Docker Engine, so we can trivially create a single-node swarm like this:

node1 (manager)
```sh
docker@node1:~$ docker swarm init
Swarm initialized: current node (q0xlwpksgfxt7s3un5vqjjsnc) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-5synm2ahj941bc1u44c8t1ms0oozze0u6qxotdcrlm9dkf8m6x-cg7w35ezyh8wgfblwcry1vo4f 192.168.99.104:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```
(May need `docker swarm init --advertise-addr eth0`)

Note:

* Gives an error if multiple network interfaces
* Specify advertise address by interface name or IP address
* `docker swarm init --advertise-addr eth0`
* Would work fine in swarm on its own. Could add other nodes though

---

## Adding nodes to a Swarm

node2 (worker)
```sh
docker@node2:~$ docker swarm join --token SWMTKN-1-5synm2ahj941bc1u44c8t1ms0oozze0u6qxotdcrlm9dkf8m6x-cg7w35ezyh8wgfblwcry1vo4f 192.168.99.104:2377
This node joined a swarm as a worker.
```
node3 (worker)
```sh
docker@node3:~$ docker swarm join --token SWMTKN-1-5synm2ahj941bc1u44c8t1ms0oozze0u6qxotdcrlm9dkf8m6x-cg7w35ezyh8wgfblwcry1vo4f 192.168.99.104:2377
This node joined a swarm as a worker.
```

---

## Listing Swarm nodes

node1 (manager)
```sh
docker@node1:~$ docker node ls
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS      ENGINE VERSION
q0xlwpksgfxt7s3un5vqjjsnc *   node1               Ready               Active              Leader              19.03.12
o5hau890eda7nzwqgrq1fc7if     node2               Ready               Active                                  19.03.12
p5gqdt2k09up8rlrr4nj2o3l0     node3               Ready               Active                                  19.03.12
docker@node1:~$
```

---

## Deploying a Stack

We can use our existing `docker-compose` file for our simple web app to deploy it as a stack:

```sh
docker@node1:~$ docker stack deploy -c docker-compose.yml webapp
Ignoring unsupported options: build

Creating network webapp_default
Creating service webapp_web
Creating service webapp_redis
```

* `build` unsupported in Swarm; needs pre-built image
* We pushed the image to Docker Hub earlier
* Because image is on Docker Hub, *only* local file we need is `docker-compose.yml`

---

## Checking Stack status

List configured stacks:
```sh
docker@node1:~$ docker stack ls
NAME                SERVICES            ORCHESTRATOR
webapp              2                   Swarm
```
List services within that stack:
```sh
docker@node1:~$ docker stack services webapp
ID                  NAME                MODE                REPLICAS            IMAGE                         PORTS
oquv4i6jc947        webapp_redis        replicated          1/1                 redis:alpine
w4iyas5q6nwo        webapp_web          replicated          1/1                 mattcen/simplewebapp:latest   *:5000->5000/tcp
$
```

---

## Removing our Stack

```sh
docker@node1:~$ docker stack rm webapp
Removing service webapp_redis
Removing service webapp_web
Removing network webapp_default
```

---

## Recap

* Docker makes it easy to run software in a contained, secure, consistent environment
* Docker Compose makes it easy to group several pieces of software together into an app
* Docker Swarm can run containers in production, across multiple physical machines if desired

---

## Migrating to containers

* Production servers can run Docker Engine in single-node Swarm
* No worse than non-Docker config
* Can slowly migrate apps to containers
* Still get some wins, like consistent deployment across environments
* Makes it easy for developers to start working on your code

---

##  Conclusion
Give Docker a shot; it encourages good software design discipline, and gives lots of flexibility!
