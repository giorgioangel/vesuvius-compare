import open3d as o3d
import numpy as np
from flask import Flask, render_template, jsonify, request, send_from_directory
from time import time
import copy
import random
import json
import csv
from backend.pipelines import ThaumatoAnakalyptor
from backend.metrics import calculate_metrics
import hashlib
import os

app = Flask(__name__)

def load_base_config():
    with open('backend/config.json', 'r') as file:
        return json.load(file)

def random_center(base_volume_dim):
    z = random.randint(2000, base_volume_dim[0] - 2000)
    y = random.randint(2000, base_volume_dim[1] - 2000)
    x = random.randint(2000, base_volume_dim[2] - 2000)
    return [z, y, x]

def generate_hash(parameters):
    hash_object = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode())
    return hash_object.hexdigest()

def downsample_point_cloud(file_path, voxel_size=3):
    pcd = o3d.io.read_point_cloud(file_path)
    down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return np.asarray(down_pcd.points).tolist()  # Convert points to list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/volumes.html')
def render_volume():
    volume_id = request.args.get('volume')
    # Ensure volume_id is passed to the template correctly or used in the URL.
    return render_template('volumes.html', volume=volume_id)

@app.route('/files/<filename>')
def serve_file_in_dir(filename):
    # Append the required file extension
    filename_nrrd = f"{filename}.nrrd"
    # Construct the full directory path
    directory_path = os.path.join('static', 'data', 'volumes')
    # Construct the full file path
    # Serve the file from the directory
    return send_from_directory(directory_path, filename_nrrd)

@app.route('/generate')
def generate_point_clouds():
    methodA = request.args.get('methodA', default='ThaumatoAnakalyptor', type=str)
    methodB = request.args.get('methodB', default='ThaumatoAnakalyptor', type=str)
    radius = request.args.get('radius', type=int)
    
    centerZ = request.args.get('centerZ', type=int)
    centerY = request.args.get('centerY', type=int)
    centerX = request.args.get('centerX', type=int)

    config = load_base_config()

    config1 = copy.deepcopy(config[methodA])
    config2 = copy.deepcopy(config[methodB])

    if centerZ is not None and centerY is not None and centerX is not None:
        center = [centerZ, centerY, centerX]
    else:
        center = random_center([14000, 7500, 8000])

    config1['center'] = center
    config2['center'] = center
    config1['radius'] = radius
    config2['radius'] = radius

    # Generate a hash based on shared parameters
    shared_params = {
        "center": center,
        "radius": config1['radius'],  # Assuming radius is same across configs or adjust as needed
    }

    hash_code = generate_hash(shared_params)

    config1['hash'] = hash_code
    config2['hash'] = hash_code

    # Adjust filenames to include hash
    config1['type_number'] = 1
    config2['type_number'] = 2

    # Ensure the configs directory exists
    if not os.path.exists('results/configs'):
        os.makedirs('results/configs')

    # Save configurations with hash in filename
    with open(f"results/configs/{hash_code}_1.json", 'w') as f:
        json.dump(config1, f, indent=4)
    with open(f"results/configs/{hash_code}_2.json", 'w') as f:
        json.dump(config2, f, indent=4)

    # Create and process pipelines based on method
    if methodA == 'ThaumatoAnakalyptor':
        pipeline1 = ThaumatoAnakalyptor(config1)
    if methodB == 'ThaumatoAnakalyptor':
        pipeline2 = ThaumatoAnakalyptor(config2)

    start_time = time()
    pipeline1.process()
    time_1 = time() - start_time
    start_time = time()
    pipeline2.process()
    time_2 = time() - start_time

    # Load point clouds for metrics calculation
    cloud1_points = np.asarray(pipeline1.pcd.points)
    cloud2_points = np.asarray(pipeline2.pcd.points)

    # Load point clouds for metrics calculation
    cloud1_normals = np.asarray(pipeline1.pcd.normals)
    cloud2_normals = np.asarray(pipeline2.pcd.normals)
    # Calculate metrics
    metrics = calculate_metrics(cloud1_points, cloud2_points, cloud1_normals, cloud2_normals)

    return jsonify({
        "hash": hash_code, 
        "color1": "blue", 
        "color2": "red",
        "params1": config1,
        "params2": config2,
        "time1": time_1,
        "time2": time_2,
        "metrics": metrics
    })

@app.route('/clouds/<filename>')
def serve_point_cloud(filename):
    # Construct the full directory path
    path = os.path.join('static', 'data', 'clouds', filename)
    print("Trying to serve file from:", filename)  # Debug output

    if not os.path.exists(path):
        print("File not found")  # More debug output
        return jsonify({"error": "File not found"}), 404
    pcd = o3d.io.read_point_cloud(path)
    down_pcd = pcd.voxel_down_sample(voxel_size=1)
    points = np.asarray(down_pcd.points).tolist()
    return jsonify(points)

@app.route('/vote', methods=['POST'])
def handle_vote():
    hash_code = request.json['hash']
    winner = request.json['winner']
    file_path = os.path.join('results', 'preferences.csv')
    
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([hash_code, winner])
    
    return jsonify({"message": "Vote recorded successfully"}), 200

@app.route('/favicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.png', mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
