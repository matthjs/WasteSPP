#!/bin/bash

PROJECT=$1
PROJECT_NAME=$2
PROG_LANG=$3

ARCAN_PATH=$4
REPOSITORY_PATH=$5
OUT_PATH=$6
LOGS_PATH=$7

# /$PROJECT_NAME removed from REPISITORY_PATH for n
 # -v before this originally

/component-annotator/src/arcan/arcan.sh analyze \
              -i $REPOSITORY_PATH/$PROJECT_NAME -p $PROJECT_NAME \
              --remote $PROJECT \
              -o $OUT_PATH -l $PROG_LANG -f $ARCAN_PATH/filters.yaml \
              output.writeDependencyGraph=true \
              output.writeAffected=false \
              output.writeComponentMetrics=False \
              output.writeSmellCharacteristics=False \
              metrics.componentMetrics=none \
              metrics.smellCharacteristics=none \
              metrics.indexCalculators=none \
              detectors.smellDetectors=none \
              -e --startDate 1-1-1 --endDate 2024-12-31 --intervalDays 28  2>&1 |& tee outfile $LOGS_PATH/$PROJECT_NAME.log