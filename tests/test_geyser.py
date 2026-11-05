import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("geyser_config", ROOT / "scripts" / "configure_geyser.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GeyserConfigTests(unittest.TestCase):
    def test_nethernets_and_floodgate(self):
        before = """bedrock:
  port: 19133
  transport: raknet
remote:
  auth-type: online
"""
        after = mod.configure(before)
        self.assertIn("port: 19132", after)
        self.assertIn("transport: nethernet", after)
        self.assertIn("auth-type: floodgate", after)
        self.assertEqual(mod.configure(after), after)

    def test_missing_transport_is_inserted(self):
        text = "bedrock:\n  port: 19132\njava:\n  auth-type: online\n"
        after = mod.configure(text)
        self.assertIn("transport: nethernet", after)
        self.assertIn("auth-type: floodgate", after)

    def test_fail_closed_on_unrecognized_config(self):
        with self.assertRaises(ValueError):
            mod.configure("java:\n  auth-type: online\n")
        with self.assertRaises(ValueError):
            mod.configure("bedrock:\n  port: 19132\n")

if __name__ == "__main__":
    unittest.main()
