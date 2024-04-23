import numpy as np
import torch
from backend.scroll_loading import load_tifstack
import open3d as o3d
from typing import Tuple, Dict
import os

class Pipeline:
    def __init__(self, config: Dict) -> None:
        self.volume_path = config.get("volume_path", "")
        self.center = tuple(config.get("center", (0, 0, 0)))
        self.radius = config.get("radius", 50)
        self.device = config.get("device", "cpu")
        self.hash = config.get("hash", "")
        self.type_number = config.get("type_number", 0)

    def load_volume(self) -> np.ndarray:
        """Load the volume data from the specified path."""
        return load_tifstack(self.volume_path)

    def process(self):
        """Process the volume data. This should be implemented by subclasses."""
        raise NotImplementedError("Process method must be implemented by subclasses.")

    def preprocess_volume(self, data: np.ndarray) -> np.ndarray:
        section = data[
            self.center[0] - self.radius:self.center[0] + self.radius,
            self.center[1] - self.radius:self.center[1] + self.radius,
            self.center[2] - self.radius:self.center[2] + self.radius,
        ]
        return section.astype(np.float32) / float(np.iinfo(np.uint16).max)
    
    def save_point_cloud(self, pcd: o3d.geometry.PointCloud) -> None:
        pcd_filename = f"{self.hash}_{self.type_number}.ply"
        file_path = os.path.join('static', 'data', 'clouds', pcd_filename)
        o3d.io.write_point_cloud(file_path, pcd)

    def save_volume_as_nrrd(self, volume: np.ndarray, filename: str) -> None:
        import SimpleITK as sitk
        # Ensure the correct data type and dimensions for SimpleITK
        sitk_volume = sitk.GetImageFromArray(volume.astype(np.float32))
        
        # Specify the file path
        file_path = os.path.join('static', 'data', 'volumes', f"{self.hash}_{filename}.nrrd")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the image to disk in NRRD format
        sitk.WriteImage(sitk_volume, file_path)

    def save_predictions_as_nrrd(self, volume: np.ndarray, pc: np.ndarray, filename: str):
        volume[pc == 1] = 1
        file_path = os.path.join('static', 'data', 'volumes', f"{self.hash}_{filename}.nrrd")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        import SimpleITK as sitk
        sitk_volume = sitk.GetImageFromArray(volume.astype(np.float32))

        # Write the image to disk in NRRD format
        sitk.WriteImage(sitk_volume, file_path)

    def create_point_cloud(self, labels_pc: np.ndarray, normals: np.ndarray) -> o3d.geometry.PointCloud:
        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(labels_pc)
        self.pcd.normals = o3d.utility.Vector3dVector(normals)
        self.pcd.normalize_normals()

class ThaumatoAnakalyptor(Pipeline):
    def __init__(self, config: Dict) -> None:
        super().__init__(config)
        # Additional specific configurations for Thaumato
        self.blur_size = config.get("blur_size", 3)
        self.sobel_chunks = config.get("sobel_chunks", 4)
        self.sobel_overlap = config.get("sobel_overlap", 3)
        self.window_size = config.get("window_size", 20)
        self.stride = config.get("stride", 20)
        self.threshold_der = config.get("threshold_der", 0.1)
        self.threshold_der2 = config.get("threshold_der2", 0.001)
        self.global_reference_vector = config.get("global_reference_vector", [0, -1, 0])

    def process(self):
        from backend.methods.thaumato.surface_detection import surface_detection
        # Load volume data
        data = self.load_volume()
        volume = self.preprocess_volume(data)
        volume_tensor = torch.from_numpy(volume).to(torch.float32).to(self.device)
        labels_out, labels_pc, normals = surface_detection(volume_tensor, torch.tensor(self.global_reference_vector).to(self.device), self.blur_size, self.sobel_chunks, self.sobel_overlap, self.window_size, self.stride, self.threshold_der, self.threshold_der2)
        self.create_point_cloud(labels_pc, normals)
        self.save_point_cloud(self.pcd)
        self.save_volume_as_nrrd(volume, "volume")
        self.save_predictions_as_nrrd(volume, labels_out.astype(np.uint16), str(self.type_number))