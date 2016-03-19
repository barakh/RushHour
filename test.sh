#Kill all old processes
pkill -9 -u b python
python monitor.py &
python car.py -p 20
