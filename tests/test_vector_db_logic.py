#!/usr/bin/env python3
"""
Unit tests for vector database logic in vector_database.py

This module tests the complex vector database operations that handle:
- ChromaDB initialization and management
- Quote storage and retrieval
- Semantic search functionality
- Metadata management and filtering
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from typing import List, Dict, Any
import tempfile
import shutil
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the classes we want to test
from vector_database import (
    VectorDatabaseManager,
    VectorDatabaseError,
    ChromaDBConnectionError,
    ChromaDBInitializationError,
    QuoteStorageError,
    SearchError,
    DataValidationError,
)


class TestVectorDatabaseLogic(unittest.TestCase):
    """Test vector database logic."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a unique test directory for each test to ensure isolation
        self.test_dir = tempfile.mkdtemp(prefix="test_chroma_")

        # Ensure the directory is empty
        for file in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Create sample quotes for testing
        self.sample_quotes = [
            {
                "text": "FlexXray provides excellent foreign material detection services.",
                "speaker_role": "expert",
                "transcript_name": "Test Transcript 1",
                "position": 1,
                "has_insight": True,
                "metadata": {"length": 100, "word_count": 15},
            },
            {
                "text": "The turnaround time is very fast.",
                "speaker_role": "expert",
                "transcript_name": "Test Transcript 2",
                "position": 2,
                "has_insight": True,
                "metadata": {"length": 80, "word_count": 12},
            },
        ]

    def tearDown(self):
        """Clean up after each test."""
        # Remove the test directory completely
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_mock_chroma_components(self):
        """Helper method to create consistent mock ChromaDB components."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_quotes_collection = Mock()

        # Reset mocks to ensure clean state
        mock_client.reset_mock()
        mock_collection.reset_mock()
        mock_quotes_collection.reset_mock()

        # Set up side effects for collection creation
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,
            mock_quotes_collection,
        ]

        return mock_client, mock_collection, mock_quotes_collection

    def _create_mock_search_results(self, num_results: int = 2):
        """Helper method to create consistent mock search results."""
        return {
            "ids": [["quote_1", "quote_2"][:num_results]],
            "documents": [["Quote text 1", "Quote text 2"][:num_results]],
            "metadatas": [
                [
                    {
                        "speaker_role": "expert",
                        "transcript_name": f"Test {i}",
                        "has_insight": True,
                    },
                    {
                        "speaker_role": "expert",
                        "transcript_name": f"Test {i}",
                        "has_insight": True,
                    },
                ][:num_results]
                for i in range(1, num_results + 1)
            ],
            "distances": [[0.1, 0.3][:num_results]],
        }

    @patch("vector_database.chromadb")
    def test_chromadb_initialization_success(self, mock_chroma):
        """Test successful ChromaDB initialization."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Test initialization
        db_manager = VectorDatabaseManager(self.test_dir)

        self.assertIsNotNone(db_manager.chroma_client)
        self.assertIsNotNone(db_manager.collection)
        self.assertIsNotNone(db_manager.quotes_collection)

    @patch("vector_database.chromadb")
    def test_chromadb_initialization_failure(self, mock_chroma):
        """Test ChromaDB initialization failure handling."""
        # Mock ChromaDB initialization failure
        mock_chroma.PersistentClient.side_effect = Exception("Connection failed")

        # Test initialization with failure
        with self.assertRaises(ChromaDBInitializationError):
            VectorDatabaseManager(self.test_dir)

    @patch("vector_database.chromadb")
    def test_quote_storage_success(self, mock_chroma):
        """Test successful quote storage."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test quote storage
        result = db_manager.store_quotes_in_vector_db(self.sample_quotes)

        self.assertTrue(result)
        # Verify add was called on quotes collection
        mock_quotes_collection.add.assert_called_once()

    @patch("vector_database.chromadb")
    def test_quote_storage_failure(self, mock_chroma):
        """Test quote storage failure handling."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock storage failure
        mock_quotes_collection.add.side_effect = Exception("Storage failed")

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test quote storage failure
        with self.assertRaises(QuoteStorageError):
            db_manager.store_quotes_in_vector_db(self.sample_quotes)

    @patch("vector_database.chromadb")
    def test_quote_storage_validation_errors(self, mock_chroma):
        """Test quote storage validation error handling."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test invalid input types
        with self.assertRaises(DataValidationError):
            db_manager.store_quotes_in_vector_db("not a list")

        with self.assertRaises(DataValidationError):
            db_manager.store_quotes_in_vector_db(self.sample_quotes, batch_size=0)

        # Test invalid quote structure
        invalid_quotes = [{"invalid": "quote"}]
        with self.assertRaises(DataValidationError):
            db_manager.store_quotes_in_vector_db(invalid_quotes)

    @patch("vector_database.chromadb")
    def test_semantic_search_functionality(self, mock_chroma):
        """Test semantic search functionality."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock search results
        mock_results = self._create_mock_search_results(2)
        mock_quotes_collection.query.return_value = mock_results

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test semantic search
        results = db_manager.semantic_search_quotes("market leadership", n_results=5)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["text"], "Quote text 1")
        self.assertEqual(results[0]["metadata"]["speaker_role"], "expert")
        self.assertEqual(results[0]["distance"], 0.1)

    @patch("vector_database.chromadb")
    def test_semantic_search_validation_errors(self, mock_chroma):
        """Test semantic search validation error handling."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test invalid query
        with self.assertRaises(DataValidationError):
            db_manager.semantic_search_quotes("", n_results=5)

        with self.assertRaises(DataValidationError):
            db_manager.semantic_search_quotes(None, n_results=5)

        # Test invalid n_results
        with self.assertRaises(DataValidationError):
            db_manager.semantic_search_quotes("test", n_results=0)

        with self.assertRaises(DataValidationError):
            db_manager.semantic_search_quotes("test", n_results=-1)

        # Test invalid filter_metadata
        with self.assertRaises(DataValidationError):
            db_manager.semantic_search_quotes(
                "test", n_results=5, filter_metadata="not a dict"
            )

    @patch("vector_database.chromadb")
    def test_semantic_search_failure(self, mock_chroma):
        """Test semantic search failure handling."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock search failure
        mock_quotes_collection.query.side_effect = Exception("Search failed")

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test search error handling
        with self.assertRaises(SearchError):
            db_manager.semantic_search_quotes("test query")

    @patch("vector_database.chromadb")
    def test_speaker_filtered_search(self, mock_chroma):
        """Test speaker role filtered search."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock search results
        mock_results = self._create_mock_search_results(1)
        mock_quotes_collection.query.return_value = mock_results

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test speaker filtered search
        results = db_manager.search_quotes_with_speaker_filter(
            "market position", speaker_role="expert", n_results=10
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["speaker_role"], "expert")

    @patch("vector_database.chromadb")
    def test_metadata_filtering(self, mock_chroma):
        """Test metadata-based filtering."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock search results
        mock_results = self._create_mock_search_results(1)
        mock_quotes_collection.query.return_value = mock_results

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test metadata filtering
        filter_metadata = {"has_insight": True}
        results = db_manager.semantic_search_quotes(
            "insight", n_results=5, filter_metadata=filter_metadata
        )

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["metadata"]["has_insight"])

    @patch("vector_database.chromadb")
    def test_batch_processing(self, mock_chroma):
        """Test batch processing of quotes."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Create many quotes for batch testing
        many_quotes = []
        for i in range(150):  # More than batch size of 100
            many_quotes.append(
                {
                    "text": f"Quote {i}",
                    "speaker_role": "expert",
                    "transcript_name": f"Transcript {i}",
                    "position": i,
                    "has_insight": True,
                    "metadata": {"length": 50, "word_count": 8},
                }
            )

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test batch storage
        result = db_manager.store_quotes_in_vector_db(many_quotes, batch_size=100)

        self.assertTrue(result)
        # Should be called twice due to batch size
        self.assertEqual(mock_quotes_collection.add.call_count, 2)

    @patch("vector_database.chromadb")
    def test_database_statistics(self, mock_chroma):
        """Test database statistics functionality."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Set up the mock to return a count
        mock_quotes_collection.count.return_value = 25

        # Mock the list_collections method to return a proper collection list
        mock_collection1 = Mock()
        mock_collection1.name = "transcript_chunks"
        mock_collection2 = Mock()
        mock_collection2.name = "flexray_quotes"
        mock_client.list_collections.return_value = [mock_collection1, mock_collection2]

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test database statistics
        stats = db_manager.get_vector_database_stats()

        # Verify basic stats
        self.assertIn("available", stats)
        self.assertIn("total_quotes", stats)
        self.assertIn("collections", stats)

        # Verify the stats values
        self.assertTrue(stats["available"])
        self.assertEqual(stats["total_quotes"], 25)
        self.assertIsInstance(stats["collections"], list)
        self.assertEqual(len(stats["collections"]), 2)

    @patch("vector_database.chromadb")
    def test_database_clearing(self, mock_chroma):
        """Test database clearing functionality."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        # Set up the mock to return a count
        mock_quotes_collection.count.return_value = 0

        # Mock the collection recreation after deletion
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,  # First call for transcript_chunks
            mock_quotes_collection,  # Second call for flexray_quotes
            mock_quotes_collection,  # Third call for recreation after clearing
        ]

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test database clearing
        result = db_manager.clear_vector_database()

        # Verify the result
        self.assertTrue(result)

        # Verify that delete_collection was called on the client (not the collection)
        mock_client.delete_collection.assert_called_once_with(name="flexray_quotes")

    @patch("vector_database.chromadb")
    def test_quote_id_generation(self, mock_chroma):
        """Test quote ID generation logic."""
        mock_client, mock_collection, mock_quotes_collection = (
            self._create_mock_chroma_components()
        )
        mock_chroma.PersistentClient.return_value = mock_client

        db_manager = VectorDatabaseManager(self.test_dir)

        # Test ID generation
        quote = {
            "text": "Test quote",
            "transcript_name": "Test Transcript",
            "position": 1,
        }

        quote_id = db_manager._generate_quote_id(quote)

        # Should be a string and consistent for same input
        self.assertIsInstance(quote_id, str)
        self.assertEqual(db_manager._generate_quote_id(quote), quote_id)

    @patch("vector_database.chromadb")
    def test_chromadb_unavailable_behavior(self, mock_chroma):
        """Test behavior when ChromaDB is not available."""
        # Mock ChromaDB as unavailable
        mock_chroma.PersistentClient.side_effect = ImportError("ChromaDB not available")

        # Test initialization with failure
        with self.assertRaises(ChromaDBInitializationError):
            VectorDatabaseManager(self.test_dir)


class TestVectorDatabaseIntegration(unittest.TestCase):
    """Test integration aspects of vector database."""

    def test_chromadb_unavailable_fallback(self):
        """Test behavior when ChromaDB is not available."""
        with patch("vector_database.CHROMA_AVAILABLE", False):
            db_manager = VectorDatabaseManager("./test_db")

            # Should gracefully handle missing ChromaDB
            self.assertIsNone(db_manager.chroma_client)
            self.assertIsNone(db_manager.collection)

            # Operations should fail gracefully with proper exceptions
            with self.assertRaises(QuoteStorageError):
                db_manager.store_quotes_in_vector_db([])

            with self.assertRaises(SearchError):
                db_manager.semantic_search_quotes("test")


if __name__ == "__main__":
    unittest.main()
