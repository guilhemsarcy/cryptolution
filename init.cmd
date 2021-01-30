REM remove existing virtual env
call conda remove --name cryptolution --all -y
REM virtual env creation
call conda create -n cryptolution python=3.7 -y
REM virtual env activation
call conda deactivate
call conda activate cryptolution
REM requirements installation
call pip install -r requirements.txt
