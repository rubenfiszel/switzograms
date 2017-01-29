wget -O gtfs.zip http://gtfs.geops.ch/dl/gtfs_complete.zip
unzip -o gtfs.zip
python3 -u process_gtfs.py
