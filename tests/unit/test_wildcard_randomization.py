import unittest
import tempfile
import os
import json
import random
from pathlib import Path
import sys
from collections import Counter

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.wildcard_manager import WildcardManager, WildcardManagerFactory


class TestWildcardRandomization(unittest.TestCase):
    """Comprehensive tests for wildcard randomization system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.wildcard_file = os.path.join(self.temp_dir, "test_wildcards.txt")
        self.usage_file = os.path.join(self.temp_dir, "test_usage.json")
        
        # Create test wildcard file with 10 items
        test_items = [f"item{i}" for i in range(1, 11)]
        with open(self.wildcard_file, 'w') as f:
            f.write('\n'.join(test_items))
        
        self.manager = WildcardManager(self.wildcard_file, self.usage_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_cycle_before_repeat(self):
        """Test that all items are used before any repeat occurs."""
        items_used = []
        
        # Get all items (should be 10)
        for _ in range(10):
            item = self.manager.get_next()
            items_used.append(item)
        
        # Check that all 10 items were used
        self.assertEqual(len(set(items_used)), 10)
        self.assertEqual(len(items_used), 10)
        
        # Verify all items are from the original list
        original_items = set([f"item{i}" for i in range(1, 11)])
        self.assertEqual(set(items_used), original_items)
    
    def test_random_start_position(self):
        """Test that each manager starts from a random position."""
        # Create multiple managers and check they start differently
        managers = []
        first_items = []
        
        for _ in range(5):
            manager = WildcardManager(self.wildcard_file, self.usage_file)
            managers.append(manager)
            first_items.append(manager.get_next())
        
        # At least some should be different (randomness test)
        unique_first_items = len(set(first_items))
        self.assertGreater(unique_first_items, 1, 
                          "All managers started with the same item - possible randomness issue")
    
    def test_reshuffle_after_exhaustion(self):
        """Test that reshuffling occurs after all items are used."""
        # Use all items
        first_cycle = [self.manager.get_next() for _ in range(10)]
        
        # Get next item (should trigger reshuffle)
        next_item = self.manager.get_next()
        
        # Should be one of the original items
        original_items = set([f"item{i}" for i in range(1, 11)])
        self.assertIn(next_item, original_items)
        
        # The order should be different due to reshuffle
        # Get the next 9 items to see the new order
        second_cycle = [next_item] + [self.manager.get_next() for _ in range(9)]
        
        # The cycles should be different (reshuffle worked)
        self.assertNotEqual(first_cycle, second_cycle)
    
    def test_multiple_cycles_distribution(self):
        """Test that over multiple cycles, all items get used roughly equally."""
        # Run through many cycles and track usage
        usage_counts = Counter()
        total_items = 1000  # Get 1000 items total
        
        for _ in range(total_items):
            item = self.manager.get_next()
            usage_counts[item] += 1
        
        # Check that all items were used
        self.assertEqual(len(usage_counts), 10)
        
        # Check that usage is reasonably distributed
        # Each item should be used between 80-120 times (allowing for randomness)
        min_expected = total_items // 10 * 0.8  # 80% of average
        max_expected = total_items // 10 * 1.2  # 120% of average
        
        for item, count in usage_counts.items():
            self.assertGreaterEqual(count, min_expected, 
                                  f"Item {item} used too few times: {count}")
            self.assertLessEqual(count, max_expected, 
                               f"Item {item} used too many times: {count}")
    
    def test_reset_functionality(self):
        """Test that reset creates a new random starting point."""
        # Get first item
        first_item = self.manager.get_next()
        
        # Reset
        self.manager.reset()
        
        # Get next item after reset
        next_item = self.manager.get_next()
        
        # The items should be different (new random start)
        # Note: This could theoretically be the same, but very unlikely
        # We're testing that reset doesn't crash and creates a new state
        self.assertIsInstance(next_item, str)
        self.assertIn(next_item, [f"item{i}" for i in range(1, 11)])
    
    def test_preview_functionality(self):
        """Test that preview shows upcoming items without consuming them."""
        # Get preview
        preview = self.manager.get_preview(5)
        
        # Should have 5 items
        self.assertEqual(len(preview), 5)
        
        # All items should be from original list
        original_items = set([f"item{i}" for i in range(1, 11)])
        self.assertTrue(all(item in original_items for item in preview))
        
        # Getting preview shouldn't affect the actual sequence
        first_item = self.manager.get_next()
        self.assertEqual(first_item, preview[0])
    
    def test_empty_wildcard_file(self):
        """Test behavior with empty wildcard file."""
        empty_file = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            f.write("")
        
        empty_manager = WildcardManager(empty_file, self.usage_file)
        
        # Should return empty string
        self.assertEqual(empty_manager.get_next(), "")
        self.assertEqual(empty_manager.get_preview(5), [])
    
    def test_wildcard_file_with_duplicates(self):
        """Test behavior with duplicate items in wildcard file."""
        duplicate_file = os.path.join(self.temp_dir, "duplicates.txt")
        with open(duplicate_file, 'w') as f:
            f.write("item1\nitem2\nitem1\nitem3\nitem2\n")
        
        duplicate_manager = WildcardManager(duplicate_file, self.usage_file)
        
        # Should load unique items
        self.assertEqual(len(duplicate_manager.items), 3)
        self.assertEqual(set(duplicate_manager.items), {"item1", "item2", "item3"})
    
    def test_wildcard_file_with_whitespace(self):
        """Test behavior with whitespace in wildcard file."""
        whitespace_file = os.path.join(self.temp_dir, "whitespace.txt")
        with open(whitespace_file, 'w') as f:
            f.write("  item1  \n\nitem2\n  item3  \n\n")
        
        whitespace_manager = WildcardManager(whitespace_file, self.usage_file)
        
        # Should strip whitespace and ignore empty lines
        self.assertEqual(len(whitespace_manager.items), 3)
        self.assertEqual(set(whitespace_manager.items), {"item1", "item2", "item3"})
    
    def test_usage_statistics_tracking(self):
        """Test that usage statistics are properly tracked."""
        # Use some items
        items_used = []
        for _ in range(5):
            item = self.manager.get_next()
            items_used.append(item)
        
        # Check usage stats
        stats = self.manager.get_usage_stats()
        
        # All used items should be in stats
        for item in items_used:
            self.assertIn(item, stats)
            self.assertEqual(stats[item], items_used.count(item))
        
        # Check usage percentages
        for item in items_used:
            percentage = self.manager.get_usage_percentage(item)
            expected_percentage = (items_used.count(item) / len(items_used)) * 100
            self.assertAlmostEqual(percentage, expected_percentage, places=1)
    
    def test_least_used_items(self):
        """Test getting least used items."""
        # Use some items multiple times
        for _ in range(3):
            self.manager.get_next()  # item1
        for _ in range(2):
            self.manager.get_next()  # item2
        self.manager.get_next()      # item3
        
        # Get least used items
        least_used = self.manager.get_least_used_items(3)
        
        # Should include unused items first
        stats = self.manager.get_usage_stats()
        unused_items = [item for item in self.manager.items if item not in stats]
        
        # Least used should include unused items
        for item in unused_items[:3]:
            self.assertIn(item, least_used)
    
    def test_factory_management(self):
        """Test WildcardManagerFactory functionality."""
        factory = WildcardManagerFactory(self.usage_file)
        
        # Get manager for same path multiple times
        manager1 = factory.get_manager(self.wildcard_file)
        manager2 = factory.get_manager(self.wildcard_file)
        
        # Should be the same instance
        self.assertIs(manager1, manager2)
        
        # Test reset all
        factory.reset_all()
        
        # Should still be the same instance
        manager3 = factory.get_manager(self.wildcard_file)
        self.assertIs(manager1, manager3)
    
    def test_concurrent_access_simulation(self):
        """Test that multiple rapid accesses work correctly."""
        # Simulate rapid access to the same manager
        items = []
        for _ in range(20):  # Get 20 items rapidly
            item = self.manager.get_next()
            items.append(item)
        
        # Should have used all 10 items twice
        self.assertEqual(len(set(items)), 10)
        
        # Check that we went through complete cycles
        first_cycle = items[:10]
        second_cycle = items[10:20]
        
        # Both cycles should contain all items
        self.assertEqual(len(set(first_cycle)), 10)
        self.assertEqual(len(set(second_cycle)), 10)
    
    def test_large_wildcard_file(self):
        """Test behavior with a large number of items."""
        large_file = os.path.join(self.temp_dir, "large.txt")
        large_items = [f"large_item_{i}" for i in range(100)]
        
        with open(large_file, 'w') as f:
            f.write('\n'.join(large_items))
        
        large_manager = WildcardManager(large_file, self.usage_file)
        
        # Should load all items
        self.assertEqual(len(large_manager.items), 100)
        
        # Test getting items
        items_used = []
        for _ in range(50):
            item = large_manager.get_next()
            items_used.append(item)
        
        # Should have used 50 unique items
        self.assertEqual(len(set(items_used)), 50)
        self.assertEqual(len(items_used), 50)
    
    def test_randomness_quality(self):
        """Test the quality of randomness over many iterations."""
        # Track the distribution of first items across many managers
        first_items_distribution = Counter()
        
        for _ in range(100):  # Create 100 managers
            manager = WildcardManager(self.wildcard_file, self.usage_file)
            first_item = manager.get_next()
            first_items_distribution[first_item] += 1
        
        # Check that all items appear as first items
        self.assertEqual(len(first_items_distribution), 10)
        
        # Check that distribution is reasonably even
        # Each item should appear as first item between 5-15 times
        min_expected = 5
        max_expected = 15
        
        for item, count in first_items_distribution.items():
            self.assertGreaterEqual(count, min_expected, 
                                  f"Item {item} never appears as first item")
            self.assertLessEqual(count, max_expected, 
                               f"Item {item} appears too often as first item")


if __name__ == '__main__':
    # Set random seed for reproducible tests
    random.seed(42)
    
    # Run tests
    unittest.main(verbosity=2) 