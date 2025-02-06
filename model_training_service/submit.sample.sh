#!/bin/bash
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=32GB
#SBATCH --gres=gpu:v100:1
##SBATCH --mem=200M

echo "Hello $USER! You are on node $HOSTNAME.  The time is $(date)."

module purge
module load mamba
mamba env create --file conda-env.yml
source activate claim-model-training-env

echo "Starting to run the python script. The time is $(date)."

# Update HF_HOME cache dir
export HF_HOME=/scratch/work/truongl3/DIME/HF_HOME_CACHE

# Configure wandb tracking
export WANDB_API_KEY="wandb-api-key"
wandb login

srun python3 /path/to/model_training.py

# Remove conda env
conda deactivate

echo "Successfully saved resulting model"