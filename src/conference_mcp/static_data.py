"""Static data for all supported conferences.

Venue, hotels, co-located events, and schedule overviews are defined here.
Live session data is fetched from upstream iCal / Sessionize feeds at runtime.
"""

from __future__ import annotations

from conference_mcp.models import ColocatedEvent, Hotel, VenueInfo

# =========================================================================
# KubeCon + CloudNativeCon Europe 2026
# =========================================================================

KUBECON_VENUE = VenueInfo(
    name="RAI Amsterdam",
    address="Europaplein 24, 1078 GZ Amsterdam, Netherlands",
    description=(
        "RAI Amsterdam is the venue for KubeCon + CloudNativeCon Europe 2026. "
        "It has its own train station (Amsterdam RAI) and is easily accessible "
        "by tram, bus, metro, and bicycle. The venue sources 100% green electricity."
    ),
    rooms=[
        "Hall 12 (Keynotes)",
        "Halls 1-5 (Solutions Showcase / Expo)",
        "Hall 7 | Room A",
        "Hall 7 | Room B",
        "Hall 7 | Room C",
        "Hall 8 | Room D",
        "Hall 8 | Room E",
        "Hall 8 | Room F",
        "Hall 8 | Room G",
        "Auditorium",
        "Elicium 1",
        "Elicium 2",
        "Forum (Ground Floor)",
        "E103-105 (1st Floor)",
        "E106-108",
        "Amtrium 1+2",
        "G102-103",
        "G104-105 (Community Hub)",
        "G106",
        "G107",
        "Emerald Room",
        "F002-005",
    ],
    transit={
        "closest_station": "Amsterdam RAI Station (train, bus, tram, metro)",
        "from_airport": "Amsterdam Schiphol (AMS) — 14.4 km, ~15 min drive, ~10 min by train",
        "public_transport": "GVB tram/bus/metro — buy an Amsterdam Travel Ticket for unlimited rides",
        "gvb_app": "https://www.gvb.nl/en/travel-information/gvb-app",
        "rai_directions": "https://www.rai.nl/en/route",
    },
    parking="€5.50/hour, max €35/day. Online day tickets: €29/day at https://parkeren.rai.nl/en/booking/period.html",
    maps={
        "venue_map": "https://events.linuxfoundation.org/wp-content/uploads/2026/03/KCEU26-VenueMap.pdf",
        "expo_map": "https://events.linuxfoundation.org/wp-content/uploads/2026/03/KCEU26-ExpoMap.pdf",
        "rai_floorplan": "https://www.rai.nl/en/calendar/kubecon-cloudnativecon-europe-2026",
    },
)

KUBECON_HOTELS: list[Hotel] = [
    Hotel(
        name="nhow Amsterdam RAI",
        address="Europaboulevard 2b, 1078 RV Amsterdam",
        distance_to_venue="350m walk / 500m drive",
        rate_from="€313.63/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.nh-hotels.com/en/hotel/nhow-amsterdam-rai",
        availability="Room Block Closed",
    ),
    Hotel(
        name="NH Collection Amsterdam Flower Market",
        address="Vijzelstraat 4, 1017 HK Amsterdam",
        distance_to_venue="3.6 km walk / 6.1 km drive",
        rate_from="€284.77/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.nh-hotels.com/en/hotel/nh-collection-amsterdam-flower-market",
        availability="Room Block Closed",
    ),
    Hotel(
        name="Avani Museum Quarter",
        address="Hobbemakade 50, Amsterdam 1071 XL",
        distance_to_venue="2.2 km walk / 2.1 km drive",
        rate_from="€262.90/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.avanihotels.com/en/museum-quarter-amsterdam",
        availability="Room Block Closed",
    ),
    Hotel(
        name="NH Amsterdam Zuid",
        address="Van Leijenberghlaan 221, 1082 GG Amsterdam",
        distance_to_venue="2.2 km walk / 2.4 km drive",
        rate_from="€236.48/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.nh-hotels.com/en/hotel/nh-amsterdam-zuid",
        availability="Room Block Closed",
    ),
    Hotel(
        name="INNSiDE by Melia",
        address="Eduard van Beinumstraat 40, 1077 XZ Amsterdam",
        distance_to_venue="1.7 km walk / 2.6 km drive",
        rate_from="€318.15/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.melia.com/en/hotels/netherlands/amsterdam/innside-amsterdam",
        availability="Room Block Closed",
    ),
    Hotel(
        name="citizenM Amsterdam South",
        address="Pr. Irenestraat 30, 1077 WX Amsterdam",
        distance_to_venue="1.3 km walk / 2.3 km drive",
        rate_from="€291.38/night (incl. breakfast)",
        rating="4 stars",
        url="https://www.citizenm.com/hotels/europe/amsterdam/south-hotel",
        availability="Room Block Closed",
    ),
    Hotel(
        name="Apollo Hotel Amsterdam",
        address="Apollolaan 2, 1077 BA Amsterdam",
        distance_to_venue="1.5 km walk / 1.7 km drive",
        rate_from="€329/night",
        rating="4 stars",
        url="https://www.marriott.com/en-us/hotels/amspo-apollo-hotel-amsterdam",
        availability="Sold Out",
        breakfast_included=False,
    ),
]

