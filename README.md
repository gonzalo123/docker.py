## Handling M1 problems in Python local development using Docker.

I've got a new laptop. One MacbookPro with M1 processor. The battery performance is impressive and the performance is very good but not all are good things. M1 processor has a different architecture. Now we're using arm64 instead of x86_64.

The problem is when we need to compile. We need to take into account this. With python I normally use pyenv to manage different python version in my laptop and I create one virtualenv per project to isolate my environment. It worked like a charm, but now I'm facing problems due to the M1 architecture. For example to install a specific python version with pyenv I need to compile it. Also when I install a pip package and it provides a binary it must be available the M1 version. 

This kind of problems are a bit frustrating. Apple provide us rosetta to use x86 binaries but a simple pip install xxx turns into a nightmare. For me, it's not assumable. I want to deploy projects to production not become an expert in low level architectures. So, Docker is my friend.

My solution to avoid this kind of problems is Docker. Now I'm not using pyenv. If I need a python interpreter I build a Docker image. Instead of virtualenv I create a container.

PyCharm also allows me to use the docker interpreter without any problem. 

That's my python Dockerfile:

````dockerfile
FROM python:3.9.6 AS base

ENV APP_HOME=/src
ENV APP_USER=appuser

RUN groupadd -r $APP_USER && \
    useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER

WORKDIR $APP_HOME

ENV TZ 'Europe/Madrid'
RUN echo $TZ > /etc/timezone && \
apt-get update && apt-get install --no-install-recommends \
    -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

RUN pip install --upgrade pip

FROM base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $APP_HOME

COPY requirements.txt .
RUN pip install -r requirements.txt

ADD src .

RUN chown -R $APP_USER:$APP_USER $APP_HOME

USER $APP_USER
````

I can build my container:

````shell
docker build -t demo .
````

Now I can add interpreter in pycharm using my demo:latest image

If I need to add a pip dependency i cannot do using pip install locally. I've two options: Add the dependency within requirements.txt and build again the image or run pip inside docker container ("with docker run -it --rm ..."). To organize those script we can easily create a package.json file. 

```json
{
  "name": "flaskdemo",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "docker_local_build": "docker build -t $npm_package_name .",
    "freeze": "docker run -it --rm -v \"$PWD\"/src:/src $npm_package_name python -m pip freeze > requirements.txt",
    "local": "npm run docker_local_build && npm run freeze",
    "python": "docker run -it --rm -v $PWD/src:/src $npm_package_name:latest",
    "bash": "docker run -it --rm -v $PWD/src:/src $npm_package_name:latest bash"
  },
  "author": {
    "name": "Gonzalo Ayuso",
    "email": "gonzalo123@gmail.com",
    "url": "https://gonzalo123.com"
  },
  "license": "MIT"
}
```

## Extra

There's another problem with M1. Maybe you don't need to face it but if you build a docker container with a M1 laptop and you try to deploy this container in linux server (not a arm64 server) your containers doesn't work. To solve it you need to build your containers with the correct architecture. Docker allows us to do that. For example:

```commandline 
docker buildx build --platform linux/amd64 -t gonzalo/demo:prodution .
```


