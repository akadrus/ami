from ami.file_system_helper import FileSystemHelper
fsh = FileSystemHelper()


def test_clears_directory_if_required(tmpdir):
    override_dir = tmpdir.mkdir("override")
    file = override_dir.join("test_file.txt")
    file.write("this_file_should_be_deleted")

    fsh.create_required_dir({"path": override_dir, "required_empty": True})
    assert len(override_dir.listdir()) == 0


def test_dont_clear_dir(tmpdir):
    override_dir = tmpdir.mkdir("override")
    file = override_dir.join("test_file.txt")
    file.write("this_file_should_be_deleted")

    fsh.create_required_dir({"path": override_dir, "required_empty": False})
    assert len(override_dir.listdir()) == 1
