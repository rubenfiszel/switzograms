cd gtfs
./get_data.sh

cd ../graph
python3 create_graph.py
cd ../notebooks
python3 compute_centers.py
cd ../graph
python3 process_graph.py
cd ..
