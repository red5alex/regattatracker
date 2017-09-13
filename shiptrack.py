import datetime

class shiptrack:
    def __init__(self, gpx_track):
        self.min_lon = self.min_lat = 90
        self.max_lon = self.max_lat = -90
        self.min_time = datetime.datetime(year=3000, month=1, day=1)
        self.max_time = datetime.datetime(year=1, month=1, day=1)
        self.gpx_track = gpx_track
        self.verts = []
        for segment in self.gpx_track.segments:
            for point in segment.points:
                lon, lat, time = point.longitude, point.latitude, point.time
                self.verts.append((lon, lat, time))
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

    def __del__(self):
        pass

