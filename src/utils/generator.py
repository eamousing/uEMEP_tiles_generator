import os
from pyproj import Proj
import textwrap
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def generate_empty_config():
    """
    Generate an empty configuration file with annotations
    """
    config = {
        "x_min": 0,
        "x_max": 0,
        "y_min": 0,
        "y_max": 0,
        "delta": 0,
        "tile_delta": 0,
        "output_dir": "./",
        "tile_name": "",
        "projection": "",
        "projection_attributes": [0, 0, 0, 0, 0]
    }

    annotations = {
        "x_min": "Minimum x coordinate",
        "x_max": "Maximum x coordinate",
        "y_min": "Minimum y coordinate",
        "y_max": "Maximum y coordinate",
        "delta": "Tile size in meters",
        "tile_delta": "Subgrid size in meters",
        "output_dir": "Output directory for tiles",
        "tile_name": "Tile name prefix",
        "projection": "Projection name (e.g., LAEA, RD)",
        "projection_attributes": "[lon_0, lat_0, false_easting, false_northing, earth_radius]"
    }

    with open("config.json", "w") as config_file:
        json.dump({"config": config, "annotations": annotations}, config_file, indent=4)

    print("Generated empty config file at config.json")

def generate_tiles(output_dir, tile_tag, tile_name, subgrid_delta, subgrid_min_x, subgrid_min_y, subgrid_max_x, subgrid_max_y):
    """
    Generate a tile file with the specified parameters.

    Args:
        output_dir (str): Directory where the tile file will be saved.
        tile_tag (int): Unique identifier for the tile.
        tile_name (str): Name prefix for the tile file.
        subgrid_delta (float): Size of the subgrid in meters.
        subgrid_min_x (float): Minimum x coordinate of the subgrid.
        subgrid_min_y (float): Minimum y coordinate of the subgrid.
        subgrid_max_x (float): Maximum x coordinate of the subgrid.
        subgrid_max_y (float): Maximum y coordinate of the subgrid.
    """

    # Create the content of the tile file
    content = textwrap.dedent(f"""
        tile_tag = {tile_tag:05d}
        subgrid_delta(x_dim_index) = {subgrid_delta:.2f}
        subgrid_delta(y_dim_index) = {subgrid_delta:.2f}
        subgrid_min(x_dim_index) = {subgrid_min_x:.2f}
        subgrid_min(y_dim_index) = {subgrid_min_y:.2f}
        subgrid_max(x_dim_index) = {subgrid_max_x:.2f}
        subgrid_max(y_dim_index) = {subgrid_max_y:.2f}
        """)
    # Create the filename for the tile file
    filename = os.path.join(output_dir, f"{tile_tag}_{tile_name}_{int(subgrid_delta)}.txt")

    # Write the content to the tile file
    with open(filename, "w") as file:
        file.write(content)

