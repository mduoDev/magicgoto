import unittest
import tempfile
import shutil
import sys
import json
from unittest import mock
from pathlib import Path
import goto_cli


class TestGotoCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.data_file = self.config_dir / "projects.json"
        goto_cli.CONFIG_DIR = self.config_dir
        goto_cli.DATA_FILE = self.data_file
        self.config_dir.mkdir(exist_ok=True)
        # Set up a default project
        self.project = "testproj"
        self.init_data({self.project: {}, "active-project": self.project})

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def init_data(self, data):
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def run_cli(self, argv):
        with mock.patch.object(sys, "argv", argv):
            try:
                goto_cli.main()
            except SystemExit as e:
                return e.code
        return 0

    def get_data(self):
        with self.data_file.open() as f:
            return json.load(f)

    # 1. Add a new key: OK
    def test_add_new_key(self):
        code = self.run_cli(["goto", "add", "foo", "/tmp"])
        self.assertEqual(code, 0)
        data = self.get_data()
        self.assertIn("foo", data[self.project])

    # 1b. Add an existing key: expect error
    def test_add_existing_key(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        code = self.run_cli(["goto", "add", "foo", "/tmp2"])
        self.assertNotEqual(code, 0)

    # 2. Update an existing key: OK
    def test_update_existing_key(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        code = self.run_cli(["goto", "update", "foo", "/tmp2"])
        self.assertEqual(code, 0)
        data = self.get_data()
        self.assertEqual(data[self.project]["foo"], str(Path("/tmp2").absolute()))

    # 2b. Update a non-existing key: error
    def test_update_nonexisting_key(self):
        code = self.run_cli(["goto", "update", "bar", "/tmp2"])
        self.assertNotEqual(code, 0)

    # 3. Add multiple url and directory keys
    def test_list_keys(self):
        self.run_cli(["goto", "add", "site", "http://example.com"])
        self.run_cli(["goto", "add", "docs", "http://docs.com"])
        self.run_cli(["goto", "add", "src", "/src"])
        self.run_cli(["goto", "add", "build", "/build"])
        # a. List keys with url
        with mock.patch("sys.stdout") as mock_stdout:
            self.run_cli(["goto", "list", "url"])
            output_url = "".join([c[0][0] for c in mock_stdout.write.call_args_list])
        self.assertIn("site", output_url)
        self.assertIn("docs", output_url)
        self.assertNotIn("src", output_url)
        # b. List keys with directories
        with mock.patch("sys.stdout") as mock_stdout:
            self.run_cli(["goto", "list", "dir"])
            output_dir = "".join([c[0][0] for c in mock_stdout.write.call_args_list])
        self.assertIn("src", output_dir)
        self.assertIn("build", output_dir)
        self.assertNotIn("site", output_dir)
        # c. List all
        with mock.patch("sys.stdout") as mock_stdout:
            self.run_cli(["goto", "list"])
            output_all = "".join([c[0][0] for c in mock_stdout.write.call_args_list])
        # d. a + b == c
        for k in ("site", "docs", "src", "build"):
            self.assertIn(k, output_all)

    # 4. Rename existing key: OK
    def test_rename_existing_key(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        code = self.run_cli(["goto", "rename", "foo", "bar"])
        self.assertEqual(code, 0)
        data = self.get_data()
        self.assertIn("bar", data[self.project])
        self.assertNotIn("foo", data[self.project])

    # 4b. Rename non-existing key: error
    def test_rename_nonexisting_key(self):
        code = self.run_cli(["goto", "rename", "ghost", "bar"])
        self.assertRaises(KeyError, lambda: self.get_data()[self.project]["bar"])
        self.assertNotEqual(code, 0)

    # 4c. Rename existing key to another existing key: ERROR
    def test_rename_to_existing_key(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        self.run_cli(["goto", "add", "bar", "/tmp2"])
        code = self.run_cli(["goto", "rename", "foo", "bar"])
        self.assertNotEqual(code, 0)

    # 5. Remove existing key: OK
    def test_remove_existing_key(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        code = self.run_cli(["goto", "remove", "foo"])
        self.assertEqual(code, 0)
        data = self.get_data()
        self.assertNotIn("foo", data[self.project])

    # 5b. Remove a non-existing key: ERROR
    def test_remove_nonexisting_key(self):
        code = self.run_cli(["goto", "remove", "ghost"])
        self.assertNotEqual(code, 0)

    # 6. Check with haskey
    def test_haskey(self):
        self.run_cli(["goto", "add", "foo", "/tmp"])
        with mock.patch("sys.stdout") as mock_stdout:
            self.run_cli(["goto", "haskey", "foo"])
            output = "".join([c[0][0] for c in mock_stdout.write.call_args_list])
        self.assertIn(str(Path("/tmp").absolute()), output)
        with mock.patch("sys.stdout") as mock_stdout:
            self.run_cli(["goto", "haskey", "ghost"])
            output = "".join([c[0][0] for c in mock_stdout.write.call_args_list])
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()
