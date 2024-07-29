#!/bin/bash
#SBATCH --time=08:15:00
#SBATCH --output=sbert_array_job_%A_%a.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=32GB
#SBATCH --gres=gpu:v100:1
##SBATCH --mem=200M

echo "Hello $USER! You are on node $HOSTNAME.  The time is $(date)."

module purge
module load mamba
mamba env create --file conda-env.yml
source activate claim-detection-env

echo "Starting to run the python script. The time is $(date)."

# Configure MLflow to communicate with a Databricks-hosted tracking server
export MLFLOW_TRACKING_URI=databricks
export MLFLOW_TRACKING_USERNAME="email"
export MLFLOW_TRACKING_PASSWORD="password" 

srun python3 /scratch/work/truongl3/DIME/auto_factchecker_pipeline/claim_detection/hyperparameter_tuning.py

# Remove conda env
conda deactivate

echo "Successfully saved model"
