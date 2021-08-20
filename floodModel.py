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

    def connectedPlanarFlood(self, val, ref_pt = (1800, 3500)):
        def recursiveCheck(pt, connected_check):
            if pt[0] > connected_check.shape[0]:
                return 0
            if pt[0] < 0:
                return 0
            if pt[1] > connected_check.shape[1]:
                return 0
            if pt[1] < 0:
                return 0
            if connected_check[pt] != -1:
                return connected_check[pt]
            else:
                val = recursiveCheck((pt[0]+1, pt[1]), connected_check) + recursiveCheck((pt[0]-1, pt[1]), connected_check)  + recursiveCheck((pt[0], pt[1]+1), connected_check) + recursiveCheck((pt[0], pt[1]-1), connected_check)
                connected_check[pt] = (val > 0)
                return (val > 0)

        def recursiveCheck2(pt, connected_check):
            print(pt)
            assert connected_check[pt] == 1
            pt1 = (pt[0]+1, pt[1])
            pt2 = (pt[0]-1, pt[1])
            pt3 = (pt[0], pt[1]+1)
            pt4 = (pt[0], pt[1]-1)
            pts = list()
            if pt[0] +1 < connected_check.shape[0]:
                pts.append(pt1)
            if pt[0] -1 >= 0:
                pts.append(pt2)
            if pt[1] +1 < connected_check.shape[1]:
                pts.append(pt3)
            if pt[1] -1 >= 0:
                pts.append(pt4)
            for cpt in pts:
                if connected_check[cpt] == -1:
                    if self.f_array[cpt] > 0:
                        connected_check[cpt] = 1
                        recursiveCheck2(cpt, connected_check)

        self.planarFlood(val)
        connected_check = np.zeros(self.f_array.shape, dtype = int) - 1
        connected_check[ref_pt] = 1
        connected_check[self.f_array == 0] = 0
        recursiveCheck2(ref_pt, connected_check)

    def connectedPlanarFlood2(self, val, ref_pt = (1800, 3500)):
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




    def connectedPlanarFloodPieces(self, val, ref_pt):
        piece_idc = self.getPiece(ref_pt)
        self.recursivePiece(piece, ref_pt)


    def getPiece(self, ref_pt):
        piece_x = ref_pt[0]//self.cuts
        piece_y = ref_pt[1]//self.cuts
        piece_idc = piece_x*self.r_array_shape[0]//self.cuts+piece_y
        return piece_idx
    def cutPieces(self, cuts = 500):
        shape = self.r_array.shape
        self.cuts = cuts
        x_pieces = shape[0]//cuts
        y_pieces = shape[1]//cuts
        self.r_array_pieces = []
        self.r_transform_pieces = []
        for i in range(x_pieces):
            for j in range(y_pieces):
                self.r_array_pieces.append(self.raster.read(1, window = R.windows.Window(cuts*i, cuts*j,500,500)))
                west,north = R.transform.xy(self.r_transform, cuts*i, cuts*j, offset='ul')
                self.r_transform_pieces.append(R.transform.from_origin(west, north, self.r_transform.xoff, self.r_transform.yoff))


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
    sys.setrecursionlimit(16000000)
    fm = floodModel(region = 'Kolhapur',
                    raster_file = 'DEM/cdne43u.tif')
    #fm.connectedPlanarFlood2(val = 460,ref_pt = (1250, 3440))
    #plt.imshow(fm.f_array, cmap = 'pink')
    #plt.show()
    #plt.imshow(fm.connected_f_array, cmap = 'pink')
    #plt.show()
    fm.planarFlood(val = 460)
    fm.connectedPlanarFlood2(val = 470,ref_pt = (1250, 3440))
    fm.f_array = fm.connected_f_array
    fm.f_array = fm.f_array.astype('int16')
    fm.storeFlood(filename = 'connected_planar_flood.tif')
