MONITOR_SET=/home/tadas/zmeventnotification/scheduling/monitor-set.sh
LOG_FILE=/home/tadas/zmeventnotification/scheduling/monitor-set.log
STOP_CMD=Monitor
START_CMD=Modect

echo "bash $MONITOR_SET $STOP_CMD 20 21 >> $LOG_FILE 2>&1" | at 08:05 2024-12-24
