import io
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY


class PDFGenerator:
    def __init__(self):
        self.buffer = io.BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer, 
            pagesize=A4, 
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.setup_styles()
        
    def setup_styles(self):
        """Define all the styles needed for the document"""
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=self.styles['Heading2'],
            fontSize=16,
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=18,
            spaceAfter=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        self.subheading_style = ParagraphStyle(
            'SubheadingStyle',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        self.bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=0,
            spaceAfter=3,
            leftIndent=20,
            bulletIndent=10
        )
        
        self.toc_style = ParagraphStyle(
            'TOCStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=3,
            spaceAfter=3,
            fontName='Helvetica'
        )
        
    def create_cover_page(self, project_name):
        """Create the cover page with title and date"""
        self.story.append(Paragraph("Product Requirements Document:", self.title_style))
        self.story.append(Paragraph(project_name, self.subtitle_style))
        self.story.append(Spacer(1, 0.2 * inch))
        
        date_str = datetime.now().strftime("%B %d, %Y")
        self.story.append(Paragraph(f"Generated on: {date_str}", self.normal_style))
        self.story.append(Spacer(1, inch))
        
    def create_table_of_contents(self):
        """Create the table of contents"""
        self.story.append(Paragraph("Table of Contents", self.subtitle_style))
        self.story.append(Spacer(1, 0.2 * inch))
        
        toc_entries = [
            "Introduction",
            "Goals and Objectives",
            "User Personas and Roles",
            "Functional Requirements",
            "Non-Functional Requirements",
            "User Interface (UI) / User Experience (UX) Considerations",
            "Data Requirements",
            "System Architecture & Technical Considerations",
            "Release Criteria & Success Metrics",
            "Timeline & Milestones",
            "Team Structure",
            "User Stories",
            "Cost Estimation",
            "Open Issues & Future Considerations",
            "Appendix",
            "Points Requiring Further Clarification"
        ]
        
        for i, entry in enumerate(toc_entries, 1):
            self.story.append(Paragraph(f"{i}. {entry}", self.toc_style))
        
    def extract_project_name(self, content):
        """Extract the project name from the content"""
        match = re.search(r"Product Requirements Document:?\s*([^\n]+)", content)
        if match:
            return match.group(1).strip()
        else:
            return "Project Requirements Document"
        
    def extract_project_name(self, content):
        """Extract the project name from the content"""
        match = re.search(r"Product Requirements Document:?\s*([^\n]+)", content)
        if match:
            return match.group(1).strip()
        else:
            return "Project Requirements Document"
    
    def parse_and_add_content(self, content):
        """Parse the content and add it to the story with proper formatting"""
        # Try to extract sections using regex pattern
        sections = {}
        
        # Look for patterns like "1. Introduction", "2. Goals and Objectives", etc.
        for i in range(1, 17):  # We have 16 sections
            section_title = self.get_default_section_title(str(i))
            pattern = rf'{i}\.\s+{re.escape(section_title)}(.*?)(?={i+1}\.\s+|$)'
            
            match = re.search(pattern, content, re.DOTALL)
            if match:
                sections[str(i)] = f"{i}. {section_title}{match.group(1)}"
            else:
                # Simplified fallback pattern
                simple_pattern = rf'{i}\.\s+(.*?)(?={i+1}\.\s+|$)'
                match = re.search(simple_pattern, content, re.DOTALL)
                if match:
                    sections[str(i)] = match.group(0)
                else:
                    # If section not found, create a placeholder
                    sections[str(i)] = f"{i}. {section_title}\n\nNo content provided for this section."
        
        # Process each section
        for section_num in sorted(sections.keys(), key=int):
            section_content = sections[section_num]
            
            # Extract title
            title_match = re.match(rf'{section_num}\.\s+(.*?)(?=\n|$)', section_content)
            section_title = title_match.group(1) if title_match else self.get_default_section_title(section_num)
            
            # Add section header
            self.story.append(Paragraph(f"{section_num}. {section_title}", self.heading_style))
            
            # Extract content (remove the title line)
            lines = section_content.split('\n', 1)
            if len(lines) > 1:
                content_text = lines[1].strip()
                if content_text:
                    self.add_content_with_formatting(content_text)
            
            # Add spacer after section
            self.story.append(Spacer(1, 0.2 * inch))
                
    def extract_sections(self, content):
        """Extract main sections from content using regex"""
        sections = {}
        # Look for patterns like "1. Introduction", "2. Goals and Objectives", etc.
        section_patterns = [
            (r'1\.\s+Introduction(.*?)(?=2\.\s+Goals|$)', '1'),
            (r'2\.\s+Goals and Objectives(.*?)(?=3\.\s+User|$)', '2'),
            (r'3\.\s+User Personas and Roles(.*?)(?=4\.\s+Functional|$)', '3'),
            (r'4\.\s+Functional Requirements(.*?)(?=5\.\s+Non-Functional|$)', '4'),
            (r'5\.\s+Non-Functional Requirements(.*?)(?=6\.\s+User Interface|$)', '5'),
            (r'6\.\s+User Interface.*?Considerations(.*?)(?=7\.\s+Data|$)', '6'),
            (r'7\.\s+Data Requirements(.*?)(?=8\.\s+System|$)', '7'),
            (r'8\.\s+System Architecture(.*?)(?=9\.\s+Release|$)', '8'),
            (r'9\.\s+Release Criteria(.*?)(?=10\.\s+Timeline|$)', '9'),
            (r'10\.\s+Timeline(.*?)(?=11\.\s+Team|$)', '10'),
            (r'11\.\s+Team Structure(.*?)(?=12\.\s+User Stories|$)', '11'),
            (r'12\.\s+User Stories(.*?)(?=13\.\s+Cost|$)', '12'),
            (r'13\.\s+Cost Estimation(.*?)(?=14\.\s+Open|$)', '13'),
            (r'14\.\s+Open Issues(.*?)(?=15\.\s+Appendix|$)', '14'),
            (r'15\.\s+Appendix(.*?)(?=16\.\s+Points|$)', '15'),
            (r'16\.\s+Points Requiring(.*?)$', '16'),
        ]
        
        for pattern, section_num in section_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                sections[section_num] = match.group(0)
            else:
                # If section not found, create a placeholder
                sections[section_num] = f"{section_num}. {self.get_default_section_title(section_num)}"
                
        return sections
    
    def get_default_section_title(self, section_num):
        """Get default section title if not found"""
        titles = {
            '1': 'Introduction',
            '2': 'Goals and Objectives',
            '3': 'User Personas and Roles',
            '4': 'Functional Requirements',
            '5': 'Non-Functional Requirements',
            '6': 'User Interface (UI) / User Experience (UX) Considerations',
            '7': 'Data Requirements',
            '8': 'System Architecture & Technical Considerations',
            '9': 'Release Criteria & Success Metrics',
            '10': 'Timeline & Milestones',
            '11': 'Team Structure',
            '12': 'User Stories',
            '13': 'Cost Estimation',
            '14': 'Open Issues & Future Considerations',
            '15': 'Appendix',
            '16': 'Points Requiring Further Clarification'
        }
        return titles.get(section_num, f"Section {section_num}")
            
    def extract_subsections(self, section_content):
        """Extract subsections from a section content"""
        subsections = {}
        
        # Look for patterns like "1.1 Purpose", "1.2 Scope", etc.
        subsection_pattern = r'(\d+)\.(\d+)\s+(.*?)(?=\d+\.\d+|\Z)'
        matches = re.finditer(subsection_pattern, section_content, re.DOTALL)
        
        for match in matches:
            section_num = match.group(1)
            subsection_num = match.group(2)
            subsection_content = match.group(0)
            subsections[subsection_num] = subsection_content
            
        return subsections
    
    def get_section_title(self, section_num, content):
        """Extract the title of a section"""
        pattern = r'\d+\.\s+(.*?)(?=\n|\Z)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        else:
            return self.get_default_section_title(section_num)
    
    def get_subsection_title(self, subsection_num, content):
        """Extract the title of a subsection"""
        pattern = r'\d+\.\d+\s+(.*?)(?=\n|\Z)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        else:
            return f"Subsection {subsection_num}"
    
    def clean_section_content(self, content):
        """Remove the section title from content"""
        pattern = r'\d+\.\s+.*?\n(.*)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # If we can't find the pattern, just return everything after the first line
            lines = content.split('\n', 1)
            if len(lines) > 1:
                return lines[1].strip()
            return ""
    
    def clean_subsection_content(self, content):
        """Remove the subsection title from content"""
        pattern = r'\d+\.\d+\s+.*?\n(.*)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # If we can't find the pattern, just return everything after the first line
            lines = content.split('\n', 1)
            if len(lines) > 1:
                return lines[1].strip()
            return ""
    
    def add_content_with_formatting(self, content):
        """Process and add content with proper formatting"""
        # Check if this is a bullet list
        if re.search(r'^\s*[\-\*]\s', content, re.MULTILINE):
            items = []
            paragraphs = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('-') or line.startswith('*'):
                    # If we had normal paragraphs before, add them
                    if paragraphs:
                        for p in paragraphs:
                            self.story.append(Paragraph(p, self.normal_style))
                        paragraphs = []
                    
                    # Add bullet item
                    bullet_text = line[1:].strip()
                    items.append(ListItem(Paragraph(bullet_text, self.bullet_style)))
                else:
                    # If we had bullet items before, add them
                    if items:
                        self.story.append(ListFlowable(items, bulletType='bullet', start=None))
                        items = []
                    
                    # Collect normal paragraph text
                    paragraphs.append(line)
            
            # Add any remaining items
            if items:
                self.story.append(ListFlowable(items, bulletType='bullet', start=None))
            
            # Add any remaining paragraphs
            if paragraphs:
                for p in paragraphs:
                    self.story.append(Paragraph(p, self.normal_style))
        else:
            # Process normal paragraphs
            paragraphs = content.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    self.story.append(Paragraph(p.strip(), self.normal_style))
    
    def add_functional_requirements_table(self, content):
        """Parse and add a table for functional requirements"""
        # Simple table extraction - in a real implementation, you'd want more robust parsing
        rows = []
        header_row = ['ID', 'Requirement Description', 'Priority', 'Dependencies']
        rows.append(header_row)
        
        # Extract table rows
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("FR") and "|" in line:
                # It's a table row
                cells = [cell.strip() for cell in line.split('|')]
                if len(cells) >= 4:
                    rows.append(cells[:4])  # Take the first 4 cells
            elif line.startswith("ID") and "|" in line:
                # Skip the header row as we've already added it
                continue
        
        # If we found no data rows, add a placeholder
        if len(rows) == 1:
            rows.append(['FR01', 'Placeholder requirement', 'High', '-'])
        
        # Create the table
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(table)
    
    def generate(self, content):
        """Generate the PDF"""
        # Extract project name
        project_name = self.extract_project_name(content)
        
        # Create cover page
        self.create_cover_page(project_name)
        
        # Create table of contents
        self.create_table_of_contents()
        
        # Add page break after TOC
        self.story.append(PageBreak())
        
        # Parse and add content
        self.parse_and_add_content(content)
        
        # Build the PDF
        self.doc.build(self.story)
        
        # Reset buffer position to the beginning
        self.buffer.seek(0)
        return self.buffer
