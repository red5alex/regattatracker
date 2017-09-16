import datetime

import math


def calculate_initial_compass_bearing(point_a, point_b):
    if (type(point_a) != tuple) or (type(point_b) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])

    difflong = math.radians(point_b[1] - point_a[1])

    x = math.sin(difflong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) * math.cos(difflong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180deg to + 180deg which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


class ShipTrack:
    def __init__(self, gpx_track):
        self.min_lon = self.min_lat = 90
        self.max_lon = self.max_lat = -90
        self.min_time = datetime.datetime(year=3000, month=1, day=1)
        self.max_time = datetime.datetime(year=1, month=1, day=1)
        self.gpx_track = gpx_track
        self.verts = []
        self.info = []
        for segment in self.gpx_track.segments:
            last_p = None
            for p in segment.points:
                # store vertex position
                lon, lat, time = p.longitude, p.latitude, p.time
                self.verts.append((lon, lat, time))

                # store additional vertex info
                if last_p is None:
                    speed = 0
                    course = 0
                else:
                    speed = p.speed_between(last_p)
                    course = calculate_initial_compass_bearing((last_p.latitude, last_p.longitude),
                                                               (p.latitude, p.longitude))
                self.info.append((course, speed))
                last_p = p

                # get bounding box
                self.min_lon = min([lon, self.min_lon])
                self.max_lon = max([lon, self.max_lon])
                self.min_lat = min([lat, self.min_lat])
                self.max_lat = max([lat, self.max_lat])
                self.min_time = min([time, self.min_time])
                self.max_time = max([time, self.max_time])

    def lons(self, max_time):
        return [v[0] for v in self.verts if v[2] < max_time]

    def lats(self, max_time):
        return [v[1] for v in self.verts if v[2] < max_time]

    def last_position_at_time(self, time, increment=0):
        return [v for v in self.verts if v[2] < time][-1 - increment]

    def last_info_at_time(self, time):
        index = len([v for v in self.verts if v[2] < time]) - 1
        return self.info[index]

    def __del__(self):
        pass
