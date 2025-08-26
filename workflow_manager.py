#!/usr/bin/env python3
"""
Workflow Manager for FlexXray Quote Analysis

This module handles high-level workflow orchestration including:
- High-level pipelines (extraction → enrichment → analysis → export)
- Batch scheduling and monitoring
- Error reporting and recovery
- Workflow state management
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum

# Import our modular components
from quote_analysis_core import QuoteAnalysisTool
from quote_extraction import QuoteExtractor
from vector_database import VectorDatabaseManager
from perspective_analysis import PerspectiveAnalyzer
from export_utils import ExportManager
from prompt_config import get_prompt_config
from quote_processing import QuoteProcessor
from summary_generation import SummaryGenerator
from data_structures import DataStructureManager
from settings import get_settings


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(Enum):
    """Pipeline execution stages."""
    EXTRACTION = "extraction"
    ENRICHMENT = "enrichment"
    ANALYSIS = "analysis"
    EXPORT = "export"


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""
    max_quotes_for_analysis: int = 50
    max_tokens_per_quote: int = 200
    enable_token_logging: bool = True
    enable_batch_processing: bool = True
    batch_size: int = 20
    batch_delay: float = 1.5
    max_retries: int = 3
    timeout_minutes: int = 60
    enable_monitoring: bool = True
    log_workflow_progress: bool = True


@dataclass
class WorkflowState:
    """Current state of workflow execution."""
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_stage: Optional[PipelineStage] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    current_operation: str = ""
    error_message: Optional[str] = None
    retry_count: int = 0
    stage_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """Manages high-level workflow orchestration for quote analysis."""
    
    def __init__(self, api_key: str, config: Optional[WorkflowConfig] = None):
        """Initialize the workflow manager."""
        self.api_key = api_key
        self.config = config or WorkflowConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize workflow state
        self.workflow_state = WorkflowState()
        
        # Initialize modular components
        self._initialize_components()
        
        # Define pipeline stages
        self.pipeline_stages = [
            PipelineStage.EXTRACTION,
            PipelineStage.ENRICHMENT,
            PipelineStage.ANALYSIS,
            PipelineStage.EXPORT
        ]
        
        # Pipeline stage weights for progress calculation
        self.stage_weights = {
            PipelineStage.EXTRACTION: 0.2,
            PipelineStage.ENRICHMENT: 0.2,
            PipelineStage.ANALYSIS: 0.4,
            PipelineStage.EXPORT: 0.2
        }
        
        self.logger.info("Workflow Manager initialized successfully")

    def _initialize_components(self):
        """Initialize all required components."""
        try:
            # Initialize core components
            self.quote_extractor = QuoteExtractor(
                min_quote_length=10,
                max_quote_length=500
            )
            
            self.vector_db_manager = VectorDatabaseManager(
                chroma_persist_directory="./chroma_db",
                openai_api_key=self.api_key
            )
            
            self.perspective_analyzer = PerspectiveAnalyzer(api_key=self.api_key)
            self.perspective_analyzer.set_vector_db_manager(self.vector_db_manager)
            
            self.export_manager = ExportManager()
            self.quote_processor = QuoteProcessor()
            self.data_structure_manager = DataStructureManager()
            
            # Initialize summary generator
            prompt_config = get_prompt_config()
            self.summary_generator = SummaryGenerator(
                openai_client=None,  # Will be set by parent class
                prompt_config=prompt_config
            )
            
            # Define key perspectives
            self.key_perspectives = [
                "business_model",
                "growth_potential", 
                "risk_factors"
            ]
            
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize components: {e}")
            raise RuntimeError(f"Component initialization failed: {e}")

    def execute_workflow(
        self, 
        directory_path: str, 
        output_directory: str = "./outputs",
        monitor_progress: bool = True
    ) -> Dict[str, Any]:
        """Execute the complete quote analysis workflow."""
        self.logger.info(f"🚀 Starting quote analysis workflow for: {directory_path}")
        
        # Initialize workflow state
        self.workflow_state = WorkflowState(
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(),
            current_operation="Initializing workflow"
        )
        
        try:
            # Create output directory
            Path(output_directory).mkdir(parents=True, exist_ok=True)
            
            # Execute pipeline stages
            results = self._execute_pipeline(directory_path, output_directory)
            
            # Update workflow state
            self.workflow_state.status = WorkflowStatus.COMPLETED
            self.workflow_state.end_time = datetime.now()
            self.workflow_state.progress = 100.0
            self.workflow_state.current_operation = "Workflow completed successfully"
            
            self.logger.info("✅ Workflow completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            self._handle_workflow_error(str(e))
            return {}

    def _execute_pipeline(
        self, 
        directory_path: str, 
        output_directory: str
    ) -> Dict[str, Any]:
        """Execute the pipeline stages sequentially."""
        results = {}
        
        for stage in self.pipeline_stages:
            try:
                self.logger.info(f"🔄 Executing stage: {stage.value}")
                self.workflow_state.current_stage = stage
                self.workflow_state.current_operation = f"Executing {stage.value}"
                
                # Execute stage
                stage_result = self._execute_stage(stage, directory_path, output_directory, results)
                
                # Store stage result
                results[stage.value] = stage_result
                self.workflow_state.stage_results[stage.value] = stage_result
                
                # Update progress
                self._update_progress(stage)
                
                self.logger.info(f"✅ Stage {stage.value} completed successfully")
                
            except Exception as e:
                self.logger.error(f"❌ Stage {stage.value} failed: {e}")
                self._handle_stage_error(stage, str(e))
                raise
        
        return results

    def _execute_stage(
        self, 
        stage: PipelineStage, 
        directory_path: str, 
        output_directory: str,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific pipeline stage."""
        if stage == PipelineStage.EXTRACTION:
            return self._execute_extraction_stage(directory_path)
        elif stage == PipelineStage.ENRICHMENT:
            return self._execute_enrichment_stage(previous_results.get("extraction", {}))
        elif stage == PipelineStage.ANALYSIS:
            return self._execute_analysis_stage(previous_results.get("enrichment", {}))
        elif stage == PipelineStage.EXPORT:
            return self._execute_export_stage(previous_results, output_directory)
        else:
            raise ValueError(f"Unknown pipeline stage: {stage}")

    def _execute_extraction_stage(self, directory_path: str) -> Dict[str, Any]:
        """Execute the quote extraction stage."""
        self.logger.info(f"📖 Extracting quotes from: {directory_path}")
        
        # Get transcript files
        transcript_files = list(Path(directory_path).glob("*.docx"))
        if not transcript_files:
            raise ValueError(f"No transcript files found in {directory_path}")
        
        self.logger.info(f"Found {len(transcript_files)} transcript files")
        
        # Process each transcript
        all_quotes = []
        for file_path in transcript_files:
            transcript_name = file_path.stem
            self.logger.info(f"Processing: {transcript_name}")
            
            # Extract text
            text = self.quote_extractor.extract_text_from_document(str(file_path))
            if not text:
                self.logger.warning(f"No text extracted from {transcript_name}")
                continue
            
            # Extract quotes
            quotes = self.quote_extractor.extract_quotes_from_text(text, transcript_name)
            if quotes:
                all_quotes.extend(quotes)
                self.logger.info(f"Extracted {len(quotes)} quotes from {transcript_name}")
            else:
                self.logger.warning(f"No quotes extracted from {transcript_name}")
        
        if not all_quotes:
            raise ValueError("No quotes extracted from any transcripts")
        
        # Store quotes in vector database
        self.vector_db_manager.store_quotes_in_vector_db(all_quotes)
        self.logger.info(f"✅ {len(all_quotes)} quotes stored in vector database")
        
        return {
            "transcripts_processed": len(transcript_files),
            "total_quotes": len(all_quotes),
            "quotes": all_quotes,
            "transcript_names": [f.stem for f in transcript_files]
        }

    def _execute_enrichment_stage(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the quote enrichment stage."""
        self.logger.info("🔧 Enriching quotes with additional metadata")
        
        if not extraction_results or "quotes" not in extraction_results:
            raise ValueError("No quotes from extraction stage")
        
        quotes = extraction_results["quotes"]
        
        # Enrich quotes using QuoteProcessor
        enriched_quotes = self.quote_processor.enrich_quotes_for_export(quotes)
        
        # Add additional enrichment
        for quote in enriched_quotes:
            # Ensure required fields
            if "speaker_role" not in quote:
                quote["speaker_role"] = "expert"  # Default assumption
            
            # Add processing metadata
            quote["enrichment_timestamp"] = datetime.now().isoformat()
            quote["enrichment_stage"] = "completed"
        
        self.logger.info(f"✅ {len(enriched_quotes)} quotes enriched successfully")
        
        return {
            "enriched_quotes": enriched_quotes,
            "enrichment_metadata": {
                "total_quotes": len(enriched_quotes),
                "enrichment_timestamp": datetime.now().isoformat()
            }
        }

    def _execute_analysis_stage(self, enrichment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the analysis stage."""
        self.logger.info("🧠 Analyzing quotes from different business perspectives")
        
        if not enrichment_results or "enriched_quotes" not in enrichment_results:
            raise ValueError("No enriched quotes from enrichment stage")
        
        enriched_quotes = enrichment_results["enriched_quotes"]
        
        # Analyze perspectives
        perspective_results = {}
        for perspective in self.key_perspectives:
            try:
                self.logger.info(f"Analyzing perspective: {perspective}")
                
                perspective_data = {
                    "title": perspective.replace("_", " ").title(),
                    "description": f"Analysis of {perspective.replace('_', ' ')} perspective",
                    "focus_areas": [perspective.replace("_", " ")]
                }
                
                analysis_result = self.perspective_analyzer.analyze_perspective_with_quotes(
                    perspective_key=perspective,
                    perspective_data=perspective_data,
                    all_quotes=enriched_quotes
                )
                
                perspective_results[perspective] = analysis_result
                self.logger.info(f"✅ {perspective} analysis completed")
                
            except Exception as e:
                self.logger.error(f"❌ Error analyzing {perspective}: {e}")
                perspective_results[perspective] = {"error": str(e)}
        
        # Generate company summary
        self.logger.info("📊 Generating company summary")
        company_summary = self._generate_company_summary(enriched_quotes)
        
        return {
            "perspective_analysis": perspective_results,
            "company_summary": company_summary,
            "analysis_metadata": {
                "perspectives_analyzed": len(perspective_results),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }

    def _execute_export_stage(
        self, 
        previous_results: Dict[str, Any], 
        output_directory: str
    ) -> Dict[str, Any]:
        """Execute the export stage."""
        self.logger.info("📤 Exporting analysis results")
        
        export_results = {}
        
        try:
            # Export company summary
            if "analysis" in previous_results and "company_summary" in previous_results["analysis"]:
                company_summary = previous_results["analysis"]["company_summary"]
                
                # Export to text
                text_file = self.export_manager.export_company_summary_page(
                    company_summary, 
                    os.path.join(output_directory, "company_summary.txt")
                )
                
                # Export to Excel
                excel_file = self.export_manager.export_company_summary_to_excel(
                    company_summary,
                    os.path.join(output_directory, "company_summary.xlsx")
                )
                
                export_results["company_summary"] = {
                    "text_file": text_file,
                    "excel_file": excel_file
                }
            
            # Export quotes
            if "enrichment" in previous_results and "enriched_quotes" in previous_results["enrichment"]:
                enriched_quotes = previous_results["enrichment"]["enriched_quotes"]
                
                quotes_file = self.export_manager.export_quotes_to_excel(
                    enriched_quotes,
                    os.path.join(output_directory, "quotes.xlsx")
                )
                
                export_results["quotes"] = {
                    "excel_file": quotes_file
                }
            
            # Export complete analysis
            analysis_file = self.export_manager.save_quote_analysis(
                previous_results,
                os.path.join(output_directory, "complete_analysis.json")
            )
            
            export_results["complete_analysis"] = {
                "json_file": analysis_file
            }
            
            self.logger.info("✅ Export stage completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Export stage failed: {e}")
            export_results["error"] = str(e)
        
        return export_results

    def _generate_company_summary(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate company summary using the summary generator."""
        if not quotes:
            return {}
        
        # Filter to expert quotes only
        expert_quotes = [q for q in quotes if q.get("speaker_role") == "expert"]
        if not expert_quotes:
            self.logger.warning("No expert quotes found for summary generation")
            return {}
        
        # Limit quotes based on configuration
        max_quotes = self.config.max_quotes_for_analysis
        if len(expert_quotes) > max_quotes:
            expert_quotes = expert_quotes[:max_quotes]
            self.logger.info(f"Limited quotes to {max_quotes} for summary generation")
        
        try:
            # Generate summary using batch processing if enabled
            if self.config.enable_batch_processing:
                result = self.summary_generator.generate_company_summary_with_batching(
                    expert_quotes, 
                    batch_size=self.config.batch_size
                )
            else:
                result = self.summary_generator.generate_company_summary_direct(expert_quotes)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Company summary generation failed: {e}")
            return {"error": str(e)}

    def _update_progress(self, completed_stage: PipelineStage):
        """Update workflow progress based on completed stage."""
        if completed_stage in self.stage_weights:
            self.workflow_state.progress += self.stage_weights[completed_stage] * 100

    def _handle_stage_error(self, stage: PipelineStage, error_message: str):
        """Handle errors during stage execution."""
        self.workflow_state.error_message = f"Stage {stage.value} failed: {error_message}"
        self.workflow_state.retry_count += 1
        
        self.logger.error(f"Stage {stage.value} failed: {error_message}")
        
        # Check if we should retry
        if self.workflow_state.retry_count < self.config.max_retries:
            self.logger.info(f"Retrying stage {stage.value} (attempt {self.workflow_state.retry_count})")
            time.sleep(self.config.batch_delay)
        else:
            self.logger.error(f"Stage {stage.value} failed after {self.config.max_retries} attempts")
            raise RuntimeError(f"Stage {stage.value} failed permanently: {error_message}")

    def _handle_workflow_error(self, error_message: str):
        """Handle workflow-level errors."""
        self.workflow_state.status = WorkflowStatus.FAILED
        self.workflow_state.end_time = datetime.now()
        self.workflow_state.error_message = error_message
        self.workflow_state.current_operation = "Workflow failed"

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and progress."""
        return {
            "status": self.workflow_state.status.value,
            "current_stage": self.workflow_state.current_stage.value if self.workflow_state.current_stage else None,
            "progress": self.workflow_state.progress,
            "current_operation": self.workflow_state.current_operation,
            "start_time": self.workflow_state.start_time.isoformat() if self.workflow_state.start_time else None,
            "end_time": self.workflow_state.end_time.isoformat() if self.workflow_state.end_time else None,
            "error_message": self.workflow_state.error_message,
            "retry_count": self.workflow_state.retry_count,
            "stage_results": list(self.workflow_state.stage_results.keys())
        }

    def cancel_workflow(self):
        """Cancel the currently running workflow."""
        if self.workflow_state.status == WorkflowStatus.RUNNING:
            self.workflow_state.status = WorkflowStatus.CANCELLED
            self.workflow_state.end_time = datetime.now()
            self.workflow_state.current_operation = "Workflow cancelled by user"
            self.logger.info("Workflow cancelled by user")

    def reset_workflow(self):
        """Reset workflow state for new execution."""
        self.workflow_state = WorkflowState()
        self.logger.info("Workflow state reset")

    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics."""
        if not self.workflow_state.start_time:
            return {}
        
        end_time = self.workflow_state.end_time or datetime.now()
        duration = (end_time - self.workflow_state.start_time).total_seconds()
        
        return {
            "duration_seconds": duration,
            "duration_minutes": duration / 60,
            "status": self.workflow_state.status.value,
            "stages_completed": len(self.workflow_state.stage_results),
            "total_stages": len(self.pipeline_stages),
            "success_rate": 100.0 if self.workflow_state.status == WorkflowStatus.COMPLETED else 0.0
        }
