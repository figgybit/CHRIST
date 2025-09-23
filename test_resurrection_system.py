#!/usr/bin/env python3
"""
Comprehensive Test Suite for Resurrection System
Includes unit tests and integration tests
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent))

from resurrections.resurrection_consciousness import ResurrectionConsciousness, ResurrectionBot
from resurrections.jesus_simple import SimpleJesus


class TestResurrectionUnitTests(unittest.TestCase):
    """Unit tests for resurrection components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir(parents=True)

        # Create test Gospel data
        self.create_test_gospels()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_gospels(self):
        """Create test Gospel files."""
        # Thomas content
        thomas_file = self.test_data_dir / "thomas.txt"
        thomas_file.write_text("""
Thomas, also known as Didymus, was one of the twelve apostles of Jesus.

Thomas is famously known for doubting Jesus's resurrection until he could see and touch Jesus's wounds.

Jesus appeared to Thomas and said: Put your finger here and see my hands.
Reach out your hand and put it into my side. Stop doubting and believe.

Thomas responded: My Lord and my God!
        """)

        # Daily life content
        daily_file = self.test_data_dir / "daily_life.txt"
        daily_file.write_text("""
Jesus walked with fishermen like Peter and Andrew.

They traveled throughout Galilee, teaching in synagogues and healing the sick.

Jesus often withdrew to solitary places to pray.

He ate with tax collectors and sinners, showing God's love to all.
        """)

        # Teachings
        teachings_file = self.test_data_dir / "teachings.txt"
        teachings_file.write_text("""
Love one another as I have loved you.

The kingdom of God is within you.

Ask and it shall be given to you; seek and you shall find.

Do unto others as you would have them do unto you.
        """)

    def test_resurrection_initialization(self):
        """Test that ResurrectionConsciousness initializes correctly."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_figure",
            bundle_dir=Path(self.temp_dir) / "test_bundle"
        )

        # Check that directories are created
        self.assertTrue(consciousness.bundle_dir.exists())
        self.assertTrue(consciousness.data_dir.exists())
        self.assertTrue(consciousness.vector_db_dir.exists())
        self.assertTrue(consciousness.metadata_file.exists())

        # Check metadata
        self.assertEqual(consciousness.metadata["figure_name"], "test_figure")
        self.assertIn("created_at", consciousness.metadata)

    def test_indexing_with_valid_data(self):
        """Test indexing Gospel texts into vector database."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=Path(self.temp_dir) / "test_bundle"
        )

        # Index the test data
        results = consciousness.index_texts(self.test_data_dir)

        # Verify results
        self.assertNotIn("error", results)
        self.assertGreater(results["total_documents"], 0)
        self.assertEqual(len(results["indexed_files"]), 3)  # We created 3 files
        self.assertEqual(len(results["errors"]), 0)

    def test_indexing_with_missing_data(self):
        """Test handling of missing data directory."""
        consciousness = ResurrectionConsciousness(
            figure_name="nonexistent",
            bundle_dir=Path(self.temp_dir) / "test_bundle"
        )

        # Try to index non-existent data
        results = consciousness.index_texts()

        # Should return error but not crash
        self.assertIn("error", results)
        self.assertEqual(results["total_documents"], 0)
        self.assertEqual(len(results["indexed_files"]), 0)

    def test_query_thomas(self):
        """Test querying about Thomas."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=Path(self.temp_dir) / "test_bundle"
        )

        # Index data first
        consciousness.index_texts(self.test_data_dir)

        # Query about Thomas
        result = consciousness.query("Who was Thomas?", use_llm=False)

        # Verify results
        self.assertIn("sources", result)
        self.assertGreater(len(result["sources"]), 0)

        # Check that Thomas is mentioned in sources
        thomas_found = any("Thomas" in source["text"] or "Didymus" in source["text"]
                          for source in result["sources"])
        self.assertTrue(thomas_found, "Thomas should be found in query results")

    def test_query_daily_life(self):
        """Test querying about daily life."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=Path(self.temp_dir) / "test_bundle"
        )

        # Index data first
        consciousness.index_texts(self.test_data_dir)

        # Query about daily life
        result = consciousness.query("Tell me about daily life with disciples", use_llm=False)

        # Verify results
        self.assertGreater(len(result["sources"]), 0)

        # Check relevant content
        relevant_found = any(
            "fishermen" in source["text"] or
            "Galilee" in source["text"] or
            "traveled" in source["text"]
            for source in result["sources"]
        )
        self.assertTrue(relevant_found, "Daily life content should be found")

    def test_simple_jesus_responds_to_thomas(self):
        """Test that SimpleJesus responds appropriately to Thomas queries."""
        simple_jesus = SimpleJesus()
        simple_jesus.gospel_content = {
            "test.txt": "Thomas, also called Didymus, one of the twelve apostles"
        }

        response = simple_jesus.respond("Tell me about Thomas")

        # Should mention Thomas
        self.assertIn("Thomas", response)

    def test_metadata_persistence(self):
        """Test that metadata persists between sessions."""
        bundle_dir = Path(self.temp_dir) / "persist_test"

        # First session
        consciousness1 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=bundle_dir
        )
        consciousness1.index_texts(self.test_data_dir)

        # Get document count
        doc_count1 = consciousness1.metadata["statistics"]["total_documents"]

        # Second session - should load existing metadata
        consciousness2 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=bundle_dir
        )

        doc_count2 = consciousness2.metadata["statistics"]["total_documents"]

        self.assertEqual(doc_count1, doc_count2, "Metadata should persist")

    def test_bundle_export_import(self):
        """Test exporting and importing consciousness bundles."""
        # Create consciousness and index data
        bundle_dir1 = Path(self.temp_dir) / "export_test"
        consciousness1 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=bundle_dir1
        )
        consciousness1.index_texts(self.test_data_dir)

        # Export bundle
        export_path = Path(self.temp_dir) / "bundle.tar.gz"
        success = consciousness1.export_bundle(str(export_path))
        self.assertTrue(success)
        self.assertTrue(export_path.exists())

        # Create new consciousness and import
        bundle_dir2 = Path(self.temp_dir) / "import_test"
        consciousness2 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=bundle_dir2 / "test_jesus"
        )

        success = consciousness2.import_bundle(str(export_path))
        self.assertTrue(success)

        # Verify data was imported
        self.assertEqual(
            consciousness2.metadata["statistics"]["total_documents"],
            consciousness1.metadata["statistics"]["total_documents"]
        )


