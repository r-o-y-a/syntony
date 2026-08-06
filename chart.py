import sys
from math import *
from itertools import combinations
from datetime import datetime, timezone


# this code calculates "aspects" in an astrological birth chart
# for compositional use. aspects occur when relationships 
# between planets have geometrically significant angles (0, 90, 180, etc)
# the calculation here uses a tolerance of ±8° (called orb)
# default intervals are assigned or can be sent from supercollider.

# aspects are calculated and returned for relationships relative to: 
# natal chart, natal<->present, and present 



# birth data from supercollider
year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])
hour = int(sys.argv[4])
minute = int(sys.argv[5])
utc_offset = float(sys.argv[6])


# aspect intervals
conjunction = float(sys.argv[7])  if len(sys.argv) > 7  else 1/1 # unison
sextile     = float(sys.argv[8])  if len(sys.argv) > 8  else 5/3 # major 6th
square      = float(sys.argv[9])  if len(sys.argv) > 9  else 3/2 # 5th
trine       = float(sys.argv[10]) if len(sys.argv) > 10 else 5/4 # major 3rd
opposition  = float(sys.argv[11]) if len(sys.argv) > 11 else 4/3 # 4th

aspects = {
    "conjunction": (0,   8, conjunction),
    "sextile":     (60,  6, sextile),
    "square":      (90,  8, square),
    "trine":       (120, 8, trine),
    "opposition":  (180, 8, opposition)
}


# julian date
def julian_date(y, m, d, h, minute, utc):
    if m <= 2:
        y -= 1
        m += 12

    a = floor(y / 100)
    b = 2 - a + floor(a / 4)
    t = (h - utc + minute / 60) / 24

    return (
        floor(365.25 * (y + 4716))
        + floor(30.6001 * (m + 1))
        + d + t + b - 1524.5
    )

birth_d = julian_date(
    year, month, day,
    hour, minute, utc_offset
) - 2451543.5


# current date for transits
now = datetime.now(timezone.utc)

transit_d = julian_date(
    now.year, now.month, now.day,
    now.hour, now.minute, 0
) - 2451543.5


# orbital elements for the given (julian) date:
    # N = longitude of ascending node
    # i = inclination of orbit
    # w = argument of perihelion
    # a = semi-major axis (approx. size of orbit)
    # e = eccentricity (how elliptical orbit is)
    # M = mean anomaly (where planet would be if it moved uniformly around its orbit)
def elements(name, d):
    return {
        "mercury": (48.3313+3.24587e-5*d, 7.0047+5e-8*d, 29.1241+1.01444e-5*d, .387098, 
.205635+5.59e-10*d, 168.6562+4.0923344368*d),
        "venus": (76.6799+2.46590e-5*d, 3.3946+2.75e-8*d, 54.8910+1.38374e-5*d, .723330, 
.006773-1.302e-9*d, 48.0052+1.6021302244*d),
        "mars": (49.5574+2.11081e-5*d, 1.8497-1.78e-8*d, 286.5016+2.92961e-5*d, 1.523688, 
.093405+2.516e-9*d, 18.6021+.5240207766*d),
        "jupiter": (100.4542+2.76854e-5*d, 1.3030-1.557e-7*d, 273.8777+1.64505e-5*d, 5.20256, 
.048498+4.469e-9*d, 19.8950+.0830853001*d),
        "saturn": (113.6634+2.38980e-5*d, 2.4886-1.081e-7*d, 339.3939+2.97661e-5*d, 9.55475, 
.055546-9.499e-9*d, 316.9670+.0334442282*d),
        "uranus": (74.0005+1.3978e-5*d, .7733+1.9e-8*d, 96.6612+3.0565e-5*d, 19.18171-1.55e-8*d, 
.047318+7.45e-9*d, 142.5905+.011725806*d),
        "neptune": (131.7806+3.0173e-5*d, 1.7700-2.55e-7*d, 272.8461-6.027e-6*d, 
30.05826+3.313e-8*d, .008606+2.15e-9*d, 260.2471+.005995147*d)
    }[name]


# calculate planet position in 3d space (x,y,z)
def position(name, d):
    N, i, w, a, e, M = elements(name, d)
    N, i, w, M = map(radians, (N, i, w, M % 360))

    # Kepler equation
    E = M + e*sin(M)*(1 + e*cos(M))

    for _ in range(5):
        E -= (E - e*sin(E) - M) / (1 - e*cos(E))

    xv = a*(cos(E)-e)
    yv = a*sqrt(1-e*e)*sin(E)

    v = atan2(yv, xv)
    r = hypot(xv, yv)

    return (
        r*(cos(N)*cos(v+w) - sin(N)*sin(v+w)*cos(i)),
        r*(sin(N)*cos(v+w) + cos(N)*sin(v+w)*cos(i)),
        r*sin(v+w)*sin(i)
    )


