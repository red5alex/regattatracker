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
    print('Parsing file ' + filepath)
    gpx_file = open(filepath, 'r')
    gpx_parser = parser.GPXParser(gpx_file)
    gpx = gpx_parser.parse()
    gpx_file.close()

    # load tracks
    tracks = []
    for vertices in gpx.tracks:
        tracks.append(shiptrack(vertices))
    return tracks

def load_climatedata():
    pass


def load_basemapdata():
    pass


def render_map(time_current, track):

    # Get Stamen Terrain base map.
    stamen_terrain = cimgt.StamenTerrain()

    # set up axes
    ax = plt.axes(projection=stamen_terrain.crs)  # Create a GeoAxes in the tile's projection.
    ax.set_extent([track.min_lon, track.max_lon, track.min_lat, track.max_lat])  # Limit  extent to track bounding box.
    ax.add_image(stamen_terrain, 12)  # Add the Stamen data at zoom level 8.

    # Use the cartopy interface to create a matplotlib transform object
    # for the Geodetic coordinate system. We will use this along with
    # matplotlib's offset_copy function to define a coordinate system which
    # translates the text by 25 pixels to the left.
    # geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    # text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # Add Title, Legend, Time indicator
    plt.title(time_current.strftime("%Y-%m-%d"))

    legend_artists = [Line([0], [0], color=color, linewidth=1) for color in ('blue', 'red', 'green')]
    legend_texts = ['S/Y Shelby', 'S/Y Elixir', 'S/Y Alinghi']
    legend = plt.legend(legend_artists, legend_texts, fancybox=True, loc='lower left', framealpha=0.75)
    legend.legendPatch.set_facecolor('none')

    plt.annotate(str(time_current.strftime("%H:%M UTM")), xy=(0.5, 0.05), xycoords='axes fraction')

    # Add ship track
    vertices = sgeom.LineString(zip(track.lons(max_time=time_current), track.lats(max_time=time_current)))
    ax.add_geometries([vertices], ccrs.PlateCarree(), facecolor='none', edgecolor='blue')

    # Add a marker for the ships last location
    last_pos = track.last_position_at_time(time_current)
    plt.plot(last_pos[0], last_pos[1], marker='o', color='blue', markersize=4, alpha=1, transform=ccrs.Geodetic())

    # finalize
    plt.show()

def render_frame(i):
    pass

def render_movie():
    pass


def main():
    # load gpx file
    filepath = 'sample_data/shelby_cornati.gpx'
    tracks = load_tracks(filepath)

    # TODO: support for multiple tracks
    track = tracks[0]
    # TODO: support moving time cursor
    time_current = track.min_time + (track.max_time - track.min_time) / 2

    render_map(time_current, track)




if __name__ == '__main__':
    main()
