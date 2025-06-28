import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from core.wildcard_manager import WildcardManager, WildcardManagerFactory


class TestWildcardManager(unittest.TestCase):
    """Test cases for WildcardManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.wildcard_file = os.path.join(self.temp_dir, "test_wildcards.txt")
        self.usage_file = os.path.join(self.temp_dir, "test_usage.json")
        
        # Create test wildcard file
        with open(self.wildcard_file, 'w') as f:
            f.write("item1\nitem2\nitem3\nitem4\nitem5\n")
        
        self.manager = WildcardManager(self.wildcard_file, self.usage_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_items(self):
        """Test loading items from file."""
        self.assertEqual(len(self.manager.items), 5)
        self.assertIn("item1", self.manager.items)
        self.assertIn("item5", self.manager.items)
    
    def test_get_next(self):
        """Test getting next item."""
        items = []
        for _ in range(5):
            items.append(self.manager.get_next())
        
        # Should get all 5 items
        self.assertEqual(len(set(items)), 5)
        self.assertTrue(all(item in self.manager.items for item in items))
    
    def test_reshuffle_after_exhaustion(self):
        """Test that items are reshuffled after exhaustion."""
        # Get all items
        first_round = [self.manager.get_next() for _ in range(5)]
        
        # Get next item (should trigger reshuffle)
        next_item = self.manager.get_next()
        self.assertIn(next_item, self.manager.items)
    
    def test_reset(self):
        """Test reset functionality."""
        # Get first item
        first_item = self.manager.get_next()
        
        # Reset
        self.manager.reset()
        
        # Get next item (should be different due to new random start)
        next_item = self.manager.get_next()
        # Note: This could theoretically be the same, but very unlikely
        # In practice, we're testing that reset doesn't crash
    
    def test_get_preview(self):
        """Test preview functionality."""
        preview = self.manager.get_preview(3)
        self.assertEqual(len(preview), 3)
        self.assertTrue(all(item in self.manager.items for item in preview))
    
    def test_usage_stats(self):
        """Test usage statistics."""
        # Get an item
        item = self.manager.get_next()
        
        # Check usage stats
        stats = self.manager.get_usage_stats()
        self.assertIn(item, stats)
        self.assertEqual(stats[item], 1)
    
    def test_usage_percentage(self):
        """Test usage percentage calculation."""
        # Get an item twice
        item = self.manager.get_next()
        self.manager.get_next()  # Get another item
        
        percentage = self.manager.get_usage_percentage(item)
        self.assertEqual(percentage, 50.0)
    
    def test_least_used_items(self):
        """Test getting least used items."""
        # Use some items
        self.manager.get_next()  # item1
        self.manager.get_next()  # item2
        
        least_used = self.manager.get_least_used_items(3)
        self.assertEqual(len(least_used), 3)
        
        # Should include unused items
        used_items = set(self.manager.get_usage_stats().keys())
        unused_in_least = [item for item in least_used if item not in used_items]
        self.assertGreater(len(unused_in_least), 0)
    
    def test_reset_usage_stats(self):
        """Test resetting usage statistics."""
        # Use an item
        item = self.manager.get_next()
        
        # Reset stats
        self.manager.reset_usage_stats()
        
        # Check stats are cleared
        stats = self.manager.get_usage_stats()
        self.assertEqual(len(stats), 0)
    
    def test_empty_file(self):
        """Test behavior with empty wildcard file."""
        empty_file = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            pass
        
        empty_manager = WildcardManager(empty_file, self.usage_file)
        self.assertEqual(empty_manager.get_next(), "")
        self.assertEqual(empty_manager.get_preview(5), [])
    
    def test_nonexistent_file(self):
        """Test behavior with nonexistent file."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        nonexistent_manager = WildcardManager(nonexistent_file, self.usage_file)
        self.assertEqual(nonexistent_manager.get_next(), "")
        self.assertEqual(nonexistent_manager.get_preview(5), [])


class TestWildcardManagerFactory(unittest.TestCase):
    """Test cases for WildcardManagerFactory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.usage_file = os.path.join(self.temp_dir, "test_usage.json")
        self.factory = WildcardManagerFactory(self.usage_file)
        
        # Create test wildcard files
        self.wildcard1 = os.path.join(self.temp_dir, "wildcard1.txt")
        self.wildcard2 = os.path.join(self.temp_dir, "wildcard2.txt")
        
        with open(self.wildcard1, 'w') as f:
            f.write("a1\na2\na3\n")
        
        with open(self.wildcard2, 'w') as f:
            f.write("b1\nb2\nb3\nb4\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_manager(self):
        """Test getting manager for wildcard path."""
        manager1 = self.factory.get_manager(self.wildcard1)
        manager2 = self.factory.get_manager(self.wildcard2)
        
        self.assertIsInstance(manager1, WildcardManager)
        self.assertIsInstance(manager2, WildcardManager)
        self.assertNotEqual(manager1, manager2)
    
    def test_manager_caching(self):
        """Test that managers are cached."""
        manager1 = self.factory.get_manager(self.wildcard1)
        manager2 = self.factory.get_manager(self.wildcard1)
        
        self.assertIs(manager1, manager2)
    
    def test_reset_all(self):
        """Test resetting all managers."""
        manager1 = self.factory.get_manager(self.wildcard1)
        manager2 = self.factory.get_manager(self.wildcard2)
        
        # Use some items
        manager1.get_next()
        manager2.get_next()
        
        # Reset all
        self.factory.reset_all()
        
        # Check that managers are still functional
        self.assertIsInstance(manager1.get_next(), str)
        self.assertIsInstance(manager2.get_next(), str)
    
    def test_get_all_usage_stats(self):
        """Test getting usage stats for all managers."""
        manager1 = self.factory.get_manager(self.wildcard1)
        manager2 = self.factory.get_manager(self.wildcard2)
        
        # Use some items
        manager1.get_next()
        manager2.get_next()
        manager2.get_next()
        
        all_stats = self.factory.get_all_usage_stats()
        
        self.assertIn("wildcard1", all_stats)
        self.assertIn("wildcard2", all_stats)
        self.assertEqual(len(all_stats["wildcard1"]), 1)
        self.assertEqual(len(all_stats["wildcard2"]), 2)


if __name__ == '__main__':
    unittest.main() 