#!/bin/bash

#SBATCH --job-name=eval
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --partition=std
#SBATCH --nodelist=gruenau7,gruenau8
#SBATCH --time=48:00:00
#SBATCH --array=0-199  # Adjust this range based on the number of tasks
#SBATCH --output=/vol/tmp/werkkai/slurm_logs/slurm_%A_%a.out
#SBATCH --error=/vol/tmp/werkkai/slurm_errors/slurm_%A_%a.err

# Print the SLURM_ARRAY_TASK_ID for debugging
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# Activate the conda environment directly
source /usr/local/anaconda3-2023.03/bin/activate eval

#man könnte das alles in vol/tmp machen und da vorher noch git clone dann muss man da aber fetch und checkout evaluation machen

#create working directory and go to working directory
cp -r ~/dev/fixkit/eval /vol/tmp/werkkai/eval_$SLURM_ARRAY_TASK_ID
cd /vol/tmp/werkkai/eval_$SLURM_ARRAY_TASK_ID

# Run the Python script with the job index as an argument
python ./eval_student_assignments.py $SLURM_ARRAY_TASK_ID

#cleanup
rm -r /vol/tmp/werkkai/eval_$SLURM_ARRAY_TASK_ID