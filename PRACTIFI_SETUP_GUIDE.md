# 🚀 Practifi Company Setup Guide

This guide will help you set up Practifi as a new company in your transcript analysis system, including support for both PDF and Word documents.

## 📋 What We've Added

### 1. **Practifi Company Configuration**
- **Company Name**: Practifi
- **Industry Focus**: Financial advisor technology platform
- **Transcript Directory**: `Practifi Transcripts`
- **Output Prefix**: `Practifi`

### 2. **PDF Document Support**
- **Supported Formats**: `.pdf` and `.docx`
- **Libraries**: PyPDF2 and pypdf for PDF processing
- **Features**: Text extraction, page counting, document validation

### 3. **Practifi-Specific Analysis Questions**
- Platform adoption and user experience
- Feature effectiveness and integration capabilities
- Customer satisfaction and competitive position
- Growth opportunities in the advisor market

## 🔧 Setup Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `PyPDF2>=3.0.0` - PDF processing
- `pypdf>=3.0.0` - Alternative PDF processing
- `python-docx>=0.8.11` - Word document processing

### Step 2: Create Practifi Transcripts Directory
```bash
python company_switcher.py --switch practifi
python company_switcher.py --validate
```

Or manually create:
```
Project Root/
└── Practifi Transcripts/          # Your Practifi transcripts go here
```

### Step 3: Add Your Transcript Files
Place your Practifi transcript files in the `Practifi Transcripts` folder:
- **PDF files** (`.pdf`) - Financial advisor interviews, user feedback, etc.
- **Word documents** (`.docx`) - Meeting notes, interview transcripts, etc.

### Step 4: Test the Setup
```bash
python test_practifi_setup.py
```

This will verify:
- Company configuration is working
- PDF and Word support is available
- Directory structure is correct
- Document processing works

## 🎯 Practifi Analysis Focus

### **Key Questions for Analysis**
1. **Platform Adoption**: How is Practifi's platform being adopted by financial advisors?
2. **User Experience**: What is the user experience like for financial advisors using Practifi?
3. **Feature Effectiveness**: Which Practifi features are most effective for advisor workflows?
4. **Integration Capabilities**: How well does Practifi integrate with existing advisor systems?
5. **Customer Satisfaction**: What is the overall satisfaction level of Practifi users?
6. **Competitive Position**: How does Practifi compare to other advisor technology platforms?
7. **Growth Opportunities**: What growth opportunities exist for Practifi in the advisor market?

### **Question Categories**
- **Key Takeaways**: Platform adoption, user experience, feature effectiveness
- **Strengths**: Integration capabilities, customer satisfaction
- **Weaknesses**: Competitive position, growth opportunities

## 📄 Document Processing Features

### **PDF Support**
- ✅ Text extraction from all pages
- ✅ Page counting
- ✅ Document validation
- ✅ Error handling for corrupted files

### **Word Document Support**
- ✅ Text extraction from paragraphs
- ✅ Table content extraction
- ✅ Document structure analysis
- ✅ Metadata extraction

### **Unified Interface**
- Single method to process any supported format
- Automatic format detection
- Consistent output structure
- Comprehensive error reporting

## 🚀 Running Analysis

### **Switch to Practifi**
```bash
python company_switcher.py --switch practifi
```

### **Run Main Analysis**
```bash
python run_streamlined_analysis.py
```
- Processes all files in `Practifi Transcripts` folder
- Outputs to `Practifi_analysis.json`, `Practifi_analysis.txt`, etc.

### **Run Quote Analysis**
```bash
python quote_analysis_tool.py
```
- Extracts quotes from Practifi transcripts
- Outputs to `Practifi_quote_analysis.json`, `Practifi_quote_analysis.txt`

## 🔍 Testing Your Setup

### **Quick Test**
```bash
python test_practifi_setup.py
```

### **Manual Verification**
```bash
# List available companies
python company_switcher.py --list

# Show Practifi info
python company_switcher.py --info

# Show Practifi questions
python company_switcher.py --questions
```

### **Document Processing Test**
```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
print(f"Supported formats: {processor.get_supported_formats()}")

# Test a specific file
result = processor.extract_text_from_document("Practifi Transcripts/sample.pdf")
if result:
    print(f"Extracted {len(result)} characters")
```

## 📁 Expected Directory Structure

```
Project Root/
├── Practifi Transcripts/          # Your Practifi transcripts
│   ├── interview_advisor_1.pdf
│   ├── user_feedback_2024.docx
│   ├── platform_review.pdf
│   └── customer_survey.docx
├── FlexXray Transcripts/          # FlexXray transcripts
├── ACME Transcripts/              # ACME transcripts
└── Outputs/                       # Analysis outputs
    ├── Practifi_analysis.json
    ├── Practifi_quote_analysis.json
    ├── FlexXray_analysis.json
    └── ACME_analysis.json
```

## 🎯 Benefits of This Setup

### **For Practifi Analysis**
- **Industry-specific questions** tailored to financial advisor technology
- **PDF support** for various document formats
- **Separate analysis** from other companies
- **Customized insights** for platform evaluation

### **For Overall System**
- **Multi-format support** (PDF + Word)
- **Easy company switching** between FlexXray, ACME, and Practifi
- **Consistent analysis framework** across different industries
- **Scalable architecture** for adding more companies

## 🔧 Troubleshooting

### **PDF Processing Issues**
```bash
# Check if PDF libraries are installed
pip list | grep -i pdf

# Install manually if needed
pip install PyPDF2 pypdf
```

### **Word Document Issues**
```bash
# Check if python-docx is installed
pip list | grep -i docx

# Install manually if needed
pip install python-docx
```

### **Directory Issues**
```bash
# Validate transcript directory
python company_switcher.py --validate

# Create directory if missing
python company_switcher.py --validate
# Follow prompts to create directory
```

## 🚀 Next Steps

1. **Add your Practifi transcripts** to the `Practifi Transcripts` folder
2. **Test the setup** with `python test_practifi_setup.py`
3. **Switch to Practifi** with `python company_switcher.py --switch practifi`
4. **Run analysis** with your preferred analysis tool
5. **Review results** in the `Outputs` folder

## 📞 Support

If you encounter any issues:
1. Check the test output for error messages
2. Verify all dependencies are installed
3. Ensure transcript files are in the correct format
4. Check file permissions and directory access

Your Practifi analysis system is now ready to go! 🎉
