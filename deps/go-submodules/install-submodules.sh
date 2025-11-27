#!/bin/bash
set -o errexit -o nounset -o pipefail -o xtrace

OUTPUT_DIR=${GOBIN:-$(go env GOPATH)/bin}

cd kubernetes
make kubectl
cp _output/bin/kubectl "$OUTPUT_DIR/kubectl"
cd ..

cd oc
oc_version=$(git tag --points-at=HEAD | grep -E '[0-9]+\.[0-9]+\.[0-9]+' --only-matching)
make oc OS_GIT_VERSION="$oc_version"
cp ./oc "$OUTPUT_DIR/oc"
cd ..
