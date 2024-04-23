import numpy as np
from scipy.spatial import KDTree
from scipy.spatial.distance import directed_hausdorff

def chamfer_distance_kdtree(cloud1, cloud2, normals1, normals2):
    # Create KDTree objects for each cloud
    tree1 = KDTree(cloud1)
    tree2 = KDTree(cloud2)

    # Find closest points and calculate squared distances
    # Query from cloud1 to cloud2
    dist_cloud1_to_cloud2, indices_12 = tree2.query(cloud1)
    dist_cloud1_to_cloud2 = np.mean(np.square(dist_cloud1_to_cloud2))  # Squaring the distances
    # Query from cloud2 to cloud1
    dist_cloud2_to_cloud1, indices_21 = tree1.query(cloud2)
    dist_cloud2_to_cloud1 = np.mean(np.square(dist_cloud2_to_cloud1))  # Squaring the distances

    # Compute the mean of the minimum distances for both directions
    chamfer_dist = dist_cloud1_to_cloud2 + dist_cloud2_to_cloud1

    cosdist_cloud1_to_cloud2 = np.mean(1-np.einsum('ij,ij->i', normals1, normals2[indices_12]))
    cosdist_cloud2_to_cloud1 = np.mean(1-np.einsum('ij,ij->i', normals2, normals1[indices_21]))

    cos_dist = cosdist_cloud1_to_cloud2 + cosdist_cloud2_to_cloud1
    return dist_cloud1_to_cloud2, dist_cloud2_to_cloud1, chamfer_dist, cosdist_cloud1_to_cloud2, cosdist_cloud2_to_cloud1, cos_dist

def calculate_metrics(cloud1, cloud2, normals1, normals2):
    # Convert numpy arrays if they're not already np.ndarray
    if not isinstance(cloud1, np.ndarray):
        cloud1 = np.array(cloud1)
    if not isinstance(cloud2, np.ndarray):
        cloud2 = np.array(cloud2)
    if not isinstance(cloud1, np.ndarray):
        normals1 = np.array(normals1)
    if not isinstance(cloud2, np.ndarray):
        normals2 = np.array(normals2)
    # Hausdorff distance
    hausdorff_dist = max(directed_hausdorff(cloud1, cloud2)[0], directed_hausdorff(cloud2, cloud1)[0])

    # Chamfer distance using KDTree
    c12, c21, chamfer_dist, n12, n21, normals_dist = chamfer_distance_kdtree(cloud1, cloud2, normals1, normals2)

    return {
        "hausdorff_distance": hausdorff_dist,
        "chamfer_12": c12,
        "chamfer_21": c21,
        "chamfer_distance": chamfer_dist,
        "normals_12": n12,
        "normals_21": n21,
        "normals_distance": normals_dist
    }