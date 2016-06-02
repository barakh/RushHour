#Kill all old processes
pkill -9 -u b python
python monitor.py &
#python multi_car.py # -p 20

python car.py # -p 20
