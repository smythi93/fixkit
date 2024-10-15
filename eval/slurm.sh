#!/bin/bash

#SBATCH --job-name=eval
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8gb
#SBATCH --partition=std
#SBATCH --nodelist=gruenau1,gruenau2,gruenau3,gruenau4,gruenau5,gruenau6,gruenau7,gruenau8,gruenau9,gruenau10
#SBATCH --time=24:00:00
#SBATCH --array=0-20  # Adjust this range based on the number of tasks
#SBATCH --output=/vol/tmp/werkkai/slurm_logs/slurm_%A_%a.out
#SBATCH --error=/vol/tmp/werkkai/slurm_errors/slurm_%A_%a.err



# Print the SLURM_ARRAY_TASK_ID for debugging
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# Activate the conda environment directly
conda activate eval

# go to directory
cd ~/dev/fixkit/eval

# Run the Python script with the job index as an argument
#python3 ./eval_student_assignments.py $SLURM_ARRAY_TASK_ID