import os
import numpy as np
from pyproj import Proj
import textwrap
import json

def generate_empty_config():
    config = {
        "x_min": 0,
        "x_max": 0,
        "y_min": 0,
        "y_max": 0,
        "delta": 0,
        "tile_delta": 0,
        "output_dir": "./",
        "tile_name": "",
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
        "projection_attributes": "[lon_0, lat_0, false_easting, false_northing, earth_radius]"
    }

    with open("config.json", "w") as config_file:
        json.dump({"config": config, "annotations": annotations}, config_file, indent=4)

    print("Generated empty config file at config.json")

def generate_tiles(output_dir, tile_tag, tile_name, subgrid_delta, subgrid_min_x, subgrid_min_y, subgrid_max_x, subgrid_max_y):
    content = textwrap.dedent(f"""
        tile_tag = {tile_tag:05d}
        subgrid_delta(x_dim_index) = {subgrid_delta:.2f}
        subgrid_delta(y_dim_index) = {subgrid_delta:.2f}
        subgrid_min(x_dim_index) = {subgrid_min_x:.2f}
        subgrid_min(y_dim_index) = {subgrid_min_y:.2f}
        subgrid_max(x_dim_index) = {subgrid_max_x:.2f}
        subgrid_max(y_dim_index) = {subgrid_max_y:.2f}
        """)
    
    filename = os.path.join(output_dir, f"{tile_tag}_{tile_name}_{int(subgrid_delta)}.txt")
    with open(filename, "w") as file:
        file.write(content)
    print(f"Generated {filename}")

def generate_grid_tiles(x_min, x_max, y_min, y_max, delta, tile_delta, projection_attributes):
    proj = Proj(proj='laea', 
                lon_0=projection_attributes[0],
                lat_0=projection_attributes[1],
                x_0=projection_attributes[2],
                y_0=projection_attributes[3],
                a=projection_attributes[4],
                units='m')
    
    i_dim = round((x_max - x_min) / delta)
    j_dim = round((y_max - y_min) / delta)

    k = 0
    tiles = []
    for i in range(1, i_dim + 1):
        for j in range(1, j_dim + 1):
            k += 1
            xx_min = x_min + (i - 1) * delta
            yy_min = y_min + (j - 1) * delta
            xx_max = x_max + i * delta
            yy_max = y_max + j * delta
            tiles.append((k, xx_min, yy_min, xx_max, yy_max))

    return tiles

def write_tiles_to_files(tiles, tile_delta, output_dir, tile_name):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for tile in tiles:
        k, xx_min, yy_min, xx_max, yy_max = tile
        generate_tiles(output_dir, k, tile_name, tile_delta, xx_min, yy_min, xx_max, yy_max)

    print(f"Number of tiles = {len(tiles)}")
    print(f"Size of each tile = {tile_delta / 1000} x {tile_delta / 1000} km")
