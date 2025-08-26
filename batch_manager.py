#!/usr/bin/env python3
"""
Batch Manager Module for FlexXray Transcripts

This module handles batching, token handling, and retries for OpenAI operations.
Extracted from perspective_analysis.py to provide focused batch processing functionality.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 20
    batch_delay: float = 1.5
    failure_delay: float = 3.0
    max_retries: int = 3
    enable_batch_processing: bool = True
    max_quotes_per_perspective: int = 200


class BatchManager:
    """Handles batching, token handling, and retries for OpenAI operations."""
    
    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize the batch manager with configuration."""
        self.config = config or BatchConfig()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.batch_processing_stats = {
            "total_batches_processed": 0,
            "successful_batches": 0,
            "failed_batches": 0,
            "total_processing_time": 0.0,
            "average_batch_time": 0.0,
        }

    def configure_batch_processing(
        self,
        batch_size: Optional[int] = None,
        batch_delay: Optional[float] = None,
        failure_delay: Optional[float] = None,
        max_retries: Optional[int] = None,
        max_quotes: Optional[int] = None,
        enable: Optional[bool] = None,
    ):
        """Configure batch processing parameters."""
        if batch_size is not None:
            self.config.batch_size = max(5, min(50, batch_size))  # Ensure reasonable range
            self.logger.info(f"Batch size set to {self.config.batch_size}")

        if batch_delay is not None:
            self.config.batch_delay = max(0.5, min(5.0, batch_delay))  # Ensure reasonable range
            self.logger.info(f"Batch delay set to {self.config.batch_delay}s")

        if failure_delay is not None:
            self.config.failure_delay = max(1.0, min(10.0, failure_delay))  # Ensure reasonable range
            self.logger.info(f"Failure delay set to {self.config.failure_delay}s")

        if max_retries is not None:
            self.config.max_retries = max(1, min(10, max_retries))  # Ensure reasonable range
            self.logger.info(f"Max retries set to {self.config.max_retries}")

        if max_quotes is not None:
            self.config.max_quotes_per_perspective = max(50, min(500, max_quotes))  # Ensure reasonable range
            self.logger.info(f"Max quotes per perspective set to {self.config.max_quotes_per_perspective}")

        if enable is not None:
            self.config.enable_batch_processing = enable
            status = "enabled" if enable else "disabled"
            self.logger.info(f"Batch processing {status}")

        self.logger.info(
            f"Batch processing configuration: size={self.config.batch_size}, "
            f"delay={self.config.batch_delay}s, failure_delay={self.config.failure_delay}s, "
            f"max_retries={self.config.max_retries}, max_quotes={self.config.max_quotes_per_perspective}"
        )

    def process_in_batches(
        self,
        items: List[Any],
        process_function: Callable[[List[Any], Dict[str, Any]], List[Any]],
        context: Optional[Dict[str, Any]] = None,
        batch_size: Optional[int] = None,
    ) -> List[Any]:
        """Process items in batches using the provided function."""
        if not items:
            return []

        if not self.config.enable_batch_processing:
            self.logger.info("Batch processing disabled, processing all items at once")
            return process_function(items, context or {})

        # Use configured batch size if not specified
        effective_batch_size = batch_size or self.config.batch_size
        effective_batch_size = max(5, min(50, effective_batch_size))  # Ensure reasonable range

        self.logger.info(
            f"Starting batch processing for {len(items)} items with batch size {effective_batch_size}"
        )

        all_results = []
        total_batches = (len(items) + effective_batch_size - 1) // effective_batch_size
        start_time = time.time()

        # Process items in batches
        for i in range(0, len(items), effective_batch_size):
            batch_num = i // effective_batch_size + 1
            batch = items[i : i + effective_batch_size]

            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

            batch_start_time = time.time()
            batch_success = False
            retry_count = 0

            # Retry logic for failed batches
            while not batch_success and retry_count < self.config.max_retries:
                try:
                    # Process this batch
                    batch_results = process_function(batch, context or {})

                    if batch_results:
                        all_results.extend(batch_results)
                        batch_success = True
                        self.batch_processing_stats["successful_batches"] += 1
                        
                        batch_duration = time.time() - batch_start_time
                        self.logger.info(
                            f"✅ Batch {batch_num} completed successfully in {batch_duration:.2f}s - "
                            f"{len(batch_results)} results"
                        )
                    else:
                        self.logger.warning(f"⚠️ Batch {batch_num} returned no results")
                        batch_success = True  # Consider empty results as success

                except Exception as e:
                    retry_count += 1
                    self.logger.error(f"❌ Batch {batch_num} failed (attempt {retry_count}): {e}")
                    
                    if retry_count < self.config.max_retries:
                        retry_delay = self.config.failure_delay * retry_count  # Exponential backoff
                        self.logger.info(f"Retrying batch {batch_num} in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        self.logger.error(f"Batch {batch_num} failed after {self.config.max_retries} attempts")
                        self.batch_processing_stats["failed_batches"] += 1
                        
                        # Add failed items with error information
                        failed_results = self._create_failed_results(batch, str(e))
                        all_results.extend(failed_results)

            # Add delay between batches to avoid rate limiting (except for last batch)
            if i + effective_batch_size < len(items):
                delay = self.config.batch_delay
                self.logger.info(f"Waiting {delay}s before next batch...")
                time.sleep(delay)

        # Update statistics
        total_duration = time.time() - start_time
        self.batch_processing_stats["total_batches_processed"] += total_batches
        self.batch_processing_stats["total_processing_time"] += total_duration
        
        if total_batches > 0:
            self.batch_processing_stats["average_batch_time"] = (
                self.batch_processing_stats["total_processing_time"] / 
                self.batch_processing_stats["total_batches_processed"]
            )

        self.logger.info(
            f"Batch processing completed: {len(all_results)} total results in {total_duration:.2f}s"
        )
        return all_results

    def _create_failed_results(self, items: List[Any], error_message: str) -> List[Dict[str, Any]]:
        """Create result objects for failed items."""
        failed_results = []
        
        for item in items:
            if isinstance(item, dict):
                failed_result = item.copy()
                failed_result["processing_status"] = "failed"
                failed_result["error_message"] = error_message
                failed_result["retry_count"] = self.config.max_retries
            else:
                failed_result = {
                    "item": item,
                    "processing_status": "failed",
                    "error_message": error_message,
                    "retry_count": self.config.max_retries,
                }
            
            failed_results.append(failed_result)
        
        return failed_results

    def get_batch_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about batch processing performance."""
        stats = {
            "configuration": {
                "batch_size": self.config.batch_size,
                "batch_delay": self.config.batch_delay,
                "failure_delay": self.config.failure_delay,
                "max_retries": self.config.max_retries,
                "max_quotes_per_perspective": self.config.max_quotes_per_perspective,
                "batch_processing_enabled": self.config.enable_batch_processing,
            },
            "performance": {
                "total_batches_processed": self.batch_processing_stats["total_batches_processed"],
                "successful_batches": self.batch_processing_stats["successful_batches"],
                "failed_batches": self.batch_processing_stats["failed_batches"],
                "success_rate": self._calculate_success_rate(),
                "total_processing_time": self.batch_processing_stats["total_processing_time"],
                "average_batch_time": self.batch_processing_stats["average_batch_time"],
                "estimated_quotes_per_minute": self._estimate_quotes_per_minute(),
                "estimated_batch_processing_time": self._estimate_batch_processing_time,
            },
            "optimization_tips": self._get_optimization_tips(),
        }

        return stats

    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of batch processing."""
        total_batches = self.batch_processing_stats["total_batches_processed"]
        successful_batches = self.batch_processing_stats["successful_batches"]
        
        if total_batches == 0:
            return 0.0
        
        return (successful_batches / total_batches) * 100

    def _estimate_quotes_per_minute(self) -> int:
        """Estimate quotes that can be processed per minute."""
        if self.config.batch_delay <= 0:
            return 0
        
        # Rough estimate based on batch size and delay
        quotes_per_batch = self.config.batch_size
        time_per_batch = self.config.batch_delay + 0.5  # Add processing time estimate
        
        quotes_per_second = quotes_per_batch / time_per_batch
        return int(quotes_per_second * 60)

    def _estimate_batch_processing_time(self, quote_count: int) -> float:
        """Estimate time needed to process a given number of quotes."""
        if self.config.batch_size <= 0:
            return 0.0
        
        num_batches = (quote_count + self.config.batch_size - 1) // self.config.batch_size
        time_per_batch = self.config.batch_delay + 0.5  # Add processing time estimate
        
        return num_batches * time_per_batch

    def _get_optimization_tips(self) -> List[str]:
        """Get optimization tips based on current configuration."""
        tips = []
        
        if self.config.batch_delay > 2.0:
            tips.append("Consider decreasing batch_delay for faster processing (if rate limits allow)")
        
        if self.config.batch_size < 15:
            tips.append("Consider increasing batch_size for more efficient processing (if API allows)")
        
        if self.config.max_retries < 3:
            tips.append("Consider increasing max_retries for better reliability")
        
        if self.config.failure_delay < 2.0:
            tips.append("Consider increasing failure_delay to avoid cascading failures")
        
        if not tips:
            tips.append("Current configuration appears well-optimized")
        
        return tips

    def get_recommended_batch_size(self) -> int:
        """Get recommended batch size based on current configuration."""
        # Conservative recommendation based on typical API limits
        if self.config.batch_delay <= 1.0:
            return min(15, self.config.batch_size)  # Smaller batches for faster processing
        elif self.config.batch_delay <= 2.0:
            return min(20, self.config.batch_size)  # Medium batches for balanced processing
        else:
            return min(25, self.config.batch_size)  # Larger batches for slower processing

    def reset_statistics(self):
        """Reset batch processing statistics."""
        self.batch_processing_stats = {
            "total_batches_processed": 0,
            "successful_batches": 0,
            "failed_batches": 0,
            "total_processing_time": 0.0,
            "average_batch_time": 0.0,
        }
        self.logger.info("Batch processing statistics reset")

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current batch processing configuration."""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
        }
        
        # Check batch size
        if self.config.batch_size < 5:
            validation_results["warnings"].append("Batch size is very small, may impact efficiency")
        elif self.config.batch_size > 50:
            validation_results["warnings"].append("Batch size is very large, may hit API limits")
        
        # Check delays
        if self.config.batch_delay < 0.5:
            validation_results["warnings"].append("Batch delay is very short, may hit rate limits")
        elif self.config.batch_delay > 5.0:
            validation_results["warnings"].append("Batch delay is very long, may impact performance")
        
        # Check retries
        if self.config.max_retries < 1:
            validation_results["errors"].append("Max retries must be at least 1")
            validation_results["valid"] = False
        elif self.config.max_retries > 10:
            validation_results["warnings"].append("Max retries is very high, may cause long delays")
        
        # Check quote limits
        if self.config.max_quotes_per_perspective < 50:
            validation_results["warnings"].append("Max quotes per perspective is low, may limit coverage")
        elif self.config.max_quotes_per_perspective > 500:
            validation_results["warnings"].append("Max quotes per perspective is very high, may impact performance")
        
        return validation_results
