[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![lint](https://github.com/guilhemsarcy/cryptolution/actions/workflows/lint.yml/badge.svg)
![doc](https://github.com/guilhemsarcy/cryptolution/actions/workflows/doc.yml/badge.svg)
![python version](https://img.shields.io/badge/dynamic/json?color=blue&label=python&query=python&url=https%3A%2F%2Fraw.githubusercontent.com%2Fguilhemsarcy%2Fcryptolution%2Fmaster%2Fpackage.json)
![dash version](https://img.shields.io/badge/dynamic/json?color=blue&label=dash&query=dependencies.dash&url=https%3A%2F%2Fraw.githubusercontent.com%2Fguilhemsarcy%2Fcryptolution%2Fmaster%2Fpackage.json)
![last commit](https://img.shields.io/github/last-commit/guilhemsarcy/cryptolution)
![commit activity](https://img.shields.io/github/commit-activity/m/guilhemsarcy/cryptolution?color=blue)

# The cryptocurrency market

The work is divided into two main parts : 
- collecting and cleaning data from Kraken API
- visualizing these data with an interactive Python App (Dash)

# Setup for local use

## Setup the environment

Example using conda : 
```
conda create -n cryptolution python=3.7
conda activate cryptolution
pip install -r requirements.txt
```

## Run the app
```
python modules/app/app.py
```

## Access the app locally
Go to : http://127.0.0.1:8050/ (default)


App screenshot :
![alt text](https://github.com/guilhemsarcy/cryptolution/blob/master/other/dashboard.JPG?raw=true)
