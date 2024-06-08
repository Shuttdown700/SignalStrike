### Overview:

paragraph

image

### Install Instructions

Linux using Bash:
```bash
# download package information from all configured sources 
sudo apt-get update
# install python
sudo apt-get install python
# verify python version
python --version
# create a virtual python environment titled "ewta_venv"
python -m venv ewta_venv
# activate the virtual environment
source ./bin/activate
# install required python modules
pip install -r requirements.txt
```

Windows using Git Bash:

Windows using PowerShell:

### Run EW Targeting Application

Windows
```cmd
run.bat
```
Linux
```bash
run.bash
```