from ami import __version__
from ami.aurora_mod_installer import AuroraModInstaller
from ami.config_loader import ConfigLoader


def test_version():
    assert __version__ == '0.1.0'


def test_directory_path_correctness():
    required_configs = {
        'mod_list': "config.yaml",
        'game_config': "kotor.yaml"
    }

    config_loader = ConfigLoader()
    mods_config = config_loader.load_config(required_configs.get('mod_list'))
    game_config = config_loader.load_config(required_configs.get('game_config'))

    required_dirs = {
        'download': {
            'path': game_config['download'],
            'required_empty': False
        },
        'temp': {
            'path': game_config['temp'],
            'required_empty': True
        },
        'override': {
            'path': game_config['override'],
            'required_empty': True
        }
    }

    ami = AuroraModInstaller(game_config, mods_config, required_dirs)

    assert ami.required_dirs == required_dirs
