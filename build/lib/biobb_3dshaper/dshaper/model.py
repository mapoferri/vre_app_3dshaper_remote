from pytorch3d.io import load_obj, load_objs_as_meshes, save_obj
from pytorch3d.transforms import Translate, Scale, Rotate, RotateAxisAngle
from pytorch3d.ops import sample_points_from_meshes
from pytorch3d.loss import chamfer_distance
from pytorch3d.structures import Meshes

import torch
import torch.nn as nn
import torch.nn.functional as F

import pytorch3d
import nibabel as nib
import SimpleITK as sitk
import trimesh
import numpy as np
import os, glob, shutil

# from scipy.ndimage.morphology import distance_transform_edt as edt
# from scipy.ndimage import convolve
# import segmentation_models_pytorch as smp

from tqdm import tqdm


class Model(nn.Module):
    def __init__(self, device, fix_meshes, mov_meshes, size=128):
        super().__init__()
        self.device = device
        # print('device', self.device)
        self.fix_meshes = load_objs_as_meshes([fix_meshes]).to(self.device)
        self.mov_meshes = load_objs_as_meshes([mov_meshes]).to(self.device)
        
        # Get the reference/target depth image
        
        # Create an optimizable parameter for the x, y, z translation of the mesh. 
        self.translation_params = nn.Parameter(
            torch.from_numpy(np.array([[0,0,0]], dtype=np.float32)).to(self.device))

        # Create an optimizable parameter for the x, y, z rotation of the mesh. 
        self.x = nn.Parameter(torch.tensor([1.0])).to(self.device)
        self.y = nn.Parameter(torch.tensor([1.0])).to(self.device)
        self.z = nn.Parameter(torch.tensor([1.0])).to(self.device)

    def forward(self):
        trans = Translate(self.translation_params, device=self.device)
        tverts = trans.transform_points(self.mov_meshes.verts_list()[0]).to(self.device)
        
        xrot = RotateAxisAngle(self.x, axis='X', device=self.device)
        tverts = xrot.transform_points(tverts).to(self.device)

        yrot = RotateAxisAngle(self.y, axis='Y', device=self.device)
        tverts = yrot.transform_points(tverts).to(self.device)

        zrot = RotateAxisAngle(self.z, axis='Z', device=self.device)
        tverts = zrot.transform_points(tverts).to(self.device)
        
        faces = self.mov_meshes.faces_list()[0]
        
        tmesh = pytorch3d.structures.Meshes(
            verts=[tverts.to(self.device)],   
            faces=[faces.to(self.device)],
        ).to(self.device)

        # compute loss
        sample_fix, normals_fix = sample_points_from_meshes(self.fix_meshes, 10000, return_normals=True)
        sample_mov, normals_mov = sample_points_from_meshes(tmesh, 10000, return_normals=True)

        # # We compare the two sets of pointclouds by computing (a) the chamfer loss
        loss_c, loss_n = chamfer_distance(sample_mov, sample_fix, x_normals=normals_mov, y_normals=normals_fix)

        # Calculate Hausdorff loss

        loss = loss_c + loss_n
        
        return loss, tmesh
