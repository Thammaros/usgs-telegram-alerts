import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from config import Config


def generate_cartopy_map(
    quake_lat,
    quake_lon,
    place,
    distance_km,
    output_path="quake_map.png",
):
    bangkok_lat, bangkok_lon = Config.BANGKOK_LAT, Config.BANGKOK_LON

    plt.figure(figsize=(12, 11), dpi=200)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.LAND.with_scale("10m"), facecolor="#f7f7f7")
    ax.add_feature(cfeature.OCEAN.with_scale("10m"), facecolor="#cde6f5")
    ax.add_feature(cfeature.BORDERS.with_scale("10m"), linestyle=":", linewidth=0.6)
    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.5)
    ax.add_feature(
        cfeature.LAKES.with_scale("10m"),
        facecolor="#b0d6f0",
        edgecolor="black",
        linewidth=0.4,
    )
    ax.add_feature(
        cfeature.RIVERS.with_scale("10m"), edgecolor="#4a90e2", linewidth=0.5
    )

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.4)
    gl.top_labels = gl.right_labels = False

    # Map extent
    center_lat = (quake_lat + bangkok_lat) / 2
    center_lon = (quake_lon + bangkok_lon) / 2

    # Calculate span in each direction
    lat_span = abs(quake_lat - bangkok_lat)
    lon_span = abs(quake_lon - bangkok_lon)

    min_span = max(distance_km / 111.0, 2.0)  # 1° ≈ 111 km
    max_span = max(lat_span, lon_span, min_span) + 2.0

    ax.set_extent(
        [
            center_lon - max_span,
            center_lon + max_span,
            center_lat - max_span,
            center_lat + max_span,
        ],
        crs=ccrs.PlateCarree(),
    )

    # Plot locations
    ax.plot(
        quake_lon,
        quake_lat,
        "ro",
        markersize=7,
        label="Epicenter",
        transform=ccrs.Geodetic(),
    )
    ax.plot(
        bangkok_lon,
        bangkok_lat,
        "go",
        markersize=7,
        label="Bangkok",
        transform=ccrs.Geodetic(),
    )

    # Connection line
    ax.plot(
        [quake_lon, bangkok_lon],
        [quake_lat, bangkok_lat],
        color="gray",
        linestyle="--",
        linewidth=1.2,
        transform=ccrs.Geodetic(),
    )

    # Labels
    if distance_km > 100:
        label_offset = min(max(distance_km / 1000.0, 0.1), 1.0)
        ax.text(
            quake_lon - label_offset,
            quake_lat + label_offset,
            place,
            fontsize=9,
            color="#e74c3c",
            weight="bold",
            transform=ccrs.Geodetic(),
        )
        ax.text(
            bangkok_lon - label_offset,
            bangkok_lat + label_offset,
            "Bangkok",
            fontsize=9,
            color="#27ae60",
            weight="bold",
            transform=ccrs.Geodetic(),
        )

        # Distance annotation at midpoint
        mid_lat = (quake_lat + bangkok_lat) / 2
        mid_lon = (quake_lon + bangkok_lon) / 2
        ax.text(
            mid_lon,
            mid_lat,
            f"{distance_km:.2f} km",
            fontsize=9,
            color="#34495e",
            weight="bold",
            transform=ccrs.Geodetic(),
            ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    # Title
    plt.title(
        "Earthquake Epicenter and Distance to Bangkok",
        fontsize=13,
        weight="bold",
        pad=20,
    )
    ax.legend(loc="lower left", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return output_path
