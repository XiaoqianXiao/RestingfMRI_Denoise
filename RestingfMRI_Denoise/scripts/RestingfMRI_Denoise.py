#scripts
#!/bin/sh
if command -v "python3" > /dev/null
then
    python3 -O -m RestingfMRI_Denoise "$@"
else
    python -O -m RestingfMRI_Denoise "$@"
fi
