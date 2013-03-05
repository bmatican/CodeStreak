#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo nginx \
  -s stop \
  -g "pid /tmp/CodeStreak.nginx.pid;"
