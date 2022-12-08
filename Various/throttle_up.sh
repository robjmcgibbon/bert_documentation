#!/bin/bash

for job in 5818098 5818147 5818580 5818635 5829531 5829535 5829534 5829533 5829532
do
  scontrol update job $job ArrayTaskThrottle=8
  scontrol update job $job Nice=0
done
