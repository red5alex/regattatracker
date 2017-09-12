# -*- coding: utf-8 -*-
"""
Map tile acquisition
--------------------

Demonstrates cartopy's ability to draw map tiles which are downloaded on
demand from the Stamen tile server. Internally these tiles are then combined
into a single image and displayed in the cartopy GeoAxes.

"""
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry as sgeom

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

import gpxpy.parser as parser


import matplotlib.pyplot as plt
import matplotlib.lines as mlines



from matplotlib.path import Path
import matplotlib.patches as patches

def newline(p1, p2):
    ax = plt.gca()
    xmin, xmax = ax.get_xbound()

    if(p2[0] == p1[0]):
        xmin = xmax = p1[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmax-p1[0])
        ymin = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmin-p1[0])

    l = mlines.Line2D([xmin,xmax], [ymin,ymax])
    ax.add_line(l)
    return l

def main():

    filepath = 'sample_data/shelby_cornati.gpx'
    print('Opening file '+filepath)
    gpx_file = open(filepath, 'r')
    print('parsing file...')
    gpx_parser = parser.GPXParser(gpx_file)
    gpx = gpx_parser.parse()
    gpx_file.close()

    # find bounds
    print('getting bounds ...')
    min_lon = min_lat = 90
    max_lon = max_lat = -90
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lon, lat = point.latitude, point.longitude
                min_lon = min([lon, min_lon])
                min_lat = min([lat, min_lat])
                max_lon = max([lon, max_lon])
                max_lat = max([lat, max_lat])

    bounds = [min_lat, max_lat, min_lon, max_lon]
    print(str(bounds))

    # Create a Stamen Terrain instance.
    print('downloading base map tiles')
    stamen_terrain = cimgt.StamenTerrain()
    #stamen_terrain = cimgt.GoogleTiles()

    print('creating map')
    # Create a GeoAxes in the tile's projection.
    ax = plt.axes(projection=stamen_terrain.crs)

    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent([min_lat, max_lat, min_lon , max_lon])


    # Add the Stamen data at zoom level 8.
    ax.add_image(stamen_terrain, 12)

    # Add a marker for the Eyjafjallajökull volcano.
    # plt.plot(-19.613333, 63.62, marker='o', color='red', markersize=12, alpha=0.7, transform=ccrs.Geodetic())

    # Use the cartopy interface to create a matplotlib transform object
    # for the Geodetic coordinate system. We will use this along with
    # matplotlib's offset_copy function to define a coordinate system which
    # translates the text by 25 pixels to the left.
    #geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    #text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # Add text 25 pixels to the left of the volcano.
    # plt.text(-19.613333, 63.62, u'Eyjafjallajökull',
    #         verticalalignment='center', horizontalalignment='right',
    #         transform=text_transform,
    #         bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round'))

    for track in gpx.tracks:
        for segment in track.segments:
            lons = [p.longitude for p in segment.points]
            lats = [p.latitude for p in segment.points]
            track = sgeom.LineString(zip(lons, lats))
            ax.add_geometries([track], ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor='black')

    plt.show()


if __name__ == '__main__':
    main()
