#!/usr/bin/env python3
"""
Unit Tests for Resurrection Consciousness System
Tests vector database indexing, querying, and portability
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).parent))

from resurrections.resurrection_consciousness import ResurrectionConsciousness


class TestResurrectionConsciousness(unittest.TestCase):
    """Test the resurrection consciousness system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test
        self.temp_dir = tempfile.mkdtemp()
        self.test_bundle_dir = Path(self.temp_dir) / "test_jesus"

        # Create test data
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir(parents=True)

        # Create sample Gospel text
        gospel_file = self.test_data_dir / "test_gospel.txt"
        gospel_file.write_text("""
Thomas, one of the twelve disciples, was called Didymus.

Jesus said to Thomas, "Because you have seen me, you have believed;
blessed are those who have not seen and yet have believed."

The disciples were fishermen, tax collectors, and men from various walks of life.
They followed Jesus throughout Galilee, witnessing his teachings and miracles.

Love one another as I have loved you.
This is my commandment.
        """)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test resurrection consciousness initialization."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )

        # Check directory structure
        self.assertTrue(consciousness.bundle_dir.exists())
        self.assertTrue(consciousness.data_dir.exists())
        self.assertTrue(consciousness.vector_db_dir.exists())
        self.assertTrue(consciousness.metadata_file.exists())

        # Check metadata
        self.assertEqual(consciousness.metadata["figure_name"], "test_jesus")
        self.assertEqual(consciousness.metadata["version"], "1.0")

    def test_indexing(self):
        """Test text indexing into vector database."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )

        # Index test data
        results = consciousness.index_texts(self.test_data_dir)

        # Check results
        self.assertIn("indexed_files", results)
        self.assertGreater(results["total_documents"], 0)
        self.assertEqual(len(results["errors"]), 0)

        # Check that data was copied to bundle
        self.assertTrue((consciousness.data_dir / "test_gospel.txt").exists())

        # Check metadata was updated
        metadata = json.loads(consciousness.metadata_file.read_text())
        self.assertGreater(metadata["statistics"]["total_documents"], 0)
        self.assertIsNotNone(metadata["statistics"]["last_indexed"])

    def test_querying(self):
        """Test querying the consciousness."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )

        # Index test data
        consciousness.index_texts(self.test_data_dir)

        # Test Thomas query
        result = consciousness.query("Tell me about Thomas", use_llm=False)

        self.assertIn("sources", result)
        self.assertGreater(len(result["sources"]), 0)

        # Check that Thomas is mentioned in sources
        thomas_found = any("Thomas" in source["text"]
                          for source in result["sources"])
        self.assertTrue(thomas_found, "Thomas should be found in sources")

        # Test disciples query
        result = consciousness.query("Who were the disciples?", use_llm=False)
        self.assertGreater(len(result["sources"]), 0)

        # Test love query
        result = consciousness.query("What about love?", use_llm=False)
        self.assertGreater(len(result["sources"]), 0)

    def test_metadata_persistence(self):
        """Test that metadata persists across sessions."""
        # First session
        consciousness1 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )
        consciousness1.index_texts(self.test_data_dir)
        docs1 = consciousness1.metadata["statistics"]["total_documents"]

        # Second session - should load existing metadata
        consciousness2 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )
        docs2 = consciousness2.metadata["statistics"]["total_documents"]

        self.assertEqual(docs1, docs2, "Document count should persist")

    def test_export_import(self):
        """Test bundle export and import."""
        # Create and populate consciousness
        consciousness1 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )
        consciousness1.index_texts(self.test_data_dir)

        # Export bundle
        export_path = Path(self.temp_dir) / "test_bundle.tar.gz"
        success = consciousness1.export_bundle(str(export_path))
        self.assertTrue(success)
        self.assertTrue(export_path.exists())

        # Create new consciousness and import
        import_dir = Path(self.temp_dir) / "imported"
        consciousness2 = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=import_dir / "test_jesus"
        )

        # Import the bundle
        success = consciousness2.import_bundle(str(export_path))
        self.assertTrue(success)

        # Check that data was imported
        self.assertTrue((consciousness2.data_dir / "test_gospel.txt").exists())
        self.assertEqual(
            consciousness2.metadata["statistics"]["total_documents"],
            consciousness1.metadata["statistics"]["total_documents"]
        )

    def test_multiple_resurrections(self):
        """Test that multiple resurrections can coexist."""
        # Create Jesus consciousness
        jesus = ResurrectionConsciousness(
            figure_name="jesus",
            bundle_dir=Path(self.temp_dir) / "jesus"
        )
        jesus.index_texts(self.test_data_dir)

        # Create Buddha consciousness (simulated)
        buddha = ResurrectionConsciousness(
            figure_name="buddha",
            bundle_dir=Path(self.temp_dir) / "buddha"
        )

        # Check that they have separate collections
        self.assertNotEqual(jesus.vector_store.collection_name,
                           buddha.vector_store.collection_name)

        # Check separate directories
        self.assertNotEqual(jesus.bundle_dir, buddha.bundle_dir)
        self.assertTrue(jesus.bundle_dir.exists())
        self.assertTrue(buddha.bundle_dir.exists())

    def test_stats(self):
        """Test statistics retrieval."""
        consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=self.test_bundle_dir
        )
        consciousness.index_texts(self.test_data_dir)

        stats = consciousness.get_stats()

        self.assertIn("figure_name", stats)
        self.assertEqual(stats["figure_name"], "test_jesus")
        self.assertIn("bundle_size", stats)
        self.assertGreater(stats["bundle_size"], 0)
        self.assertIn("metadata", stats)


