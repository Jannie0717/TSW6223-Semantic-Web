Semantic Course and Career Recommendation System - Category 2 Version
====================================================================

Project Domain:
Education

Real-World Problem:
Students often have difficulty choosing suitable courses because they do not clearly understand the connection between current skills, missing skills, course choices and future career paths.

Two Related Subdomains:
1. Course Recommendation
2. Career Path and Skill Gap Analysis

Selected Semantic Web Topic:
Category 2: RDF, RDFS and SPARQL

Important Modification:
This version has been modified to use Category 2 only.
OWL and inference have been removed from the code, RDF data file, interface text and report support files.

Main Features:
1. Student selects an interest area.
2. Student selects current skills.
3. Student optionally selects a target career.
4. System uses SPARQL to find possible careers related to the selected interest.
5. System uses SPARQL to identify matched skills and missing skills.
6. System uses SPARQL to recommend courses that teach the missing skills.

How to Run:
1. Install Python 3.10 or above.
2. Open CMD or terminal in this project folder.
3. Create a virtual environment:
   python -m venv venv

4. Activate virtual environment:
   Windows CMD:
   venv\Scripts\activate.bat

   Windows PowerShell:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   venv\Scripts\activate

   macOS/Linux:
   source venv/bin/activate

5. Install dependencies:
   pip install -r requirements.txt

6. Run the application:
   python app.py

7. Keep the terminal open and browse to:
   http://127.0.0.1:5000

Project Structure:
app.py                         Main Flask application
requirements.txt               Python libraries required
data/education_rdf_rdfs.ttl    RDF/RDFS schema and sample data
templates/index.html           Web interface
static/style.css               Page styling
docs/                          Report and testing support files

Suggested Demonstration Example:
Interest Area: Artificial Intelligence
Target Career: AI Engineer
Current Skills: Python Programming

Expected Output:
- Matched skill: Python Programming
- Missing skills: Algorithms, Deep Learning, Machine Learning
- Recommended courses: Algorithm Design, Deep Learning, Machine Learning

Semantic Web Usage:
RDF is used to represent students, courses, skills, careers and interests as triples.
RDFS is used to define classes, properties, domain and range.
SPARQL is used to query possible careers, skill gaps and recommended courses.
