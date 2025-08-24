#!/usr/bin/env python3
"""
Export Utilities Module for FlexXray Transcripts

This module handles export functionality including Excel, text, and other formats
for the quote analysis tool.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# Check if openpyxl is available for Excel export
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

class ExportManager:
    def __init__(self, output_directory: str = "Outputs"):
        """Initialize the export manager."""
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)

    def save_quote_analysis(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Save quote analysis results to JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_directory, f"FlexXray_quote_analysis_{timestamp}.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"Quote analysis saved to: {output_file}")
            return output_file
            
        except (IOError, OSError) as e:
            print(f"File system error saving quote analysis: {e}")
            return ""
        except (ValueError, TypeError) as e:
            print(f"Data serialization error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error saving quote analysis: {e}")
            return ""

    def export_quote_analysis_to_text(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Export quote analysis results to text file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_directory, f"FlexXray_quote_analysis_{timestamp}.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("FLEXXRAY QUOTE ANALYSIS RESULTS\n")
                f.write("=" * 50 + "\n\n")
                
                # Write metadata
                metadata = results.get('metadata', {})
                f.write(f"Analysis Date: {metadata.get('analysis_date', 'Unknown')}\n")
                f.write(f"Total Transcripts: {metadata.get('total_transcripts', 0)}\n")
                f.write(f"Total Quotes: {metadata.get('total_quotes', 0)}\n\n")
                
                # Write perspectives
                perspectives = results.get('perspectives', {})
                for perspective_key, perspective_data in perspectives.items():
                    f.write(f"PERSPECTIVE: {perspective_data.get('title', 'Unknown')}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Description: {perspective_data.get('description', '')}\n\n")
                    
                    # Write themes
                    themes = perspective_data.get('themes', [])
                    for theme in themes:
                        f.write(f"  Theme: {theme.get('name', 'Unknown')}\n")
                        f.write(f"  Description: {theme.get('description', '')}\n")
                        
                        # Write quotes for this theme
                        quotes = theme.get('quotes', [])
                        for i, quote in enumerate(quotes, 1):
                            f.write(f"    Quote {i}: {quote.get('text', '')}\n")
                            if quote.get('transcript_name'):
                                f.write(f"      Source: {quote['transcript_name']}\n")
                        f.write("\n")
                    
                    f.write("\n")
                
                # Write quote summary
                quote_summary = results.get('quote_summary', {})
                f.write("QUOTE SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Strengths: {quote_summary.get('strengths_count', 0)}\n")
                f.write(f"Weaknesses: {quote_summary.get('weaknesses_count', 0)}\n")
                f.write(f"Neutral: {quote_summary.get('neutral_count', 0)}\n\n")
            
            print(f"Quote analysis exported to text: {output_file}")
            return output_file
            
        except (IOError, OSError) as e:
            print(f"File system error exporting to text: {e}")
            return ""
        except (ValueError, TypeError) as e:
            print(f"Data formatting error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error exporting to text: {e}")
            return ""

    def export_company_summary_page(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page to text file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_directory, f"FlexXray_Company_Summary_Page_{timestamp}.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("FLEXXRAY COMPANY SUMMARY PAGE\n")
                f.write("=" * 40 + "\n\n")
                
                # Write key takeaways
                takeaways = summary_data.get('key_takeaways', [])
                if takeaways:
                    f.write("KEY TAKEAWAYS\n")
                    f.write("-" * 20 + "\n")
                    for i, takeaway in enumerate(takeaways, 1):
                        # Handle both 'insight' and 'theme' fields
                        insight = takeaway.get('insight', takeaway.get('theme', ''))
                        f.write(f"{i}. {insight}\n")
                        
                        # Handle both 'supporting_quotes' and 'quotes' fields
                        quotes = takeaway.get('supporting_quotes', takeaway.get('quotes', []))
                        if quotes:
                            f.write("   Supporting quotes:\n")
                            for quote in quotes[:2]:  # Limit to 2 quotes
                                if isinstance(quote, dict):
                                    # Use formatted_text if available, otherwise fall back to text
                                    quote_text = quote.get('formatted_text', quote.get('text', quote.get('quote', '')))
                                    speaker = quote.get('speaker', quote.get('speaker_info', 'Unknown'))
                                    document = quote.get('document', quote.get('transcript_name', 'Unknown'))
                                    f.write(f"     - \"{quote_text}\" - {speaker} from {document}\n")
                                else:
                                    f.write(f"     - {quote}\n")
                        f.write("\n")
                
                # Write strengths
                strengths = summary_data.get('strengths', [])
                if strengths:
                    f.write("STRENGTHS\n")
                    f.write("-" * 15 + "\n")
                    for i, strength in enumerate(strengths, 1):
                        # Handle both 'insight' and 'theme' fields
                        insight = strength.get('insight', strength.get('theme', ''))
                        f.write(f"{i}. {insight}\n")
                        
                        # Handle both 'supporting_quotes' and 'quotes' fields
                        quotes = strength.get('supporting_quotes', strength.get('quotes', []))
                        if quotes:
                            f.write("   Supporting quotes:\n")
                            for quote in quotes[:2]:  # Limit to 2 quotes
                                if isinstance(quote, dict):
                                    # Use formatted_text if available, otherwise fall back to text
                                    quote_text = quote.get('formatted_text', quote.get('text', quote.get('quote', '')))
                                    speaker = quote.get('speaker', quote.get('speaker_info', 'Unknown'))
                                    document = quote.get('document', quote.get('transcript_name', 'Unknown'))
                                    f.write(f"     - \"{quote_text}\" - {speaker} from {document}\n")
                                else:
                                    f.write(f"     - {quote}\n")
                        f.write("\n")
                
                # Write weaknesses
                weaknesses = summary_data.get('weaknesses', [])
                if weaknesses:
                    f.write("WEAKNESSES\n")
                    f.write("-" * 15 + "\n")
                    for i, weakness in enumerate(weaknesses, 1):
                        # Handle both 'insight' and 'theme' fields
                        insight = weakness.get('insight', weakness.get('theme', ''))
                        f.write(f"{i}. {insight}\n")
                        
                        # Handle both 'supporting_quotes' and 'quotes' fields
                        quotes = weakness.get('supporting_quotes', weakness.get('quotes', []))
                        if quotes:
                            f.write("   Supporting quotes:\n")
                            for quote in quotes[:2]:  # Limit to 2 quotes
                                if isinstance(quote, dict):
                                    # Use formatted_text if available, otherwise fall back to text
                                    quote_text = quote.get('formatted_text', quote.get('text', quote.get('quote', '')))
                                    speaker = quote.get('speaker', quote.get('speaker_info', 'Unknown'))
                                    document = quote.get('document', quote.get('transcript_name', 'Unknown'))
                                    f.write(f"     - \"{quote_text}\" - {speaker} from {document}\n")
                                else:
                                    f.write(f"     - {quote}\n")
                        f.write("\n")
            
            print(f"Company summary page exported to text: {output_file}")
            return output_file
            
        except (IOError, OSError) as e:
            print(f"File system error exporting company summary page: {e}")
            return ""
        except (ValueError, TypeError) as e:
            print(f"Data formatting error exporting company summary page: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error exporting company summary page: {e}")
            return ""

    def export_company_summary_to_excel(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page to Excel file."""
        if not EXCEL_AVAILABLE:
            print("openpyxl not available for Excel export")
            return ""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_directory, f"FlexXray_Company_Summary_Page_{timestamp}.xlsx")
        
        try:
            # Create workbook and worksheet
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Company Summary"
            
            # Define styles
            header_font = Font(bold=True, size=14)
            section_font = Font(bold=True, size=12)
            quote_font = Font(italic=True)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font_white = Font(bold=True, color="FFFFFF")
            
            # Write title
            ws['A1'] = "FLEXXRAY COMPANY SUMMARY PAGE"
            ws['A1'].font = header_font
            ws.merge_cells('A1:D1')
            
            current_row = 3
            
            # Write key takeaways
            takeaways = summary_data.get('key_takeaways', [])
            if takeaways:
                ws[f'A{current_row}'] = "KEY TAKEAWAYS"
                ws[f'A{current_row}'].font = section_font
                current_row += 1
                
                for i, takeaway in enumerate(takeaways, 1):
                    ws[f'A{current_row}'] = f"{i}. {takeaway.get('insight', '')}"
                    ws[f'A{current_row}'].font = Font(bold=True)
                    current_row += 1
                    
                    if takeaway.get('supporting_quotes'):
                        for quote in takeaway['supporting_quotes'][:2]:  # Limit to 2 quotes
                            quote_cell = ws[f'B{current_row}']
                            # Use formatted_text if available, otherwise fall back to text
                            quote_text = quote.get('formatted_text', quote.get('text', ''))
                            quote_cell.value = f"• {quote_text}"
                            quote_cell.font = quote_font
                            quote_cell.alignment = Alignment(wrap_text=False, vertical="top")
                            current_row += 1
                    
                    current_row += 1
                
                current_row += 1
            
            # Write strengths
            strengths = summary_data.get('strengths', [])
            if strengths:
                ws[f'A{current_row}'] = "STRENGTHS"
                ws[f'A{current_row}'].font = section_font
                current_row += 1
                
                for i, strength in enumerate(strengths, 1):
                    ws[f'A{current_row}'] = f"{i}. {strength.get('insight', '')}"
                    ws[f'A{current_row}'].font = Font(bold=True)
                    current_row += 1
                    
                    if strength.get('supporting_quotes'):
                        for quote in strength['supporting_quotes'][:2]:  # Limit to 2 quotes
                            quote_cell = ws[f'B{current_row}']
                            # Use formatted_text if available, otherwise fall back to text
                            quote_text = quote.get('formatted_text', quote.get('text', ''))
                            quote_cell.value = f"• {quote_text}"
                            quote_cell.font = quote_font
                            quote_cell.alignment = Alignment(wrap_text=False, vertical="top")
                            current_row += 1
                    
                    current_row += 1
                
                current_row += 1
            
            # Write weaknesses
            weaknesses = summary_data.get('weaknesses', [])
            if weaknesses:
                ws[f'A{current_row}'] = "WEAKNESSES"
                ws[f'A{current_row}'].font = section_font
                current_row += 1
                
                for i, weakness in enumerate(weaknesses, 1):
                    ws[f'A{current_row}'] = f"{i}. {weakness.get('insight', '')}"
                    ws[f'A{current_row}'].font = Font(bold=True)
                    current_row += 1
                    
                    if weakness.get('supporting_quotes'):
                        for quote in weakness['supporting_quotes'][:2]:  # Limit to 2 quotes
                            quote_cell = ws[f'B{current_row}']
                            # Use formatted_text if available, otherwise fall back to text
                            quote_text = quote.get('formatted_text', quote.get('text', ''))
                            quote_cell.value = f"• {quote_text}"
                            quote_cell.font = quote_font
                            quote_cell.alignment = Alignment(wrap_text=False, vertical="top")
                            current_row += 1
                    
                    current_row += 1
            
            # Set specific column widths with special handling for quote column
            column_widths = {
                'A': 40,   # Main content column
                'B': 80,   # Quote column - Wide for full quote display
                'C': 30,   # Additional content columns
                'D': 30
            }
            
            for col_letter, width in column_widths.items():
                if col_letter in ws.column_dimensions:
                    ws.column_dimensions[col_letter].width = width
            

            
            # Save workbook
            wb.save(output_file)
            wb.close()
            
            print(f"Company summary page exported to Excel: {output_file}")
            return output_file
            
        except (IOError, OSError) as e:
            print(f"File system error exporting company summary page to Excel: {e}")
            return ""
        except (ValueError, TypeError) as e:
            print(f"Data formatting error exporting company summary page to Excel: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error exporting company summary page to Excel: {e}")
            return ""

    def export_quotes_to_excel(self, quotes_data: List[Dict[str, Any]], output_file: str = None) -> str:
        """Export quotes to Excel file with proper text wrapping for quote column."""
        if not EXCEL_AVAILABLE:
            print("openpyxl not available for Excel export")
            return ""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_directory, f"FlexXray_quotes_{timestamp}.xlsx")
        
        try:
            # Create workbook and worksheet
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Quotes"
            
            # Define styles
            header_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font_white = Font(bold=True, color="FFFFFF", size=12)
            quote_font = Font(size=11)
            
            # Define headers
            headers = [
                "Quote ID", "Quote Text", "Speaker", "Company/Title", "Transcript", 
                "Sentiment", "Relevance Score", "Theme", "Date"
            ]
            
            # Write headers
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font_white
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            # Write quote data
            for row, quote in enumerate(quotes_data, 2):
                # Quote ID
                ws.cell(row=row, column=1, value=quote.get('id', f"Q{row-1}"))
                
                # Quote Text - This is the main column that needs wrapping
                quote_cell = ws.cell(row=row, column=2, value=quote.get('text', ''))
                quote_cell.font = quote_font
                quote_cell.alignment = Alignment(wrap_text=True, vertical="top")
                
                # Speaker
                speaker_info = quote.get('speaker_info', '')
                if isinstance(speaker_info, dict):
                    speaker_name = speaker_info.get('name', '')
                else:
                    speaker_name = str(speaker_info)
                ws.cell(row=row, column=3, value=speaker_name)
                
                # Company/Title
                if isinstance(speaker_info, dict):
                    company_title = speaker_info.get('company', '') or speaker_info.get('title', '')
                else:
                    company_title = ''
                ws.cell(row=row, column=4, value=company_title)
                
                # Transcript
                ws.cell(row=row, column=5, value=quote.get('transcript_name', ''))
                
                # Sentiment
                ws.cell(row=row, column=6, value=quote.get('sentiment', ''))
                
                # Relevance Score
                relevance = quote.get('relevance_score', '')
                if relevance is not None:
                    ws.cell(row=row, column=7, value=float(relevance))
                else:
                    ws.cell(row=row, column=7, value='')
                
                # Theme
                ws.cell(row=row, column=8, value=quote.get('theme', ''))
                
                # Date
                date_value = quote.get('date', '')
                if date_value:
                    ws.cell(row=row, column=9, value=date_value)
            
            # Set column widths with special handling for quote column
            column_widths = {
                'A': 10,   # Quote ID
                'B': 80,   # Quote Text - Wide column for quotes
                'C': 20,   # Speaker
                'D': 25,   # Company/Title
                'E': 30,   # Transcript
                'F': 15,   # Sentiment
                'G': 15,   # Relevance Score
                'H': 20,   # Theme
                'I': 15    # Date
            }
            
            for col_letter, width in column_widths.items():
                ws.column_dimensions[col_letter].width = width
            
            # Set row heights for quote rows to accommodate wrapped text
            for row in range(2, len(quotes_data) + 2):
                ws.row_dimensions[row].height = 60  # Set minimum height for quote rows
            
            # Freeze the header row
            ws.freeze_panes = 'A2'
            
            # Save workbook
            wb.save(output_file)
            wb.close()
            
            print(f"Quotes exported to Excel: {output_file}")
            return output_file
            
        except (IOError, OSError) as e:
            print(f"File system error exporting quotes to Excel: {e}")
            return ""
        except (ValueError, TypeError) as e:
            print(f"Data formatting error exporting quotes to Excel: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error exporting quotes to Excel: {e}")
            return ""

    def _extract_section(self, text: str, section_header: str) -> str:
        """Extract a section from text based on header."""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if section_header.lower() in line.lower():
                in_section = True
                continue
            elif in_section and line.strip() and not line.startswith(' '):
                break
            elif in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines).strip()

    def _extract_bullet_points(self, text: str, section_header: str) -> List[str]:
        """Extract bullet points from a section."""
        section_text = self._extract_section(text, section_header)
        if not section_text:
            return []
        
        lines = section_text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                # Clean up the bullet point
                clean_line = re.sub(r'^[•\-*]\s*', '', line)
                clean_line = re.sub(r'^\d+\.\s*', '', clean_line)
                if clean_line:
                    bullet_points.append(clean_line)
        
        return bullet_points
