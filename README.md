# scrape_colbase
Download image files match keyword from Colbase https://colbase.nich.go.jp

## About

This script download images with meta data from Colbase -- the web database provided by National Institutes of Cultural Heritage of Japan. 

## Install

### pip
pip install -r requirements.txt

### conda
conda install --file requirements.txt

### install chromewebdriver
You need to install a chromewebdriver that matches your version of Chrome.
#### MacOS example
conda install python-chromewebdriver-binary==103.0.5060.53.0
#### Windows example
pip install chromedriver-binary==103.0.5060.53.0

## How to use

python scrape_colbase.py --keyword \<keyword> --output_dir \<output directory>