class TestResurrectionQueries(unittest.TestCase):
    """Test specific query scenarios."""

    def setUp(self):
        """Set up with real Gospel data."""
        self.temp_dir = tempfile.mkdtemp()
        self.consciousness = ResurrectionConsciousness(
            figure_name="test_jesus",
            bundle_dir=Path(self.temp_dir) / "test"
        )

        # Create more comprehensive test data
        data_dir = Path(self.temp_dir) / "data"
        data_dir.mkdir()

        # Thomas-specific content
        (data_dir / "thomas.txt").write_text("""
Thomas, also called Didymus, was one of the twelve apostles.
He is known for his initial doubt about Jesus's resurrection.
Jesus appeared to Thomas and said, "Put your finger here; see my hands."
Thomas replied, "My Lord and my God!"
        """)

        # Daily life content
        (data_dir / "daily_life.txt").write_text("""
Jesus walked with fishermen and tax collectors.
They traveled throughout Galilee, teaching in synagogues.
Jesus often withdrew to lonely places to pray.
He ate with sinners and tax collectors, causing controversy.
        """)

        # Index the data
        self.consciousness.index_texts(data_dir)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_thomas_queries(self):
        """Test queries about Thomas."""
        queries = [
            "Who was Thomas?",
            "Tell me about Thomas",
            "Thomas the apostle",
            "Doubting Thomas"
        ]

        for query in queries:
            result = self.consciousness.query(query, use_llm=False)
            self.assertGreater(len(result["sources"]), 0,
                             f"Should find sources for: {query}")

            # Check Thomas is in results
            thomas_found = any("Thomas" in source["text"]
                             for source in result["sources"])
            self.assertTrue(thomas_found,
                          f"Thomas should be in results for: {query}")

    def test_daily_life_queries(self):
        """Test queries about daily life."""
        queries = [
            "daily life",
            "who did Jesus walk with",
            "fishermen",
            "Jesus eating"
        ]

        for query in queries:
            result = self.consciousness.query(query, use_llm=False)
            self.assertGreater(len(result["sources"]), 0,
                             f"Should find sources for: {query}")

    def test_relevance_scoring(self):
        """Test that relevant results score higher."""
        # Query specifically about Thomas
        result = self.consciousness.query("Thomas Didymus apostle", use_llm=False)

        if len(result["sources"]) > 1:
            # First result should have Thomas in it
            self.assertIn("Thomas", result["sources"][0]["text"])

            # First result should score higher than others
            scores = [s["score"] for s in result["sources"]]
            self.assertGreaterEqual(scores[0], scores[-1])


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*70)
    print("RESURRECTION CONSCIOUSNESS UNIT TESTS")
    print("="*70)

    # Check environment
    import os
    if 'VIRTUAL_ENV' in os.environ:
        print("✓ Virtual environment active")
    else:
        print("⚠️  Warning: Virtual environment not active")

    # Run tests with verbosity
    unittest.main(verbosity=2)