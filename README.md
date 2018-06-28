# InaSAFE Realtime Processor

This repository contains code specific for InaSAFE Realtime Hazard
processing service, or in short (IRH). This service is used in BNPB to
gather and integrate Hazard data from various agencies and convert it
into InaSAFE Hazard Layers to be further processed by InaSAFE Realtime
System.

**Statuses:**

[![Build Status](https://travis-ci.org/inasafe/inasafe-realtime.svg?branch=develop)](https://travis-ci.org/inasafe/inasafe-realtime)

[![codecov](https://codecov.io/gh/inasafe/inasafe-realtime/branch/develop/graph/badge.svg)](https://codecov.io/gh/inasafe/inasafe-realtime)

**Architecture:**

[![Architecture](https://github.com/inasafe/inasafe-realtime/raw/develop/docs/Kartoza%20-%20DFAT-%2031%20January%20-%202018%20-%20Status.png)]


# Development Guide

This document describes how to get the IRH environment setup. We mainly
develops using PyCharm Professional IDE, courtesy of JetBrains. This
setup will automatically generate project configuration for PyCharm.

**Prerequisites:**

- Running MacOS or Ubuntu 16.04/16.10
- Docker Engine installed
- Ansible is installed (pip install ansible or brew install ansible)
- PyCharm professional is installed (tested versions: 2016.3, 2017.1, 2017.2, or 2017.3)


## Step 1: Checkout inasafe-realtime repo

Checkout or clone main repository or your own fork.

```
git clone git@github.com:inasafe/inasafe-realtime.git
```

We work in **develop** branch.

Open the checkout directory in PyCharm as a project.
This is important because the ansible scripts in the next step depend
on the .idea directory that gets created there.
Then close pycharm again while you run the next steps.

## Step 2: Configure specific options for your local system

In this step, we configure our project generator to fill in
some configuration settings.

```
cd  deployment/ansible/development/group_vars/
cp all.sample.yml all.yml
```

Edit all.yml for your own system.

```
use_pycharm (set to **yes** if using pycharm, **no** for otherwise)
remote_user (your username)
remote_group (your user’s group)
project_path (the location of the project)
interpreters →  inasafe_realtime →  ipaddress: (your local machine ipaddress)
```


Example:

```
  3 use_pycharm: yes
  4 remote_user: timlinux
  5 remote_group: staff
  6 project_path: "/Users/timlinux/dev/docker/inasafe-realtime"
  8 interpreters:
  9   inasafe_realtime:
 10     name: 'InaSAFE Realtime Container'
 11     domain_alias: 'docker-realtime-orchestration'
 12     ssh_port: &inasafe_realtime_ssh_port 35103
 13     pycharm_helpers: /root/.pycharm_helpers
 14     ipaddress: &inasafe_realtime_host_ip 192.168.1.113
 ```


Generate your project config:

```
make setup-ansible
```

Fill in your sudo password (to change /etc/hosts entry)
Choose your pycharm version.

Ansible should return something like this:

```
PLAY RECAP *********************************************************************
localhost                  : ok=13   changed=3    unreachable=0    failed=0
````

Failed=0 is the important part here.
After this, you are safe to restart PyCharm and open the project.


## Step 3: Running the local development build

We mainly uses docker to build our development environment.

For the rest of the instruction, execute **make** commands from ```deployment```
folder.

This will build the docker images

```
make build
```

Upstart your docker containers

```
make up
```

To check that your services running, run:

```
make status
```


This will run the environment in docker containers and then use a
remote interpreter in PyCharm so that you can debug. Open pycharm again.
After the process finished, you need to open your PyCharm preference to
make the PyCharm aware of the remote python interpreter.
You will see these 3 remote interpreters:

InaSAFE Realtime Hazard Container → For the celery worker
InaSAFE Realtime Shakemap Monitor Container  → Monitor the shakemap folder (for initial shakemap type)
InaSAFE Realtime Shakemap Corrected Monitor Container → Monitor shakemap the shakemap folder (for data-informed shakemap type)

## Step 4: Running in develop mode

If the interpreter is connected properly in PyCharm, you should be able
to see python package lists in ```Project Interpreter``` Dialog.

To run the code using PyCharm configuration, choose your appropriate Run
configuration from Run/Debug Configuration Dropdown.

Run the “Run Monitoring Service” or "Run Monitoring Service - Shakemap Processed"
run configuration in PyCharm to start service for respective shakemap monitoring type.

Run the “Celery Workers” run configuration in PyCharm to start Celery Task service for IRH.


## Step 5: Testing in develop mode

In addition to run configuration in ```Run``` mode, you can also run it in
```Debug``` mode by clicking the Debug button. This allows you to use PyCharm
debugging features like breakpoints, etc.

To test your shakemap monitor, you need drop a shake grid.xml file into
‘shakemaps’ directory in this kind of directory structure:
shakemaps/\<YYMMDDHHmmss>/grid.xml

If it’s working properly, the worker will pick up the grid.xml,
and process it.

You can run unittests in PyCharm. To do so, highlight your
test files, methods or packages and open context menu, then
click Run unittests...

Tests that runs in PyCharm will run in synchronous mode.

## Step 6: Production image build

Will be implemented later

## Step 7: Publishing updated images to production

Will be implemented later


# Advanced Guide

## Change celery async mode

InaSAFE Realtime Hazard services uses Celery to handle loads. Because
of the way celery architecture works, it was optimized for asynchronous
job. However, sometimes debugging only functional usage in synchronous
mode is preferred. That is why the default pycharm unittests run in
synchronous mode. To switch into async mode, you can put additional
configuration in your `all.yml` file like this:

```
inasafe_realtime_worker:
  environment:
    task_always_eager: True
    on_travis: False
```

Explanation for above: put another yaml key called `task_always_eager`
and `on_travis` in that `inasafe_realtime_worker.environment` tree.

After that, run again `make setup-ansible` to refresh your new configuration

In celery async mode, your test will hang while waiting for task results.
Your task can only be executed by the worker, so make sure to start
`Celery Workers` Run configuration before running your tests.

## Configuring mock InaSAFE Django server

InaSAFE Realtime Hazard services will try to communicate with InaSAFE Django
via REST API. Your test will fail if you do not put correct credentials
for the rest API. Yaml configuration tree for this is in:

```
realtime_rest_api:
  host: *inasafe_realtime_host_ip
  port: 61102
  user: test@realtime.inasafe.org
  password: thepaassword
```

Change the value into your actual InaSAFE Django test instance.

If you don't want to use real django server, you can use preconfigured
mock server. Change above value into this:

```
realtime_rest_api:
  host: localhost
  port: 8000
  user: test@realtime.inasafe.org
  password: thepaassword
```

Then run `make setup-ansible` to refresh your configuration.

Note that this is a mock server that only able to test REST request but
don't actually check the content and always returned HTTP 200 code (OK).
