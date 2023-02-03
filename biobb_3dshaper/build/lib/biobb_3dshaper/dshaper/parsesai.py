#!/usr/bin/env python3

"""Module containing the Template class and the command line interface."""
import argparse
import pandas as pd
import numpy as np
import os
import shutil, glob
from pathlib import PurePath
# from biobb_guild.guild.common import *
from tqdm import tqdm
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_3dshaper.dshaper.model import Model
import torch

class Registration(BiobbObject):

    def __init__(self, input1_meshes_path, input2_meshes_path, output_meshes_path, properties=None, **kwargs) -> None:

        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # 2.1 Modify to match constructor parameters
        # Input/Output files
        self.io_dict = { 
                'in1': { 'input1_meshes_path': input1_meshes_path},
                'in2': { 'input2_meshes_path': input2_meshes_path},
            'out': {'output_meshes_path': output_meshes_path} 
        }
        self.files = sorted(os.listdir(self.io_dict['in1']['input1_meshes_path']))
        self.properties = properties
        self.device = self.properties.get('device', 'cpu')

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Template <template.template.Template>` object."""

        # 4. Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()       

        self.run()

        return 0

    def run(self):
        
        with tqdm(self.files, 'Optimizing...') as iterator:
	    
            for idx, file in enumerate(iterator):
                
                # v, f = [], []
                
                # for l in ['L1', 'L2', 'L3', 'L4', 'L5']:
                    
                ct_mesh_file = os.path.join(self.io_dict['in1']['input1_meshes_path'], file)
                mr_mesh_file = os.path.join(self.io_dict['in2']['input2_meshes_path'], file)
                
                if (not os.path.exists(ct_mesh_file)) or (not os.path.exists(mr_mesh_file)) :
                    continue
                
                if os.path.exists(self.io_dict['out']['output_meshes_path']):
                    continue
                else:
                    os.mkdir(self.io_dict['out']['output_meshes_path'])
                
                model = Model(self.device, mr_mesh_file, ct_mesh_file).to(self.device)
                optimizer = torch.optim.Adam(model.parameters(), lr=2.0)
                
                for i in range(1001):
                    print("Running iteration: ", i)
                   # continue
                    optimizer.zero_grad()
                    loss, tmesh = model()
                    loss.backward()
                    optimizer.step()
                
                torch.save(model.state_dict(), self.io_dict['out']['output_meshes_path']+'/'+file.replace('.obj', '.pth'))
                    # verts, faces = tmesh.verts_packed(), tmesh.faces_packed()
                    # save_file = ct_mesh_file.replace('CT_Shapes_OBJ', '2023/CT_Shapes_OBJ_Transformed')


def registration(input1_mesh_path:str, input2_mesh_path:str, output_mesh_path:str, properties: dict = None, **kwargs) -> int:
    """Create :class:`Template <template.template.Template>` class and
    execute the :meth:`launch() <template.template.Template.launch>` method."""

    # return ParseHippie(properties=properties, **kwargs).launch()
    return Registration(input1_mesh_path, input2_mesh_path, output_mesh_path, properties, **kwargs).launch()

def main():

    parser = argparse.ArgumentParser(description='Description for the template module.')
    parser.add_argument('-c','--config', default='conf.yml')
    parser.add_argument('-i1','--input1', default='/home/bscuser/Escritorio/biobbs/biobb_3dshaper/inp1')
    parser.add_argument('-i2','--input2', default='/home/bscuser/Escritorio/biobbs/biobb_3dshaper/inp2')
    parser.add_argument('-o','--output', default='/home/bscuser/Escritorio/biobbs/biobb_3dshaper/weights')

    args = parser.parse_args()
    args.config = args.config or "{}"

    properties = settings.ConfReader(config=args.config).get_prop_dic()
    # os.makedirs('/media/snatarajan/data/2023/MySpine/shapes/vert_mr_transformed', exist_ok=True)
    # for l in ['L1', 'L2', 'L3', 'L4', 'L5']:
        # os.makedirs('/media/snatarajan/data/2023/MySpine/shapes/vert_mr_transformed/' + l, exist_ok=True)

    # 11. Adapt to match Class constructor (step 2)
    # Specific call of each building block
    registration(input1_mesh_path=args.input1, input2_mesh_path=args.input2, output_mesh_path=args.output, properties=properties)

    # start_registration(device, files)

if __name__ == '__main__':
    main()

# 12. Complete documentation strings
