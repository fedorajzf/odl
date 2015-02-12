# -*- coding: utf-8 -*-
"""
simple_test.py -- a simple test script

Copyright 2014, 2015 Holger Kohr

This file is part of RL.

RL is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RL is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RL.  If not, see <http://www.gnu.org/licenses/>.
"""

from math import pi
import numpy as np
from matplotlib import pyplot as plt

from RL.datamodel import ugrid as ug
from RL.datamodel import gfunc as gf
from RL.builders import xray

# from RL.utility.utility import InputValidationError

# Initialize a sample grid
sample_shape = [100, 75, 50]
sample_voxel_size = 0.5
sample_grid = ug.Ugrid(sample_shape, spacing=sample_voxel_size)

# Initialize detector grid
detector_shape = [200, 150]
detector_pixel_size = 0.4
detector_grid = ug.Ugrid(detector_shape, spacing=detector_pixel_size)

# Set tilt angles
tilt_angles = np.linspace(-pi / 2, pi / 2, 181, endpoint=True)

# Initialize the geometry
xray_geometry = xray.xray_ct_parallel_geom_3d(sample_grid, detector_grid,
                                              axis=2, angles=tilt_angles,
                                              rotating_sample=True)

# Initialize the volume values (cuboid of value 1.0)
sample_fvals = np.zeros(sample_shape)
sample_fvals[25:75, 17:57, 20:30] = 1.0  # thicknesses 50, 40, 10
sample_func = gf.Gfunc(fvals=sample_fvals, spacing=sample_voxel_size)

# Show central slices
sample_func[50, :, :].display(saveto='test/temp/orig_x.png')
sample_func[:, 37, :].display(saveto='test/temp/orig_y.png')
sample_func[:, :, 25].display(saveto='test/temp/orig_z.png')

# Create forward and backward projectors
forward_projector = xray.xray_ct_parallel_3d_projector(xray_geometry)
backprojector = xray.xray_ct_parallel_3d_backprojector(xray_geometry)

# Compute projection
proj_func = forward_projector(sample_func)

#proj_func[:, :, 0].display()
#proj_func[:, :, 45].display()
#proj_func[:, :, 90].display()
#proj_func[:, :, 135].display()
#proj_func[:, :, 180].display()

# Compute backprojection
bp_func = backprojector(proj_func)

print(bp_func.shape)

#bp_func[50, :, :].display()
#bp_func[:, 37, :].display()
#bp_func[:, :, 25].display()


def landweber(fwd_proj, backproj, data, init_guess, niter, relax=0.5):

    cur_guess = init_guess.copy()
    for i in range(niter):
        residual = fwd_proj(cur_guess) - data
        residual_bp = backproj(residual)
        cur_guess = cur_guess - relax * residual_bp

    return cur_guess

# Start Landweber method with start value 0
init_guess = gf.Gfunc(fvals=0., shape=sample_shape, spacing=sample_voxel_size)

landw_sol = landweber(forward_projector, backprojector, proj_func,
                      init_guess, niter=1, relax=0.5)

landw_sol[50, :, :].display(saveto='test/temp/landw_3_x.png')
landw_sol[:, 37, :].display(saveto='test/temp/landw_3_y.png')
landw_sol[:, :, 25].display(saveto='test/temp/landw_3_z.png')

plt.show(block=True)
