#!/usr/bin/env python3
"""
Tiles Generator for uEMEP

This script generates grid tiles for the uEMEP model based on a configuration file.

Example usage:
    python src/tiles_generator.py --config config.json --make-tile-map
"""

import argparse
import json
import sys
from utils.generator import generate_grid_tiles, write_tiles_to_files, generate_empty_config, plot_tiles

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Tiles Generator for uEMEP",
        epilog="Example usage: python src/tiles_generator.py --config config.json"
    )

    # Add arguments to the parser
    parser.add_argument(
        '--config', type=str,
        help='Path to the JSON configuration file containing the parameters for tile generation.'
    )
    parser.add_argument(
        '--generate-config', action='store_true',
        help='Generate an empty JSON configuration file.'
    )
    parser.add_argument(
        '--make-tile-map', action='store_true',
        help='Generate a map with the specified extent and plot the tiles.'
    )
    
    # Print help message if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    # Parse the arguments
    args = parser.parse_args()

    # Generate an empty config file if requested
    if args.generate_config:
        generate_empty_config()
        sys.exit(0)

    # Load the configuration file and denerate the tiles
    if args.config:
        with open(args.config, 'r') as config_file:
            config = json.load(config_file)["config"]

        # Overwrite coordinates if country is specified
        if "country" in config and config["country"]:
            with open('data/europe_bounding_boxes.json', 'r') as bbox_file:
                bounding_boxes = json.load(bbox_file)
                country = config["country"]
                if country in bounding_boxes:
                    bbox = bounding_boxes[country]
                    config["x_min"] = bbox["x_min"]
                    config["x_max"] = bbox["x_max"]
                    config["y_min"] = bbox["y_min"]
                    config["y_max"] = bbox["y_max"]
                else:
                    raise ValueError(f"Country '{country}' not found in europe_bounding_boxes.json")

        # Generate grid tiles based on the configuration
        tiles = generate_grid_tiles(config)

        # Plot the tiles if requested
        if args.make_tile_map:
            plot_tiles(tiles, config)

        # Write the tiles to files
        write_tiles_to_files(tiles, config)

if __name__ == "__main__":
    main()
