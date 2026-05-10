# Roads

The OSM road classification includes:

### Motorway

- Must be high-speed and of good road quality.
- Must have limited access at grade-separated interchanges.
- Characterized by a lack of intersection controls, such as traffic lights or stop signs.
- Typical speed between 80-120 mn/h.

### Trunk

- Important, high performance roads that aren't classified as highway=motorway.
- Directions of traffic are usually separated, but aren't always divided.
- Roads without too many major restrictions to drive on (usually may be used by any type of motorized vehicles).
- Speeds are usually greater than 40mph/60 km/h.
- Can have intersection controls (traffic lights, roundabouts).

### Primary

- Major roads linking between large towns or major routes.
- The most significant road classification below trunk/motorway that lack large interchanges, on-ramps, and exits.

### Secondary

- Not part of a major route but is important in connecting major routes.
- Oten connect mid-sized towns.
- In cities, they connect major arterial ways.
- Typically has 2 or more lanes with good/fair road quality.

### Tertiary

- The lowest level of arterial traffic flow.
- Low to moderate traffic flow.
- Accumulate traffic from minor road ways like residential and lead them to more major roads.
- Frequently used within urban areas for established bus routes
- Usually have commercial establishments on either sides of the road.

### Unclassifed

- Roadways with public access that are non-residential. 
- Main roads within an industrial area.
- Typically long and continuous unless going through a settlement.

### Residential

- Typically have lower speed limits.
- Can be longer, continuous roads.
- Should be anchored (connected on one or both ends) to a road of the same or higher class.
- May include access to non-residential features like shops.

### Living street

- Roads with VERY LOW speed limits and other mostly pedestrian friendly traffic rules.
- Living streets give the right of way or equal rights to pedestrians over other road users.
- Not to be a part of through traffic for routing purposes.

### Service (excluded)

- Generally used to grant access to certain areas, such as schools, malls, industrial buildings, etc.
- Will almost never be a long, continuous road.

### Track (excluded)

- Most often unpaved, rural roads.
- Can have a dead end.

### Pedestrian (excluded)

- Pedestrian roads are mainly or exclusively for pedestrians but some vehicles may be authorized (buses, emergency, taxis, deliveries, etc.).
- Often found in shopping areas, town centers, places with tourist attractions, and recreation areas.
- Can also be found in residential communities designed to be navigated primarily by foot.
- For more information about pedestrian streets and other pedestrian features see the pedestrian doc (link).

### Footway (excluded)

- Typically exclusively for foot traffic.
- Generally found only within urban settings.
- Usually seen as sidewalks or minor pathways designated solely for pedestrians.
- Under specific circumstances, these may be used in combination with bicycles.
- Surface type may vary, but usually are paved with some material.

### Cicleway (excluded)

- A separate way designated for cyclists.

### Path (excluded)

- A generic path used by pedestrians, small vehicles, and/or animals.
- Generally found only within rural settings.
- Could be seen as walking and hiking trails, bike paths, horse and stock trails, or mountain bike trails, etc.
- Surface types may vary, but usually are natural to the area (unpaved).

Note: Motorway is the only international standard classification, all other road classes are relative to the country/region.

## Assumption

category_attributes = {
    'motorway': {'width': 30, 'maxspeed': 120},
    'trunk': {'width': 15, 'maxspeed': 100},
    'primary': {'width': 12, 'maxspeed': 90},
    'secondary': {'width': 10, 'maxspeed': 50},
    'tertiary': {'width': 8, 'maxspeed': 50},
    'residential': {'width': 7, 'maxspeed': 30},
    'living_street': {'width': 6, 'maxspeed': 20},
    'busway': {'width': 8, 'maxspeed': 50},
    'unclassified': {'width': 8, 'maxspeed': 30}
}