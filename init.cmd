REM virtual env creation
call conda create -n cryptolution python=3.7 -y
REM virtual env activation
call conda deactivate
call conda activate cryptolution
REM requirements installation
call pip install -r requirements.txt
call pip uninstall pyzmq -y
call pip install pyzmq==20
REM additional packages installation
call jupyter nbextensions_configurator enable --sys-prefix
call jupyter contrib nbextension install --sys-prefix
