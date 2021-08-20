import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import rasterio as R
import sys

class floodModel:
    def __init__(self, region, raster_file):
        self.region = region
        self.raster_file = raster_file
        self.raster = R.open(raster_file)
        self.r_array = self.raster.read(1)
        self.r_transform = self.raster.transform

    """Just fill up with water any parts of the DEM with value less than given val."""
    def planarFlood(self, val):
        flood_array = self.r_array.copy()
        flood_array[flood_array > val] = 0
        up_array = flood_array.copy()
        up_array[up_array > 0] = val
        flood_array = up_array - flood_array
        self.f_array = flood_array

    def generateGraph(self):
        self.g = nx.Graph()
        for i in range(self.f_array.shape[0]):
            for j in range(self.f_array.shape[1]):
                self.g.add_node((i,j))
                print(node)
                if self.f_array[i,j] > 0:
                    if i > 0:
                        if self.f_array[i-1,j] > 0:
                            self.g.add_edge((i-1,j), (i,j))
                    if j > 0:
                        if self.f_array[i,j-1] > 0:
                            self.g.add_edge((i,j-1), (i,j))

    """This function takes some starting reference point pixels that are flooded,
    and only floods those pixels below a certain threshold elevation which
    can be connected by a continuous water body to the reference point.
    """
    def connectedPlanarFlood(self, val, ref_pt = (1800, 3500)):
        recur_list = [ref_pt]
        self.planarFlood(val)
        connected_check = np.zeros(self.f_array.shape, dtype = int)
        #recur_check = np.zeros(self.f_array.shape, dtype = int)
        #recur_check[ref_pt] = 1
        connected_check[ref_pt] = 1

        while len(recur_list) > 0:
            #Grab the top stack point.
            pt = recur_list.pop(0)
            print(pt)
            assert self.f_array[pt] > 0
            assert connected_check[pt] == 1
            #assert recur_check[pt] = 1
            # Add the points to the recur_list stack.
            pt1 = (pt[0]+1, pt[1])
            pt2 = (pt[0]-1, pt[1])
            pt3 = (pt[0], pt[1]+1)
            pt4 = (pt[0], pt[1]-1)
            if pt[0] +1 < connected_check.shape[0]:
                if self.f_array[pt1] > 0 and connected_check[pt1] == 0:
                    connected_check[pt1] = 1
                    recur_list.append(pt1)
            if pt[0] -1 >= 0:
                if self.f_array[pt2] > 0 and connected_check[pt2] == 0:
                    connected_check[pt2] = 1
                    recur_list.append(pt2)
            if pt[1] +1 < connected_check.shape[1]:
                if self.f_array[pt3] > 0 and connected_check[pt3] == 0:
                    connected_check[pt3] = 1
                    recur_list.append(pt3)
            if pt[1] -1 >= 0:
                if self.f_array[pt4] > 0 and connected_check[pt4] == 0:
                    connected_check[pt4] = 1
                    recur_list.append(pt4)

        self.connected_f_array = self.f_array*connected_check


    def storeFlood(self, filename = 'flood.tif', driver='GTiff',crs='+proj=latlong'):
        flood = R.open( filename,
                        'w',
                        driver=driver,
                        height=self.raster.shape[0],
                        width=self.raster.shape[1],
                        count=1,
                        dtype=self.f_array.dtype,
                        crs=crs,
                        transform = self.r_transform
                        )

        flood.write(self.f_array, 1)
        flood.close()


if __name__ == '__main__':
    fm = floodModel(region = 'Kolhapur',
                    raster_file = 'DEM/cdne43u.tif')
    fm.planarFlood(val = 460)
    fm.connectedPlanarFlood(val = 470,ref_pt = (1250, 3440))
    fm.f_array = fm.connected_f_array
    fm.f_array = fm.f_array.astype('int16')
    fm.storeFlood(filename = 'connected_planar_flood.tif')
