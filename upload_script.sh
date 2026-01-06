#!/bin/bash
scp rename_planner.py leo@10.1.0.4:/home/leo/rename_planner/rename_planner.py
ssh leo@10.1.0.4 "
 cd ~/rename_planner
 source .venv/bin/activate
 python3 rename_planner.py /mnt/extra/backup /home/leo/rename_plan.sqlite
"
rm -f rename_plan.sqlite
scp leo@10.1.0.4:/home/leo/rename_plan.sqlite rename_plan.sqlite
ssh leo@10.1.0.4 "rm -f ~/rename_plan.sqlite"