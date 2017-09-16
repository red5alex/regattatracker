# -*- coding: utf-8 -*-
import os
from moviepy.video.io.bindings import mplfig_to_npimage
import moviepy.editor as mpy
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.lines import Line2D as Line
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import shapely.geometry as sgeom
import gpxpy.parser as parser
from cached_tiler import CachedTiler
from shiptrack import ShipTrack


def newline(p1, p2):
    ax = plt.gca()
    xmin, xmax = ax.get_xbound()

    if p2[0] == p1[0]:
        xmin = xmax = p1[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = p1[1] + (p2[1] - p1[1]) / (p2[0] - p1[0]) * (xmax - p1[0])
        ymin = p1[1] + (p2[1] - p1[1]) / (p2[0] - p1[0]) * (xmin - p1[0])

    l = mlines.Line2D([xmin, xmax], [ymin, ymax])
    ax.add_line(l)
    return l


def load_tracks(ship):
    filepath = ship[0]
    print('Parsing file ' + filepath)
    gpx_file = open(filepath, 'r')
    gpx_parser = parser.GPXParser(gpx_file)
    gpx = gpx_parser.parse()
    gpx_file.close()

    # load tracks
    tracks = []
    for vertices in gpx.tracks:
        tracks.append(ShipTrack(vertices, {"name": ship[1], "color": ship[2]}))
    return tracks


def load_climatedata():
    pass


def render_map(time_current, ships, margin, plot=False):
    # Get Stamen Terrain base map.
    stamen_terrain = CachedTiler(cimgt.StamenTerrain())

    min_lon = min([s[0].min_lon for s in ships])
    max_lon = max([s[0].max_lon for s in ships])
    min_lat = min([s[0].min_lat for s in ships])
    max_lat = max([s[0].max_lat for s in ships])

    d_lon = max_lon - min_lon
    d_lat = max_lat - min_lat

    # stop_time = max([st[0].max_time for st in ship_tracks])

    # set up axes
    fig = plt.figure()
    fig.set_size_inches(20, 10)
    ax = plt.axes(projection=stamen_terrain.crs)  # Create a GeoAxes in the tile's projection.
    ax.set_extent([min_lon - margin * d_lon,
                   max_lon + margin * d_lon,
                   min_lat - margin * d_lat,
                   max_lat + margin * d_lat])  # Limit  extent to track bounding box.
    ax.add_image(stamen_terrain, 12)  # Add the Stamen data at zoom level 8.

    # Use the cartopy interface to create a matplotlib transform object
    # for the Geodetic coordinate system. We will use this along with
    # matplotlib's offset_copy function to define a coordinate system which
    # translates the text by 25 pixels to the left.
    # geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    # text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # Add Title, Legend, Time indicator
    plt.title(time_current.strftime("%Y-%m-%d"))

    ship_names = [s[0].meta["name"] for s in ships]
    ship_colors = [s[0].meta["color"] for s in ships]

    legend_artists = [Line([0], [0], color=color, linewidth=1) for color in ship_colors]
    legend = plt.legend(legend_artists, ship_names, fancybox=True, loc='lower left', framealpha=0.75)
    legend.legendPatch.set_facecolor('none')

    plt.annotate(str(time_current.strftime("%H:%M UTM")), xy=(0.5, 0.05), xycoords='axes fraction')

    # Add ship tracks
    for ship in ships:
        vertices = sgeom.LineString(zip(ship[0].lons(max_time=time_current), ship[0].lats(max_time=time_current)))
        ax.add_geometries([vertices], ccrs.PlateCarree(), facecolor='none', edgecolor=ship[0].meta["color"])

        # Add a marker for the ships last location
        last_pos = ship[0].last_position_at_time(time_current)
        last_info = ship[0].last_info_at_time(time_current)
        plt.plot(last_pos[0], last_pos[1], marker=(3, 0, last_info[0]), color=ship[0].meta["color"], markersize=5,
                 alpha=1,
                 transform=ccrs.PlateCarree())

    # plt.annotate("Shelby: {:.1f} kts".format(last_info[1] * 1.94384), xy=(0.9, 0.05), xycoords='axes fraction')
    # plt.annotate("Elixir: {:.1f} kts".format(last_info[1] * 1.94384), xy=(0.9, 0.05), xycoords='axes fraction')

    # finalize
    if plot:
        plt.show()
    return fig


def render_movie(time_start, time_end, duration_secs, fps, ships, filename, margin):
    nframes = duration_secs * fps + 2
    dt = (time_end - time_start) / nframes
    times = [(time_start + i * dt) for i in range(1, nframes)]

    def render_frame(f):
        time = times[int(f * fps)]
        fig = render_map(time, ships, margin)
        return mplfig_to_npimage(fig)

    animation = mpy.VideoClip(render_frame, duration=duration_secs)
    animation.write_videofile(filename, fps=fps)


def main(ship_info, margin=0.05, showplot=True, export_movie_to=None, duration=30, fps=15):
    # load gpx file
    ships = []
    for ship in ship_info:
        print('loading file ' + ship[0])
        ships.append(load_tracks(ship))

    start_time = min([s[0].min_time for s in ships])
    stop_time = max([s[0].max_time for s in ships])

    # render movie
    if export_movie_to is not None:
        render_movie(start_time, stop_time, duration, fps, ships, export_movie_to, margin)

    # render map
    if showplot:
        render_map(stop_time, ships, margin, plot=True)


if __name__ == '__main__':
    # Script Parameters
    duration_sec = 45  # duration of the movie in seconds
    ship_info = [('sample_data/shelby_cornati.gpx', 'S/Y Shelby', 'blue'),
                 ('sample_data/elixir_cornati.gpx', 'S/Y Elixir', 'red')]
    filename = "kornati.mp4"

    # Script execution
    main(ship_info, duration=duration_sec, export_movie_to=filename)