def generate_grid_tiles(config):
    """
    Generate grid tiles based on the provided configuration

    Args:
        config (dict): Configuration dictionary containing parameters for tile generation

    Returns:
        list: List of generated tiles with their coordinates
    """

    # Extract config
    x_min = config["x_min"]
    y_min = config["y_min"]
    x_max = config["x_max"]
    y_max = config["y_max"]
    delta = config["delta"]
    tile_delta = config["tile_delta"]
    projection = config["projection"]
    projection_attributes = config["projection_attributes"]

    # Define projection based on configuration
    if projection == "LAEA":
        proj = Proj(
            proj='laea', 
            lon_0=projection_attributes[0], 
            lat_0=projection_attributes[1],
            x_0=projection_attributes[2], 
            y_0=projection_attributes[3], 
            a=projection_attributes[4],
            units='m')
    elif projection == "RD":
        proj = Proj(
            proj='sterea',
            lon_0=projection_attributes[0],
            lat_0=projection_attributes[1],
            x_0=projection_attributes[2],
            y_0=projection_attributes[3],
            ellps=projection_attributes[4],
            units='m')
    else:
        raise ValueError(f"Unsupported projection: {projection}")

    # Convert input coordinates from lat/lon to the projection
    x_min_proj, y_min_proj = proj(x_min, y_min)
    x_max_proj, y_max_proj = proj(x_max, y_max)

    # Number of tiles in each dimension
    i_dim = int((x_max_proj - x_min_proj) // delta)
    j_dim = int((y_max_proj - y_min_proj) // delta)

    tiles = []
    k = 0

    # Loop to generate non-overlapping tiles
    for i in range(i_dim):
        for j in range(j_dim):
            k += 1
            xx_min = x_min_proj + i * delta
            yy_min = y_min_proj + j * delta
            xx_max = xx_min + delta
            yy_max = yy_min + delta
            tiles.append((k, xx_min, yy_min, xx_max, yy_max))

    return tiles

def write_tiles_to_files(tiles, config):
    """
    Write the generated tiles to files based on the provided configuration

    Args:
        tiles (list): List of generated tiles with their coordinates
        config (dict): Configuration dictionary containing parameters for tile generation
    """

    # Extract config
    tile_delta = config["tile_delta"]
    delta = config["delta"]
    output_dir = config["output_dir"]
    tile_name = config["tile_name"]

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Loop to write each tile to a file
    for tile in tiles:
        k, xx_min, yy_min, xx_max, yy_max = tile
        generate_tiles(output_dir, k, tile_name, tile_delta, xx_min, yy_min, xx_max, yy_max)

    print(f"Number of tiles = {len(tiles)}")
    print(f"Size of each tile = {delta / 1000} x {delta / 1000} km")

def plot_tiles(tiles, config):
    """
    Plot the generated tiles for visualization

    Args:
        tiles (list): List of generated tiles with their coordinates
        config (dict): Configuration dictionary containing parameters for tile generation
    """

    # Extract config
    projection = config["projection"]
    projection_attributes = config["projection_attributes"]
    output_dir = config["output_dir"]
    tile_name = config["tile_name"]
    subgrid_delta = config["tile_delta"]
    
    # Define the projection based on config
    if projection == "LAEA":
        map_proj = ccrs.LambertAzimuthalEqualArea(
            central_longitude=projection_attributes[0],
            central_latitude=projection_attributes[1],
            false_easting=projection_attributes[2],
            false_northing=projection_attributes[3]
        )
    elif projection == "RD":
        map_proj = ccrs.Stereographic(
            central_longitude=projection_attributes[0],
            central_latitude=projection_attributes[1],
            false_easting=projection_attributes[2],
            false_northing=projection_attributes[3]
        )
    else:
        raise ValueError(f"Unsupported projection: {projection}")

    # Create plot
    fig, ax = plt.subplots(
        figsize=(10, 10),
        subplot_kw={'projection': map_proj}
    )
    
    # Add map features
    ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
    ax.add_feature(cfeature.COASTLINE, zorder=0)
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.set_global()

    # Plot each tile as a rectangle
    for tile in tiles:
        k, xx_min, yy_min, xx_max, yy_max = tile
        rect = patches.Rectangle(
            (xx_min, yy_min),
            xx_max - xx_min,
            yy_max - yy_min,
            linewidth=1,
            edgecolor='blue',
            facecolor='none',
            transform=map_proj
        )
        ax.add_patch(rect)

        # Calculate the center of the rectangle for text placement
        center_x = (xx_min + xx_max) / 2
        center_y = (yy_min + yy_max) / 2

        # Add the tile number at the center of the tile
        ax.text(center_x, center_y, str(k), fontsize=10, ha='center', va='center', color='blue')
    
    # Set axis limits to zoom in on the area of interest
    buffer = 0.05
    x_min = min(tile[1] for tile in tiles) - buffer
    x_max = max(tile[3] for tile in tiles) + buffer
    y_min = min(tile[2] for tile in tiles) - buffer
    y_max = max(tile[4] for tile in tiles) + buffer
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Save the plot to a file
    filename = os.path.join(output_dir, f"map_{tile_name}_{int(subgrid_delta)}.png")
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved as {filename}")
