import os
import json
from pathlib import Path

import typer
from pipeline import Pipeline
from loguru import logger

def app():
    """Run the app."""
    # Get the streams from the app config
    app_config_path = Path(__file__).parent / "configs" / "app_config.json"
    with open(str(app_config_path), "r") as file:
        streams = json.load(file)["streams"]
        
    model_config_path = Path(__file__).parent / "configs" / "detector_config.txt"
    if not model_config_path.exists():
        raise FileNotFoundError(f"{model_config_path} does not exist")
    
    logger.info("Building the pipeline")
    
    pipeline = Pipeline(
        streams=streams,
        tiled_output_height=1080,
        tiled_output_width=1920,
        model_config_path=model_config_path
    )
    
    logger.info("Starting pipeline")
    pipeline.run()

@logger.catch()
def main() -> None:
    """Main function."""
    typer.run(app)
    
    
if __name__ == "__main__":
    main()