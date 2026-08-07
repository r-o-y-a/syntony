import sys
from math import *
from itertools import combinations
from datetime import datetime, timezone


# this code calculates planetary relationships for
# natal chart, natal<->present, and present 
# and returns the harmonics associated with 
# the astrological aspects present in them


# inputs to calculate birth chart
year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])
hour = int(sys.argv[4])
minute = int(sys.argv[5])
utc_offset = float(sys.argv[6])

# tolerance for deviation from an aspect
orb = 2

# angle & harmonic values from https://en.wikipedia.org/wiki/Astrological_aspect
aspects = {
    "conjunction":   (0.00,   1),
    "opposition":    (180.00, 2),

    "square":        (90.00,  4),
    "octile":        (45.00,  8),
    "trioctile":     (135.00, 8),
    "sexdecile":     (22.50, 16),
    "sesquioctile":  (67.50, 16),
    "quinsemioctile":(112.50,16),
    "sepsemioctile": (157.50,16),

    "trine":         (120.00, 3),
    "sextile":       (60.00,  6),
    "duodecile":     (30.00, 12),
    "quincunx":      (150.00,12),

    "quattuorvigintile": (15.00,24),
    "squile":            (75.00,24),
    "squine":            (105.00,24),
    "quindecile24":      (165.00,24),

    "quintile":      (72.00,  5),
    "biquintile":    (144.00, 5),
    "decile":        (36.00, 10),
    "tridecile":     (108.00,10),
    "quindecile15":  (24.00, 15),
    "biquindecile":  (48.00, 15),
    "quadraquindecile": (96.00,15),
    "sepquindecile": (168.00,15),

    "vigintile":     (18.00,20),
    "trivigintile":  (54.00,20),
    "sepvigintile":  (126.00,20),
    "nonvigintile":  (162.00,20),

    "quadragintile": (9.00,40),

    "septile":       (51.43, 7),
    "biseptile":     (102.86,7),
    "triseptile":    (154.29,7),
    "semiseptile":   (25.71,14),
    "tresemiseptile":(77.14,14),
    "quinsemiseptile":(128.57,14),

    "novile":        (40.00, 9),
    "binovile":      (80.00, 9),
    "quadranovile":  (160.00,9),
    "octodecile":    (20.00,18),
    "trigintasextile": (10.00,36),

    "undecile":      (32.83,11),
    "biundecile":    (65.45,11),
    "triundecile":   (98.18,11),
    "quadundecile":  (130.91,11),
    "quinundecile":  (163.63,11)
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


# calculate planet position in cartesian space
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



def calculate_relationships(chart1, chart2=None):

    relationships = []

    if chart2 is None:

        pairs = (
            (
                chart1[a],
                chart1[b]
            )
            for a, b in combinations(chart1, 2)
        )

    else:

        pairs = (
            (
                chart2[transit_planet],
                chart1[natal_planet]
            )
            for transit_planet in chart2
            for natal_planet in chart1
        )

    for p1, p2 in pairs:

        angle = (
            p2 - p1
        ) % 360

        distance = min(
            angle,
            360 - angle
        )

        for name, (target, harmonic) in aspects.items():

            offset = min(
                abs(distance - target),
                360 - abs(distance - target)
            )

            if offset <= orb:

                if name == "quindecile24" or name == "quindecile15":
                    name = "quindecile"

                relationships.append([
                    name,
                    harmonic,
                    round(offset, 2),
                    round(distance, 2)
                ])

                break

    return relationships


birth_relationships = calculate_relationships(
    birth_chart
)

transit_relationships = calculate_relationships(
    birth_chart,
    transit_chart
)

current_relationships = calculate_relationships(
    transit_chart
)

print([
    birth_relationships,
    transit_relationships,
    current_relationships
])