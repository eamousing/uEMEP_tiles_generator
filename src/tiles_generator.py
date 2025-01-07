import argparse
import json
import sys
from utils.generator import generate_grid_tiles, write_tiles_to_files, generate_empty_config

def main():
    parser = argparse.ArgumentParser(
        description="Tiles Generator for uEMEP",
        epilog="Example usage: python src/tiles_generator.py --config config.json"
    )
    parser.add_argument(
        '--config', type=str,
        help='Path to the JSON configuration file containing the parameters for tile generation'
    )
    parser.add_argument(
        '--generate-config', action='store_true',
        help='Generate an empty JSON configuration file'
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()

    if args.generate_config:
        generate_empty_config()
        sys.exit(0)

    if args.config:
        with open(args.config, 'r') as config_file:
            config = json.load(config_file)["config"]

        tiles = generate_grid_tiles(
            config['x_min'], config['x_max'], config['y_min'], config['y_max'],
            config['delta'], config['tile_delta'], config['projection_attributes']
        )
        write_tiles_to_files(tiles, config['tile_delta'], config['output_dir'], config['tile_name'])

if __name__ == "__main__":
    main()