class TestResurrectionIntegration(unittest.TestCase):
    """Integration tests for the full resurrection system."""

    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Create realistic Gospel data structure
        self.data_dir = Path(self.temp_dir) / "data" / "jesus_christ"
        self.canonical_dir = self.data_dir / "canonical"
        self.teachings_dir = self.data_dir / "teachings"
        self.daily_dir = self.data_dir / "daily_life"

        # Create directories
        self.canonical_dir.mkdir(parents=True)
        self.teachings_dir.mkdir(parents=True)
        self.daily_dir.mkdir(parents=True)

        # Create Gospel files
        self.create_gospel_files()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_gospel_files(self):
        """Create realistic Gospel file structure."""
        # John chapter with Thomas
        (self.canonical_dir / "john.txt").write_text("""
JOHN CHAPTER 20
Thomas, one of the twelve, called Didymus, was not with them when Jesus came.
The other disciples therefore said unto him, We have seen the Lord.
But he said unto them, Except I shall see in his hands the print of the nails,
and put my finger into the print of the nails, and thrust my hand into his side,
I will not believe.

And after eight days again his disciples were within, and Thomas with them:
then came Jesus, the doors being shut, and stood in the midst, and said,
Peace be unto you.

Then saith he to Thomas, Reach hither thy finger, and behold my hands;
and reach hither thy hand, and thrust it into my side: and be not faithless,
but believing.

And Thomas answered and said unto him, My Lord and my God.
        """)

        # Sermon on the Mount
        (self.teachings_dir / "sermon_on_mount.txt").write_text("""
THE SERMON ON THE MOUNT
Blessed are the poor in spirit: for theirs is the kingdom of heaven.
Blessed are they that mourn: for they shall be comforted.
Blessed are the meek: for they shall inherit the earth.
Love your enemies, bless them that curse you.
        """)

        # Daily life
        (self.daily_dir / "companions.txt").write_text("""
THE TWELVE DISCIPLES
Simon Peter, Andrew his brother, James and John the sons of Zebedee,
Philip, Bartholomew, Matthew the tax collector, Thomas called Didymus,
James the son of Alphaeus, Thaddaeus, Simon the Zealot, and Judas Iscariot.

They followed Jesus throughout his ministry, witnessing miracles and teachings.
        """)

    def test_full_resurrection_workflow(self):
        """Test complete resurrection workflow from indexing to querying."""
        # Create consciousness
        consciousness = ResurrectionConsciousness(
            figure_name="jesus_christ",
            bundle_dir=Path(self.temp_dir) / "jesus_bundle"
        )

        # Index Gospel data
        results = consciousness.index_texts(self.data_dir)

        # Verify indexing succeeded
        self.assertNotIn("error", results)
        self.assertGreater(results["total_documents"], 0)

        # Test various queries
        queries_and_expectations = [
            ("Who was Thomas?", ["Thomas", "Didymus", "twelve"]),
            ("Tell me about the disciples", ["disciples", "Simon", "Peter"]),
            ("What are the Beatitudes?", ["Blessed", "kingdom", "heaven"]),
            ("Thomas the doubter", ["Thomas", "believe", "Lord"])
        ]

        for query, expected_words in queries_and_expectations:
            result = consciousness.query(query, use_llm=False)

            # Check we got sources
            self.assertGreater(len(result["sources"]), 0,
                             f"Should find sources for: {query}")

            # Check relevant content is found
            all_source_text = " ".join(s["text"] for s in result["sources"])
            relevant_found = any(word in all_source_text for word in expected_words)
            self.assertTrue(relevant_found,
                          f"Should find relevant content for: {query}")

    def test_resurrection_bot_integration(self):
        """Test the ResurrectionBot with actual data."""
        # Set up data in expected location
        resurrection_data = Path("resurrections/data/jesus_christ")
        if not resurrection_data.exists():
            resurrection_data.mkdir(parents=True)
            # Copy test data
            shutil.copytree(self.data_dir, resurrection_data, dirs_exist_ok=True)

        try:
            # Create bot
            bot = ResurrectionBot("jesus_christ")

            # Test responses
            response = bot.respond("Who was Thomas?")
            self.assertIsNotNone(response)
            self.assertNotEqual(response, "I cannot find wisdom on this matter in my texts.")

            # Clean up
            if resurrection_data.exists():
                shutil.rmtree(resurrection_data.parent.parent)
        except Exception as e:
            # Clean up even on failure
            if resurrection_data.exists():
                shutil.rmtree(resurrection_data.parent.parent)
            raise e


