from ami.config_loader import ConfigLoader


def test_config_setting_for_kotor():
    config_loader = ConfigLoader()
    game_config = config_loader.load_config('kotor.yaml')

    kotor_allowed_file_extensions = ['mdx', 'mdl', 'txi', 'tga', 'tif']
    assert game_config['allowed_file_extensions'] == kotor_allowed_file_extensions