KUBECON_COLOCATED_EVENTS: list[ColocatedEvent] = [
    ColocatedEvent(
        name="Agentics Day: MCP + Agents",
        duration="Half-Day (afternoon)",
        location="Hall 7 | Room A",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/agentics-day-mcp-agents/",
        description="Co-located event focused on Model Context Protocol and AI agents in cloud-native.",
    ),
    ColocatedEvent(
        name="ArgoCon",
        duration="Full-Day",
        location="Auditorium (Track 1) + G102-103 (Track 2)",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/argocon/",
    ),
    ColocatedEvent(
        name="BackstageCon",
        duration="Full-Day",
        location="Hall 8 | Room E",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/backstagecon/",
    ),
    ColocatedEvent(
        name="CiliumCon",
        duration="Half-Day (afternoon)",
        location="Elicium 1",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/ciliumcon/",
    ),
    ColocatedEvent(
        name="Cloud Native AI + Kubeflow Day",
        duration="Full-Day",
        location="Hall 7 | Room B (Track 1) + Room C (Track 2)",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/cloud-native-ai-kubeflow-day/",
    ),
    ColocatedEvent(
        name="Cloud Native Telco Day",
        duration="Full-Day",
        location="G104-105",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/cloud-native-telco-day/",
    ),
    ColocatedEvent(
        name="FluxCon",
        duration="Half-Day (morning)",
        location="Elicium 1",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/fluxcon/",
    ),
    ColocatedEvent(
        name="KeycloakCon",
        duration="Half-Day (morning)",
        location="Hall 7 | Room A",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/keycloakcon/",
    ),
    ColocatedEvent(
        name="Kubernetes on Edge Day",
        duration="Half-Day (morning)",
        location="Emerald Room",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/kubernetes-on-edge-day/",
    ),
    ColocatedEvent(
        name="KyvernoCon",
        duration="Half-Day (afternoon)",
        location="E106-108",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/kyvernocon/",
    ),
    ColocatedEvent(
        name="Observability Day",
        duration="Full-Day",
        location="Forum (Ground Floor; Track 1) + E103-105 (1st Floor; Track 2)",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/observability-day/",
    ),
    ColocatedEvent(
        name="Open Source SecurityCon",
        duration="Full-Day",
        location="Hall 8 | Room D",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/open-source-securitycon/",
    ),
    ColocatedEvent(
        name="Open Sovereign Cloud Day",
        duration="Half-Day (afternoon)",
        location="F002-005",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/open-sovereign-cloud-day/",
    ),
    ColocatedEvent(
        name="OpenTofu Day",
        duration="Half-Day (afternoon)",
        location="Emerald Room",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/opentofu-day/",
    ),
    ColocatedEvent(
        name="Platform Engineering Day",
        duration="Full-Day",
        location="Hall 8 | Room F (Track 1) + Room G (Track 2)",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/platform-engineering-day/",
    ),
    ColocatedEvent(
        name="WasmCon",
        duration="Half-Day (morning)",
        location="E106-108",
        requires="ALL ACCESS PASS",
        url="https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/co-located-events/wasmcon/",
    ),
]

KUBECON_SCHEDULE_OVERVIEW = {
    "event": "KubeCon + CloudNativeCon Europe 2026",
    "dates": "23-26 March 2026",
    "location": "RAI Amsterdam, Netherlands",
    "timezone": "CET (Central European Time, UTC+1)",
    "hashtags": ["#KubeCon", "#CloudNativeCon"],
    "schedule_at_a_glance": {
        "monday": "Pre-event Programming: Co-Located Events (ArgoCon, CiliumCon, Agentics Day, Platform Engineering Day, etc.)",
        "tuesday": "Keynotes (Hall 12), Breakout Sessions, Solutions Showcase (Halls 1-5), KubeCrawl + CloudNativeFest (5:30-7PM)",
        "wednesday": "Keynotes, Breakout Sessions, Solutions Showcase",
        "thursday": "Keynotes, Breakout Sessions, Solutions Showcase",
    },
    "useful_links": {
        "schedule": "https://kccnceu2026.sched.com/",
        "colocated_schedule": "https://colocatedeventseu2026.sched.com/",
        "registration": "https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/register/",
        "venue": "https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/attend/venue-travel/",
        "code_of_conduct": "https://events.linuxfoundation.org/kubecon-cloudnativecon-europe/attend/code-of-conduct/",
        "youtube_recordings": "https://www.youtube.com/@cncf/playlists",
    },
}

