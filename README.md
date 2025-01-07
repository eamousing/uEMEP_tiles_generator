# uEMEP Tiles Generator

This project provides a command-line interface (CLI) tool for generating spatial tiles for the uEMEP model. The tool allows users to generate tiles based on specified parameters and save them to a specified output directory.

## Features

- Generate tiles with specified dimensions and projection attributes.
- Save generated tiles to a specified output directory.
- Generate an empty JSON configuration file with annotations for easy customization.

## Installation

    ```sh
    # Clone the repository
    git clone https://github.com/yourusername/uEMEP_tiles_generator.git

    # Navigate to the project directory
    cd uEMEP_tiles_generator

    # Install the required dependencies
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage

### Generate Tiles

To generate tiles, create a JSON configuration file with the required parameters. You can use the `--generate-config` option to generate an empty configuration file with annotations:

```sh
python src/tiles_generator.py --generate-config
```

This will create a `config.json` file in the current directory. Edit this file to specify the parameters for the tile generation. Note that this command will overwrite any existing `config.json` file, so renaming this file before editing it is advised.

### Run the Tile Generator

Once you have edited the configuration file, run the tile generator with the `--config` option:

```sh
python src/tiles_generator.py --config config.json
```

This will generate the tiles based on the specified parameters and save them to the specified output directory.

