# -*- coding: utf-8 -*-

import datetime

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.lines import Line2D as Line
from matplotlib.transforms import offset_copy
from matplotlib.path import Path
import matplotlib.patches as patches

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.io.shapereader as shpreader

import shapely.geometry as sgeom

import gpxpy.parser as parser

from shiptrack import shiptrack

def newline(p1, p2):
    ax = plt.gca()
    xmin, xmax = ax.get_xbound()

    if (p2[0] == p1[0]):
        xmin = xmax = p1[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = p1[1] + (p2[1] - p1[1]) / (p2[0] - p1[0]) * (xmax - p1[0])
        ymin = p1[1] + (p2[1] - p1[1]) / (p2[0] - p1[0]) * (xmin - p1[0])

    l = mlines.Line2D([xmin, xmax], [ymin, ymax])
    ax.add_line(l)
    return l


def load_tracks(filepath):
    pass


def load_climatedata():
    pass


def load_basemapdata():
    pass


def render_map():
    pass


def main():
    # load gpx file
    filepath = 'sample_data/shelby_cornati.gpx'
    print('Parsing file ' + filepath)
    gpx_file = open(filepath, 'r')
    gpx_parser = parser.GPXParser(gpx_file)
    gpx = gpx_parser.parse()
    gpx_file.close()

    # load tracks
    tracks = []
    for vertices in gpx.tracks:
        tracks.append(shiptrack(vertices))

    # TODO: support for multiple tracks
    track = tracks[0]

    # Create a Stamen Terrain instance.
    print('downloading base map tiles')
    stamen_terrain = cimgt.StamenTerrain()
    print('creating map')

    # Create a GeoAxes in the tile's projection.
    ax = plt.axes(projection=stamen_terrain.crs)

    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent([track.min_lon, track.max_lon, track.min_lat, track.max_lat])

    # Add the Stamen data at zoom level 8.
    ax.add_image(stamen_terrain, 12)

    # Add a marker for the Eyjafjallajökull volcano.
    # plt.plot(-19.613333, 63.62, marker='o', color='red', markersize=12, alpha=0.7, transform=ccrs.Geodetic())

    # Use the cartopy interface to create a matplotlib transform object
    # for the Geodetic coordinate system. We will use this along with
    # matplotlib's offset_copy function to define a coordinate system which
    # translates the text by 25 pixels to the left.
    # geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    # text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # Add text 25 pixels to the left of the volcano.
    # plt.text(-19.613333, 63.62, u'Eyjafjallajökull',
    #         verticalalignment='center', horizontalalignment='right',
    #         transform=text_transform,
    #         bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round'))

    # TODO: support moving time cursor
    time_current = track.min_time + (track.max_time - track.min_time) / 2

    # add annotations to map
    plt.title(time_current.strftime("%Y-%m-%d"))
    plt.annotate(str(time_current.strftime("%H:%M UTM")), xy=(0.5, 0.05), xycoords='axes fraction')

    vertices = sgeom.LineString(zip(track.lons(max_time=time_current),
                                    track.lats(max_time=time_current)))
    ax.add_geometries([vertices], ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='black')

    legend_artists = [Line([0], [0], color=color, linewidth=1)
                      for color in ('black')]
    legend_texts = ['S/Y Shelby']
    legend = plt.legend(legend_artists, legend_texts, fancybox=True,
                        loc='lower left', framealpha=0.75)
    legend.legendPatch.set_facecolor('none')

    plt.show()


if __name__ == '__main__':
    main()
