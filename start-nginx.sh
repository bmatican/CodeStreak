#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OS=$(uname -s)
case $OS in
"Darwin")
  GROUP=www
  ;;
"Linux")
  GROUP=www-data
  ;;
*)
  echo "Unknown OS"
  ;;
esac

sudo nginx \
  -c $DIR/.nginx_conf \
  -g "pid /tmp/CodeStreak.nginx.pid; user $USER $GROUP;"
