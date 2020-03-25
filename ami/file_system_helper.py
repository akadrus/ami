import os
import shutil


class FileSystemHelper:
    @staticmethod
    def get_temporary_path(temp_directory, file_name):
        file_name = file_name.replace(".", "_")
        return os.path.join(temp_directory, file_name)

    @staticmethod
    def create_required_dir(directory):
        dir_path = directory.get("path")
        should_be_empty = directory.get("required_empty", False)
        if os.path.isdir(dir_path) and should_be_empty:
            shutil.rmtree(dir_path)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        return True

    @staticmethod
    def find_file_by_part_of_name(file_name, modifications_location):
        for r, d, f in os.walk(modifications_location):
            for file in f:
                if file_name in file:
                    return {"file_name": file, "absolute_path": os.path.join(r, file)}

    # it will choose one folder as root for others path (required for autoinstall)
    @staticmethod
    def define_root_dir(config, temp_path, ami_temp_dir, game_mod_extensions):
        if "root_dir" in config:
            return config["root_dir"]

        mod_files = {}
        for root, dirs, files in os.walk(temp_path):
            # we remove path to kmi temp dir since we use full path for safety, but we
            # don't want to count it in our nest_level calculations
            relative_path = root.replace(ami_temp_dir, "")
            path = relative_path.split(os.sep)
            base_name = os.path.basename(root)

            current_dir = {
                "absolute_path": root,
                "relative_path": relative_path,
                "nest_level": len(path) - 1,
                "have_files": False,
            }

            # @FIXME it should be function
            for file in files:
                if file.endswith(game_mod_extensions):
                    current_dir["have_files"] = True
            # @FIXME END

            mod_files[base_name] = current_dir

        root_dir = {}
        # @FIXME rename value and key to something more redable
        for key, value in mod_files.items():
            # if we have no idea what root_dir could be
            if value["have_files"] and not root_dir:
                root_dir = value
            elif value["have_files"]:
                if root_dir["nest_level"] == value["nest_level"]:
                    # we're going deeper
                    root_dir["have_sliblings_with_files"] = True
                elif value["nest_level"] > root_dir["nest_level"]:
                    # this should never happen
                    throw_error_so_much = 1
                elif root_dir["nest_level"] > value["nest_level"]:
                    # that's it!
                    root_dir = value

            # if 'have_sliblings_with_files' in root_dir and root_dir['have_sliblings_with_files'] is True:
            #   we move our root one level up

        return {"path": root_dir["absolute_path"]}
