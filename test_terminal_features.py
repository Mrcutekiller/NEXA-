
import os
import json
import unittest
from main import TerminalWorkspace, TerminalTab, TerminalPane

class TestTerminalWorkspace(unittest.TestCase):
    def setUp(self):
        self.state_file = "test_terminal_state.json"
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        self.workspace = TerminalWorkspace(state_path=self.state_file)

    def tearDown(self):
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

    def test_bootstrap(self):
        """Verify initial workspace setup."""
        self.assertEqual(len(self.workspace.tabs), 1)
        self.assertEqual(len(self.workspace.panes), 1)
        self.assertIsNotNone(self.workspace.active_tab_id)

    def test_tab_management(self):
        """Test creating, switching, and closing tabs."""
        # Create
        new_tab = self.workspace.create_tab("Dev")
        self.assertEqual(len(self.workspace.tabs), 2)
        self.assertEqual(self.workspace.active_tab_id, new_tab.tab_id)
        
        # Switch
        self.workspace.switch_tab("1")
        self.assertEqual(self.workspace.get_active_tab().label, "Home")
        
        # Close
        self.workspace.close_tab("Home")
        self.assertEqual(len(self.workspace.tabs), 1)
        self.assertEqual(self.workspace.get_active_tab().label, "Dev")

    def test_pane_management(self):
        """Test splitting and focusing panes."""
        self.workspace.split_active_pane(layout="vertical", label="Logs")
        tab = self.workspace.get_active_tab()
        self.assertEqual(len(tab.pane_ids), 2)
        self.assertEqual(self.workspace.get_active_pane().label, "Logs")
        
        # Focus back
        self.workspace.focus_pane("1")
        self.assertEqual(self.workspace.get_active_pane().label, "Primary")

    def test_session_restoration(self):
        """Verify that state persists to disk and restores correctly."""
        self.workspace.create_tab("PersistenceTest")
        self.workspace.remember_command("ls -la")
        self.workspace.save()
        
        # New workspace instance pointing to same file
        new_ws = TerminalWorkspace(state_path=self.state_file)
        self.assertEqual(len(new_ws.tabs), 2)
        self.assertIn("ls -la", new_ws.command_history)
        self.assertEqual(new_ws.tabs[-1].label, "PersistenceTest")

    def test_search_logic(self):
        """Test regex and fixed search in output history."""
        pane = self.workspace.get_active_pane()
        pane.append("Error: Connection refused")
        pane.append("Success: Data synced")
        
        matches = self.workspace.search_active_output("Error", regex=False)
        self.assertEqual(len(matches), 1)
        self.assertIn("Connection refused", matches[0])

if __name__ == "__main__":
    unittest.main()
