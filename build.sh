#!/bin/bash
set -e
rm -rf package lambda.zip
mkdir -p package

pip install -r src/requirements.txt -t package
cp -r src/*.py package/
cp -r src/utils package/

cd package
zip -r ../lambda.zip .
cd ..