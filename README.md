# Vesuvius Compare
![Alt text](/screenshot.jpg?raw=true "Screenshot")
Video explanation: https://www.youtube.com/watch?v=0uF_WCdlAzA

## Overview
Vesuvius Compare is a Flask-based visualization tool designed for side-by-side pairwise comparison of automatic point cloud extraction and automatic surface segmentation of papyrus sheets from CT scans, as part of the Vesuvius Challenge. This application supports the execution and comparison of various computational pipelines, including ThaumatoAnakalyptor [https://github.com/schillij95/ThaumatoAnakalyptor/tree/main] and custom implementations. Users can interactively visualize outcomes, compute metrics, and save data to create a dataset aimed at refining algorithms through Reinforcement Learning from Human Feedback (RLHF) or hyperparameter finetuning.

## Installation

### Prerequisites
- Anaconda or Miniconda installed on your machine.
- Wide monitor or display. The visualization tool is not optimized for narrow displays.

### Environment Setup
1. **Clone the Repository:**
   Clone the repository to your local machine using:
   ```bash
   git clone https://github.com/giorgioangel/vesuvius-compare.git
   cd vesuvius-compare
   ```

2. **Create the Conda Environment:**
   Set up the Anaconda environment using the provided `environment.yml`:
   ```bash
   conda env create -f environment.yml
   conda activate vesuvius-compare
   ```

3. **Configure the Application:**
   Modify the `config.json` file to specify the path to the grid cells of Scroll 1.

   Currently, this is pointing to my Scroll 1 grid_cell volume folder, but it should point to yours:
   ```json
   "volume_path": "D:/vesuvius/Scroll1.volpkg/volume_grids/20230205180739/"
   ```

## Running the Application

1. **Launch the Server:**
   Start the application:
   ```bash
   python app.py
   ```

2. **Access the Web Interface:**
   Navigate to the following URL in a web browser:
   ```
   http://127.0.0.1:5000
   ```

## Usage

### Interactive Visualization
Upon accessing the web interface, users can:
- **Select Pipelines:** Choose two methods or pipelines for generating segmentations and point clouds.
- **Configure Parameters:** Define the block size (radius), sample a random block from Scroll 1, or specify exact coordinates for the central position of the block.
- **Generate and Compare Outputs:** Interactively visualize segmentation and point cloud results side by side for each method.

### Metrics
The tool calculates and displays key metrics to assess the quality of the point clouds and surface segmentations:
- **Hausdorff Distance:** Measures the maximum distance from a point in one set to the nearest point in the other set.
- **Chamfer Distance:** Calculates the mean nearest-neighbor distance between two point sets, computed both symmetrically and directionally.
- **Normals Metric:** Evaluates one minus the average cosine similarity between the normals of the nearest points in the two sets (in Euclidean space). The metrics go from 0 to 2, 0 means aligned, 1 means orthogonal, and 2 aligned in the opposite direction.

### Voting System
Users can vote on which method produces better results based on visual and metric-based assessments. This feedback is crucial for potentially enhancing the algorithms through RLHF or hyperparameter fine-tuning.

## Extending Vesuvius Compare

### Adding Custom Pipelines
1. **Implement Your Pipeline:**
   Create a new class in `./backend/pipelines.py` by subclassing `Pipeline`. Your class must implement the `process()` method:
   ```python
   class MyCustomPipeline(Pipeline):
      def process(self):
         # Insert custom processing logic here
         # The process method should end with the following commands
         self.create_point_cloud(labels_pc, normals)
         self.save_point_cloud(self.pcd)
         self.save_volume_as_nrrd(volume, "volume")
         self.save_predictions_as_nrrd(volume, labels_out.astype(np.uint16), str(self.type_number))
   ```

   For better modularization, you can define your functions by creating a new folder in `./backend/methods/` and importing it accordingly in the `./backend/pipelines.py`, before creating the custom subclass.

2. **Register New Pipeline:**
   Update `./backend/config.json` to include the new pipeline with its default parameters and update `./app.py` accordingly in this place:
   ```python
   # Create and process pipelines based on method
    if methodA == 'ThaumatoAnakalyptor':
        pipeline1 = ThaumatoAnakalyptor(config1)
    elif methodA == 'MyCustomPipeline':
        pipeline1 = MyCustomPipeline(config1)
   # etc.
   ```

3. **Modify the User Interface:**
   Add the new pipeline as an option in the HTML dropdown menus for both `methodA` and `methodB` to allow user selection.
   Example for `methodA`:
      ```HTML
      <select id="methodA">
         <option value="ThaumatoAnakalyptor">ThaumatoAnakalyptor</option>
         <option value="MyCustomPipeline">MyCustomPipeline</option>
      </select>
   ```

## Where are data collected:
The 3D chunks (unprocessed, processed with `methodA` and processed with `methodB`) are stored in `nrrd` format, that is used by the interactive visualization, in the folder
`./static/data/volumes/`.

The extracted point clouds (`methodA` and  `methodB`) are stored in `ply` format in the folder
`./static/data/clouds/`.

The parameters of both methods are stored in the folder
`./results/configs/`.

The dataset of collected preferences is stored in the file `./results/preferences.csv`.

## Credits and License
This work implements some functions from
- ThaumatoAnakalyptor [https://github.com/schillij95/ThaumatoAnakalyptor/tree/main]
- VolumeAnnotate [https://github.com/caethan/VolumeAnnotate/blob/main/main_app/loading.py]
- ThaumatoAnakalyptor-learn [https://github.com/tomhsiao1260/ThaumatoAnakalyptor-learn/blob/main/ThaumatoAnakalyptor/surface_detection.py]

The NRRD volume visualizer is based on the Three.js example [https://github.com/mrdoob/three.js/blob/master/examples/webgl_loader_nrrd.html]

The Point Cloud visualizer exploits Plotly.

This work is released under the MIT LICENSE.