KUBECON_AIRLINE_DISCOUNTS = [
    {
        "airline": "United Airlines",
        "code": "ZRQ5172168",
        "booking_url": "https://www.united.com/en/us/book-flight/united-reservations?txtPromoCode=ZRQ5172168",
        "valid_dates": "13 March - 3 April 2026",
        "phone": "1-800-426-1122 (Mon-Fri, no booking fee)",
    },
    {
        "airline": "Delta Air Lines",
        "code": "NY49D",
        "booking_url": "https://www.delta.com/flightsearch/book-a-flight?meetingEventCode=NY49D",
        "valid_dates": "11 March - 3 April 2026",
        "phone": "1-800-328-1111 (Mon-Fri 8am-6:30pm EST, no booking fee)",
    },
]

# =========================================================================
# ContainerDays Hamburg 2026
# =========================================================================

CDS_VENUE = VenueInfo(
    name="MS Bleichen",
    address="Hamburg, Germany",
    description=(
        "ContainerDays Hamburg 2026 takes place aboard the MS Bleichen, "
        "a permanently moored event ship in Hamburg's harbor. The venue features "
        "6 tracks across multiple decks and offers a unique waterfront conference experience. "
        "AIContext runs as a co-located track alongside the main ContainerDays program."
    ),
    rooms=[
        "Room 1: Main Track",
        "Room 2: Platform Engineering Track",
        "Room 3: Cloud Native Experience & Golang Track",
        "Room 4: Security Track",
        "MS Bleichen: Mixed Track",
        "Room 5: AIContext Track",
    ],
    transit={
        "closest_station": "Hamburg S-Bahn / U-Bahn (various stations, see venue site)",
        "from_airport": "Hamburg Airport (HAM) — ~25 min by S-Bahn to city center",
        "public_transport": "HVV S-Bahn, U-Bahn, and bus network — tickets via hvv app",
        "hvv_app": "https://www.hvv.de/en",
        "venue_directions": "https://www.containerdays.io/containerdays-hamburg-2026/location/",
    },
    parking="Check venue website for parking availability",
    maps={
        "venue_page": "https://www.containerdays.io/containerdays-hamburg-2026/location/",
        "official_site": "https://www.containerdays.io/containerdays-hamburg-2026/",
    },
)

CDS_HOTELS: list[Hotel] = [
    Hotel(
        name="Near Hamburg HafenCity / City Center",
        address="Check booking.com or hotels.com for current rates",
        distance_to_venue="Varies — use venue page for best areas",
        rate_from="Varies",
        rating="Varies",
        url="https://www.containerdays.io/containerdays-hamburg-2026/location/",
        availability="Check availability",
    ),
]

CDS_WORKSHOPS: list[ColocatedEvent] = [
    ColocatedEvent(
        name="ContainerDays Main Conference",
        duration="Multi-Day",
        location="MS Bleichen (all tracks)",
        requires="CONFERENCE PASS",
        url="https://www.containerdays.io/containerdays-hamburg-2026/tickets/",
        description="Three days of talks across 6 tracks: Main, Platform Engineering, Cloud Native & Golang, Security, Mixed, and AIContext.",
    ),
    ColocatedEvent(
        name="AIContext Track",
        duration="Multi-Day",
        location="Room 5: AIContext Track",
        requires="CONFERENCE PASS",
        url="https://www.containerdays.io/containerdays-hamburg-2026/agenda/",
        description="Dedicated AI track running alongside ContainerDays covering AI agents, MCP, LLMs, and ML infrastructure.",
    ),
]

CDS_SCHEDULE_OVERVIEW = {
    "event": "ContainerDays Hamburg 2026",
    "dates": "September 2-4, 2026",
    "location": "MS Bleichen, Hamburg, Germany",
    "timezone": "CEST (Central European Summer Time, UTC+2)",
    "hashtags": ["#ContainerDays", "#CDS2026", "#AIContext"],
    "schedule_at_a_glance": {
        "wednesday": "Registration (8:30 AM), Opening Remarks, Sessions across 6 tracks, Kelsey Hightower Keynote (1:30 PM), Evening Event (6:05 PM)",
        "thursday": "Sessions across 6 tracks, Panel discussions, Exhibition Networking (4:10 PM)",
        "friday": "Sessions across 6 tracks, Coffee Breaks, Exhibition Networking — conference closes ~2 PM",
    },
    "useful_links": {
        "schedule": "https://www.containerdays.io/containerdays-hamburg-2026/agenda/",
        "registration": "https://www.containerdays.io/containerdays-hamburg-2026/tickets/",
        "speakers": "https://www.containerdays.io/containerdays-hamburg-2026/speakers/",
        "venue": "https://www.containerdays.io/containerdays-hamburg-2026/location/",
        "partners": "https://www.containerdays.io/containerdays-hamburg-2026/partners/",
        "code_of_conduct": "https://www.containerdays.io/code-of-conduct/",
    },
}
