REM virtual env creation
call conda create -n cryptolution_prod python=3.7 -y
REM virtual env activation
call conda deactivate
call conda activate cryptolution_prod
REM requirements installation
call pip install -r requirements.txt
