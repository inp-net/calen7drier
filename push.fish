#!/usr/bin/env fish
set v 1.0.6

docker build -t harbor.k8s.inpt.fr/net7/ade-feed-url:$v .
# latest tag
docker build -t harbor.k8s.inpt.fr/net7/ade-feed-url .
docker push harbor.k8s.inpt.fr/net7/ade-feed-url:$v
docker push harbor.k8s.inpt.fr/net7/ade-feed-url