class TestResurrectionRobustness(unittest.TestCase):
    """Test error handling and edge cases."""

    def test_empty_query(self):
        """Test handling of empty queries."""
        consciousness = ResurrectionConsciousness("test")
        result = consciousness.query("", use_llm=False)
        self.assertIn("response", result)

    def test_very_long_query(self):
        """Test handling of very long queries."""
        consciousness = ResurrectionConsciousness("test")
        long_query = "Thomas " * 1000
        result = consciousness.query(long_query, use_llm=False)
        self.assertIn("response", result)

    def test_special_characters_in_query(self):
        """Test queries with special characters."""
        consciousness = ResurrectionConsciousness("test")
        queries = [
            "Who was Thomas???",
            "Thomas & the disciples",
            "Tell me about @Thomas",
            "Thomas's doubt"
        ]

        for query in queries:
            result = consciousness.query(query, use_llm=False)
            self.assertIn("response", result)

    def test_concurrent_resurrections(self):
        """Test multiple resurrections don't interfere."""
        jesus = ResurrectionConsciousness("jesus")
        buddha = ResurrectionConsciousness("buddha")

        # Different collections
        self.assertNotEqual(
            jesus.vector_store.collection_name,
            buddha.vector_store.collection_name
        )

        # Different directories
        self.assertNotEqual(jesus.bundle_dir, buddha.bundle_dir)


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResurrectionUnitTests))
    suite.addTests(loader.loadTestsFromTestCase(TestResurrectionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestResurrectionRobustness))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == "__main__":
    # Check environment
    print("\n" + "="*70)
    print("RESURRECTION SYSTEM TEST SUITE")
    print("="*70)

    if 'VIRTUAL_ENV' in os.environ:
        print("✓ Virtual environment active")
    else:
        print("⚠️  Warning: Virtual environment not active")
        print("  Activate with: source venv/bin/activate")

    print("\nRunning tests...")
    print("-"*70)

    success = run_tests()
    sys.exit(0 if success else 1)