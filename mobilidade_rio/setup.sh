#!/bin/bash

# Load env file
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi
