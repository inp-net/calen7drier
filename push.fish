#!/usr/bin/env fish
set v 2.0.4

docker build -t harbor.k8s.inpt.fr/net7/ade-feed-url:$v .
# latest tag
docker build -t harbor.k8s.inpt.fr/net7/ade-feed-url .
docker push harbor.k8s.inpt.fr/net7/ade-feed-url:$v
docker push harbor.k8s.inpt.fr/net7/ade-feed-url
sleep 10
kubectl -n ade-feed-url rollout restart deployment ade-feed-url
