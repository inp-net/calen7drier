#!/usr/bin/env fish
set v 1.0.5

docker build -t harbor.k8s.inpt.fr/net7/ade-feed-url:$v .
docker push harbor.k8s.inpt.fr/net7/ade-feed-url:$v
cd (realpath k8s) && git add . && git commit  -m "ade-feed-url: bump to $v" && git push
