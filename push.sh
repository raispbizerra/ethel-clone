#!/bin/bash

git add src/database/ethel.db
today='exames '$(date +%d-%m)
git commit -m $today
git push origin master