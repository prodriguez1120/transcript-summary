#!/usr/bin/env python3
"""
Company API - Frontend Integration Layer

This module provides a clean API interface for frontend applications to interact
with the company switcher functionality. It's designed to work well with web
frameworks like Flask, FastAPI, or any frontend that needs to manage company
configurations.
"""

import json
import os
from typing import Dict, List, Optional, Any
from company_config import list_available_companies, get_company_config, COMPANY_CONFIGS


class CompanyAPI:
    """API wrapper for company management functionality."""
    
    def __init__(self):
        """Initialize the company API."""
        self.current_company = "flexxray"  # Default company
        self.settings_file = "current_company.txt"
        self._load_current_company()
    
    def _load_current_company(self):
        """Load the current company from file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.current_company = f.read().strip()
            except:
                self.current_company = "flexxray"
    
    def _save_current_company(self):
        """Save the current company to file."""
        try:
            with open(self.settings_file, 'w') as f:
                f.write(self.current_company)
        except:
            pass
    
    def get_companies_list(self) -> Dict[str, Any]:
        """
        Get a list of all available companies for dropdown menu.
        
        Returns:
            Dict with companies list and current selection
        """
        try:
            companies = list_available_companies()
            current = self.current_company
            
            # Format for frontend dropdown
            companies_data = []
            for company_id in companies:
                config = get_company_config(company_id)
                companies_data.append({
                    "id": company_id,
                    "name": config.display_name,
                    "is_current": company_id == current,
                    "transcript_directory": config.transcript_directory,
                    "output_prefix": config.output_prefix,
                    "question_count": len(config.key_questions)
                })
            
            return {
                "success": True,
                "companies": companies_data,
                "current_company": current,
                "total_count": len(companies_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "companies": [],
                "current_company": None
            }
    
    def switch_company(self, company_id: str) -> Dict[str, Any]:
        """
        Switch to a different company.
        
        Args:
            company_id: The company identifier to switch to
            
        Returns:
            Dict with success status and company info
        """
        try:
            # Validate company exists
            available_companies = list_available_companies()
            if company_id not in available_companies:
                return {
                    "success": False,
                    "error": f"Company '{company_id}' not found",
                    "available_companies": available_companies
                }
            
            # Switch company
            self.current_company = company_id
            self._save_current_company()
            
            # Get updated company info
            company_info = self.get_company_info(company_id)
            return {
                "success": True,
                "message": f"Successfully switched to {company_info['company']['display_name']}",
                "company": company_info['company']
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_company_info(self, company_id: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a company.
        
        Args:
            company_id: Company identifier (uses current if None)
            
        Returns:
            Dict with company information
        """
        try:
            company_id = company_id or self.current_company
            config = get_company_config(company_id)
            
            if not config:
                return {
                    "success": False,
                    "error": f"Company '{company_id}' not found"
                }
            
            return {
                "success": True,
                "company": {
                    "id": config.name,
                    "display_name": config.display_name,
                    "transcript_directory": config.transcript_directory,
                    "output_prefix": config.output_prefix,
                    "key_questions": config.key_questions,
                    "question_categories": config.question_categories,
                    "industry_keywords": config.industry_keywords,
                    "company_specific_terms": config.company_specific_terms,
                    "question_count": len(config.key_questions),
                    "category_count": len(config.question_categories)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_company(self) -> Dict[str, Any]:
        """
        Get information about the currently selected company.
        
        Returns:
            Dict with current company information
        """
        return self.get_company_info()
    
    def validate_company_setup(self, company_id: str = None) -> Dict[str, Any]:
        """
        Validate that a company's setup is complete.
        
        Args:
            company_id: Company identifier (uses current if None)
            
        Returns:
            Dict with validation results
        """
        try:
            company_id = company_id or self.current_company
            config = get_company_config(company_id)
            
            if not config:
                return {
                    "success": False,
                    "error": f"Company '{company_id}' not found"
                }
            
            # Check transcript directory
            import os
            transcript_dir_exists = os.path.exists(config.transcript_directory)
            
            # Check if directory has files
            transcript_files = []
            if transcript_dir_exists:
                try:
                    transcript_files = [
                        f for f in os.listdir(config.transcript_directory)
                        if os.path.isfile(os.path.join(config.transcript_directory, f))
                        and f.lower().endswith(('.txt', '.docx', '.pdf'))
                    ]
                except:
                    transcript_files = []
            
            return {
                "success": True,
                "validation": {
                    "company_id": company_id,
                    "display_name": config.display_name,
                    "transcript_directory_exists": transcript_dir_exists,
                    "transcript_directory_path": config.transcript_directory,
                    "transcript_files_count": len(transcript_files),
                    "transcript_files": transcript_files,
                    "has_questions": len(config.key_questions) > 0,
                    "has_categories": len(config.question_categories) > 0,
                    "is_ready_for_analysis": (
                        transcript_dir_exists and 
                        len(transcript_files) > 0 and 
                        len(config.key_questions) > 0
                    )
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_company_questions(self, company_id: str = None) -> Dict[str, Any]:
        """
        Get the key questions for a company.
        
        Args:
            company_id: Company identifier (uses current if None)
            
        Returns:
            Dict with questions organized by category
        """
        try:
            company_id = company_id or self.current_company
            config = get_company_config(company_id)
            
            if not config:
                return {
                    "success": False,
                    "error": f"Company '{company_id}' not found"
                }
            
            # Organize questions by category
            questions_by_category = {}
            for category, question_keys in config.question_categories.items():
                questions_by_category[category] = {
                    "title": category.replace('_', ' ').title(),
                    "questions": []
                }
                for key in question_keys:
                    if key in config.key_questions:
                        questions_by_category[category]["questions"].append({
                            "key": key,
                            "question": config.key_questions[key]
                        })
            
            return {
                "success": True,
                "company_id": company_id,
                "display_name": config.display_name,
                "questions_by_category": questions_by_category,
                "total_questions": len(config.key_questions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Example usage for different frontend frameworks
def example_flask_endpoints():
    """
    Example Flask endpoints using the CompanyAPI.
    """
    from flask import Flask, jsonify, request
    
    app = Flask(__name__)
    company_api = CompanyAPI()
    
    @app.route('/api/companies', methods=['GET'])
    def get_companies():
        """Get list of companies for dropdown."""
        return jsonify(company_api.get_companies_list())
    
    @app.route('/api/companies/current', methods=['GET'])
    def get_current_company():
        """Get current company info."""
        return jsonify(company_api.get_current_company())
    
    @app.route('/api/companies/<company_id>', methods=['GET'])
    def get_company(company_id):
        """Get specific company info."""
        return jsonify(company_api.get_company_info(company_id))
    
    @app.route('/api/companies/<company_id>/switch', methods=['POST'])
    def switch_company(company_id):
        """Switch to a different company."""
        return jsonify(company_api.switch_company(company_id))
    
    @app.route('/api/companies/<company_id>/validate', methods=['GET'])
    def validate_company(company_id):
        """Validate company setup."""
        return jsonify(company_api.validate_company_setup(company_id))
    
    @app.route('/api/companies/<company_id>/questions', methods=['GET'])
    def get_company_questions(company_id):
        """Get company questions."""
        return jsonify(company_api.get_company_questions(company_id))
    
    return app


def example_fastapi_endpoints():
    """
    Example FastAPI endpoints using the CompanyAPI.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI()
    company_api = CompanyAPI()
    
    @app.get("/api/companies")
    async def get_companies():
        """Get list of companies for dropdown."""
        result = company_api.get_companies_list()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    
    @app.get("/api/companies/current")
    async def get_current_company():
        """Get current company info."""
        result = company_api.get_current_company()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    
    @app.get("/api/companies/{company_id}")
    async def get_company(company_id: str):
        """Get specific company info."""
        result = company_api.get_company_info(company_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    
    @app.post("/api/companies/{company_id}/switch")
    async def switch_company(company_id: str):
        """Switch to a different company."""
        result = company_api.switch_company(company_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    return app


# Test the API
if __name__ == "__main__":
    api = CompanyAPI()
    
    print("=== Company API Test ===")
    
    # Test getting companies list
    print("\n1. Getting companies list:")
    companies_result = api.get_companies_list()
    print(json.dumps(companies_result, indent=2))
    
    # Test getting current company
    print("\n2. Getting current company:")
    current_result = api.get_current_company()
    print(json.dumps(current_result, indent=2))
    
    # Test validation
    print("\n3. Validating current company setup:")
    validation_result = api.validate_company_setup()
    print(json.dumps(validation_result, indent=2))
    
    # Test getting questions
    print("\n4. Getting company questions:")
    questions_result = api.get_company_questions()
    print(json.dumps(questions_result, indent=2))
