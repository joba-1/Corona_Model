# Mini Installation Guide for Covid_Model on Suse Linux
sudo zypper in git python2 screen
mkdir ~/cov && cd ~/cov
git clone https://github.com/joba-1/Corona_Model
wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh
. ~/.bashrc
conda config --set auto_activate_base false
conda update conda
conda create -n gerdaenv python=3.8 geopandas
conda activate gerdaenv
cd Corona_Model/
pip install -e .
screen -mS cov
jupyter notebook

# Mini Update & Startup Guide for Covid_Model Jupyter Notebooks
cd ~/cov/Corona_Model
conda update conda
conda activate gerdaenv
git pull
pip install -e .
screen -mS cov
jupyter notebook

# Mini Startup Guide for Covid_Model Jupyter Notebooks
cd ~/cov/Corona_Model
conda activate gerdaenv
screen -mS cov
jupyter notebook

# Mini Screen Guide
Leave screen: [Ctrl][a] [d]
Reconnect screen: screen -r cov

