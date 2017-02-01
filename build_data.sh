cd gtfs
./get_data.sh
cd ../graph
python3 create_graph.py
python3 process_graph.py
cd ..
