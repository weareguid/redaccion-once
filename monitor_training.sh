#!/bin/bash

# Monitoring script for training progress
while true; do
    echo "=== $(date) ==="
    echo "GPU Usage:"
    nvidia-smi
    echo "Memory Usage:"
    free -h
    echo "Disk Usage:"
    df -h
    echo "Training Log:"
    tail -n 20 training.log
    echo "=================="
    sleep 300  # Update every 5 minutes
done