# sun
def sun_position(d):
    w = radians(282.9404 + 4.70935e-5*d)
    e = .016709 - 1.151e-9*d
    M = radians((356.0470 + .9856002585*d) % 360)

    E = M + e*sin(M)*(1 + e*cos(M))

    for _ in range(5):
        E -= (E - e*sin(E) - M) / (1 - e*cos(E))

    x = cos(E)-e
    y = sqrt(1-e*e)*sin(E)

    v = atan2(y, x)
    r = hypot(x, y)
    lon = v+w

    return r*cos(lon), r*sin(lon), degrees(lon) % 360


# moon
def moon_longitude(d):
    N = radians(125.1228 - .0529538083*d)
    i = radians(5.1454)
    w = radians(318.0634 + .1643573223*d)
    e = .0549
    M = radians((115.3654 + 13.0649929509*d) % 360)

    E = M + e*sin(M)*(1 + e*cos(M))

    for _ in range(5):
        E -= (E - e*sin(E) - M) / (1 - e*cos(E))

    xv = cos(E)-e
    yv = sqrt(1-e*e)*sin(E)

    v = atan2(yv, xv)

    x = cos(N)*cos(v+w) - sin(N)*sin(v+w)*cos(i)
    y = sin(N)*cos(v+w) + cos(N)*sin(v+w)*cos(i)

    return degrees(atan2(y, x)) % 360


# pluto - its orbit differs from the other planets
def pluto_position(d):
    P = radians(238.95 + .003968789*d)

    lon = (
        238.9508 + .00400703*d
        -19.799*sin(P) + 19.848*cos(P)
        +.897*sin(2*P) - 4.956*cos(2*P)
        +.610*sin(3*P) + 1.211*cos(3*P)
        -.341*sin(4*P) - .190*cos(4*P)
        +.128*sin(5*P) - .034*cos(5*P)
    )

    lat = (
        -3.9082
        -.011*sin(P) - 5.453*cos(P)
        +.220*sin(2*P) - 1.471*cos(2*P)
        -.536*sin(3*P) - .371*cos(3*P)
    )

    r = (
        40.72
        +6.68*sin(P) + 6.90*cos(P)
        -.18*sin(2*P) - .03*cos(2*P)
        +.20*sin(3*P) - .14*cos(3*P)
    )

    lon = radians(lon)
    lat = radians(lat)

    return (
        r*cos(lon)*cos(lat),
        r*sin(lon)*cos(lat),
        r*sin(lat)
    )


# chart
def calculate_chart(d):

    sx, sy, sun_lon = sun_position(d)

    chart = {"sun": sun_lon}

    for planet in [
        "mercury", "venus", "mars", "jupiter",
        "saturn", "uranus", "neptune"
    ]:
        x, y, z = position(planet, d)

        chart[planet] = degrees(
            atan2(y + sy, x + sx)
        ) % 360

    chart["moon"] = moon_longitude(d)

    px, py, pz = pluto_position(d)

    chart["pluto"] = degrees(
        atan2(py + sy, px + sx)
    ) % 360

    return chart


birth_chart = calculate_chart(birth_d)
transit_chart = calculate_chart(transit_d)




# relationships
#for a, b in combinations(birth_chart, 2):

#    angle = (birth_chart[b] - birth_chart[a]) % 360
#    distance = min(angle, 360-angle)
#    aspect = "-"

#    for name, (target, tolerance, ratio) in aspects.items():
#        if abs(distance-target) <= tolerance:
#            aspect = name
#            break

    # simple output for supercollider
#    print(a, b, round(angle, 2), aspect)



# calculate birth relationships and map aspects to intervals
intervals = []

for a, b in combinations(birth_chart, 2):

    angle = (
        birth_chart[b] - birth_chart[a]
    ) % 360

    distance = min(
        angle,
        360 - angle
    )

    for name, (target, tolerance, ratio) in aspects.items():

        if abs(distance - target) <= tolerance:

            intervals.append(ratio)

            break


# calculate transit-natal relationships and map aspects to intervals
transit_intervals = []

for transit_planet in transit_chart:

    for natal_planet in birth_chart:

        angle = (
            transit_chart[transit_planet] - birth_chart[natal_planet]
        ) % 360

        distance = min(
            angle,
            360 - angle
        )

        for name, (target, tolerance, ratio) in aspects.items():

            if abs(distance - target) <= tolerance:

                transit_intervals.append(ratio)

                break



# calculate current relationships and map aspects to intervals
current_intervals = []

for a, b in combinations(transit_chart, 2):

    angle = (
        transit_chart[b] - transit_chart[a]
    ) % 360

    distance = min(
        angle,
        360 - angle
    )

    for name, (target, tolerance, ratio) in aspects.items():

        if abs(distance - target) <= tolerance:

            current_intervals.append(ratio)

            break
        
# output only decimal interval arrays for SuperCollider
print([intervals, transit_intervals, current_intervals])