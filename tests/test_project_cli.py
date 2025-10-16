import unittest
import tempfile
import shutil
import sys
import json
from unittest import mock
from pathlib import Path

import project_cli


class TestProjectCLI(unittest.TestCase):
    def setUp(self):
        # Patch CONFIG_DIR and DATA_FILE to use a temp directory
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.data_file = self.config_dir / "projects.json"
        project_cli.CONFIG_DIR = self.config_dir
        project_cli.DATA_FILE = self.data_file

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_cli(self, argv):
        with mock.patch.object(sys, 'argv', argv):
            try:
                project_cli.main()
            except SystemExit as e:
                return e.code
        return 0

    def test_add_project(self):
        code = self.run_cli(['project', 'add', 'alpha'])
        self.assertEqual(code, 0)
        with self.data_file.open() as f:
            data = json.load(f)
        self.assertIn('alpha', data)
        self.assertEqual(data['active-project'], 'alpha')

    def test_add_duplicate_project(self):
        self.run_cli(['project', 'add', 'alpha'])
        code = self.run_cli(['project', 'add', 'alpha'])
        self.assertNotEqual(code, 0)

    def test_switch_existing_project(self):
        self.run_cli(['project', 'add', 'alpha'])
        self.run_cli(['project', 'add', 'beta'])
        code = self.run_cli(['project', 'alpha'])
        self.assertEqual(code, 0)
        with self.data_file.open() as f:
            data = json.load(f)
        self.assertEqual(data['active-project'], 'alpha')

    def test_switch_nonexistent_project(self):
        code = self.run_cli(['project', 'ghost'])
        self.assertNotEqual(code, 0)

    def test_rename_project(self):
        self.run_cli(['project', 'add', 'alpha'])
        code = self.run_cli(['project', 'rename', 'alpha', 'omega'])
        self.assertEqual(code, 0)
        with self.data_file.open() as f:
            data = json.load(f)
        self.assertIn('omega', data)
        self.assertNotIn('alpha', data)

    def test_rename_nonexistent_project(self):
        code = self.run_cli(['project', 'rename', 'ghost', 'omega'])
        self.assertNotEqual(code, 0)

    def test_rename_to_existing_project(self):
        self.run_cli(['project', 'add', 'alpha'])
        self.run_cli(['project', 'add', 'beta'])
        code = self.run_cli(['project', 'rename', 'alpha', 'beta'])
        self.assertNotEqual(code, 0)

    def test_remove_project(self):
        self.run_cli(['project', 'add', 'alpha'])
        code = self.run_cli(['project', 'remove', 'alpha', '-y'])
        self.assertEqual(code, 0)
        with self.data_file.open() as f:
            data = json.load(f)
        self.assertNotIn('alpha', data)

    def test_remove_nonexistent_project(self):
        code = self.run_cli(['project', 'remove', 'ghost', '-y'])
        self.assertNotEqual(code, 0)


if __name__ == '__main__':
    unittest.main()
