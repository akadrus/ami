import click
import os
from ami.file_system_helper import FileSystemHelper
from ami.config_loader import ConfigLoader
from ami.aurora_mod_installer import AuroraModInstaller


fsh = FileSystemHelper()


@click.command()
def cli():
    # TODO we should let user select game and ask about config if there's none
    required_configs = {"mod_list": "config.yaml", "game_config": "kotor.yaml"}

    configs_status = {os.path.isfile(config) for config in required_configs.values()}

    config_loader = ConfigLoader()
    mods_config = config_loader.load_config(required_configs.get("mod_list"))
    game_config = config_loader.load_config(required_configs.get("game_config"))

    required_dirs = {
        "download": {"path": game_config["download"], "required_empty": False},
        "temp": {"path": game_config["temp"], "required_empty": True},
        "override": {"path": game_config["override"], "required_empty": True},
    }
    dirs_status = {
        fsh.create_required_dir(directory) for directory in required_dirs.values()
    }

    # TODO this code should be moved out to testable class

    if configs_status and dirs_status:
        ami = AuroraModInstaller(game_config, mods_config, required_dirs)
        ami()


if __name__ == "__main__":
    cli()
