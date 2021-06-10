#!/bin/sh
#PBS -A open
PATH="/Users/apf5504/work/Research/anaconda3/bin:$PATH"
echo "Job Started at $(date)"
python HyperParameterSearch.py
echo "Job Ended at $(date)"
