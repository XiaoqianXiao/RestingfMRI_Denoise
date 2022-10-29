import glob
import os
from nilearn import datasets

def get_parcelation_file_path(name: str) -> str:
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, name) + ".nii.gz"
    if os.path.exists(path):
        return path
    else:
        raise ValueError(f"File '{path}' is not part of denoise valid parcelation!")
    
def get_distance_matrix_file_path() -> str:
    ret = glob.glob(os.path.join(os.path.dirname(__file__), "*.npy"))
    if len(ret) != 1:
        raise ValueError("Unexpected number of parcelation files")
    return ret[0]
