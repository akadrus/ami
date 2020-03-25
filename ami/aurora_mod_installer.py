from ami.file_system_helper import FileSystemHelper
from ami.archive_helper import ArchiveHelper
import os
import click
import shutil
from tabulate import tabulate


class AuroraModInstaller:
    mod_extensions = []
    # This should be coming from global_config or stay here
    archives_extensions = ("7z", "zip", "rar")
    move_table = {}

    def __init__(self, game_config, mods_config, required_dirs):
        self.game_config = game_config
        self.mod_extensions = tuple(game_config["allowed_file_extensions"])
        self.mods_config = mods_config
        self.required_dirs = required_dirs
        self.fsh = FileSystemHelper()
        self.ah = ArchiveHelper()

    def __call__(self):
        # main loop, should be elsewhere #FIXME
        for mod_slug in self.mods_config:
            self.handle_config_entry(mod_slug)
        if click.confirm("Print final mod configuration?"):
            print_list = []
            headers = ["file", "provider"]
            for file, info in self.move_table.items():
                print_list.append([file, info["provider"]])
            print(tabulate(print_list, headers, tablefmt="fancy_grid"))
        if click.confirm("Can we proceed?", abort=True):
            for file_name, info in self.move_table.items():
                shutil.move(info["source"], info["destination"])
            print("Done!")
            return

    def handle_config_entry(self, modification_config_slug):
        modification_config = self.mods_config[modification_config_slug]
        if "type" in modification_config and modification_config["type"] == "STOP":
            wait = True
            while wait:
                input("Press Enter to continue...")
        else:
            self.handle_mod_from_config(modification_config)

    def handle_mod_from_config(self, modification_config):
        search_path = self.required_dirs["download"]["path"]
        file_info = self.fsh.find_file_by_part_of_name(
            modification_config["file_name"], search_path
        )
        if file_info and os.path.isfile(file_info["absolute_path"]):
            modification_config["file_info"] = file_info
            self.install_mod(modification_config)
        else:
            print("Failed to find " + modification_config["file_name"])

    def install_mod(self, modification_config):
        target = modification_config["file_info"]["file_name"]
        modification_config["temp_path"] = self.fsh.get_temporary_path(
            self.required_dirs["temp"]["path"], target
        )
        temp_path = modification_config["temp_path"]
        self.ah.extract(modification_config["file_info"]["absolute_path"], temp_path)

        # if there is no variants at all
        if "variants" not in modification_config:
            modification_config["variants"] = {}

        if "main" not in modification_config["variants"]:
            root_dir = self.fsh.define_root_dir(
                modification_config,
                temp_path,
                self.required_dirs["temp"]["path"],
                self.mod_extensions,
            )
            main_variant = {**modification_config, **root_dir}
            modification_config["variants"] = {
                **modification_config["variants"],
                **{"main": main_variant},
            }

        if (
            modification_config["variants"]["main"] is not False
            and "path" not in modification_config["variants"]["main"]
        ):
            root_dir = self.fsh.define_root_dir(
                modification_config,
                temp_path,
                self.required_dirs["temp"]["path"],
                self.mod_extensions,
            )
            modification_config["variants"]["main"] = {
                **modification_config["variants"]["main"],
                **root_dir,
                **modification_config,
            }

        variants = modification_config["variants"]
        self.analyze_variant_directory(variants["main"])
        root_dir = variants["main"]["path"]
        variants.pop("main", None)

        # FIXME źle tworzy PATH dla wariantów, do przebuodwania!
        for mod_dir in variants:
            variants[mod_dir]["path"] = os.path.join(
                root_dir, variants[mod_dir]["path"]
            )
            variants[mod_dir]["file_name"] = target
            self.analyze_variant_directory(variants[mod_dir])

    def analyze_variant_directory(self, modification_config):
        temp_mod_path = modification_config["path"]
        if (
            "have_files" in modification_config
            and modification_config["have_files"] is False
        ):
            return 0

        if "rename_files" in modification_config:
            for file_to_rename in modification_config["rename_files"]:
                if len(file_to_rename) == 2:
                    source = os.path.join(temp_mod_path, file_to_rename[0])
                    dest = os.path.join(temp_mod_path + file_to_rename[1])
                    os.rename(source, dest)

        if "delete_files" in modification_config:
            for file_to_delete in modification_config["delete_files"]:
                delete_target = os.path.join(temp_mod_path, file_to_delete)
                os.remove(delete_target)

        if "preserve_files" in modification_config:
            for r, d, f in os.walk(temp_mod_path):
                for file in f:
                    if file not in modification_config["preserve_files"]:
                        delete_target = os.path.join(temp_mod_path, file)
                        os.remove(delete_target)

        for root, dirs, files in os.walk(temp_mod_path):
            for file in files:
                extension = self.get_file_extension(file)
                if extension.endswith(self.mod_extensions):
                    source = os.path.join(temp_mod_path, file)
                    destination = os.path.join(
                        self.required_dirs["override"]["path"], file
                    )
                    self.move_table[file] = {
                        "source": source,
                        "destination": destination,
                        "provider": modification_config["file_name"],
                        "variant": modification_config["path"],
                    }
            # @FIXME we don't want to go into subdirectories without specific config,
            # there should be some kind of return status
            break
        # @FIXME! handle preserve_only and throw error if both delete and preserve directive exist in config
        return 0

    def get_file_extension(self, path):
        filename, file_extension = os.path.splitext(path)
        return file_extension.lower()
