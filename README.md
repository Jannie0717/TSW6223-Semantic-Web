# TSW6223-Semantic-Web
## Semantic Course and Career Recommendation System - Category 2 Version

Project Domain:
Education

Real-World Problem:
Students often have difficulty choosing suitable courses because they do not clearly understand the connection between current skills, missing skills, course choices and future career paths.

Subdomain
---------
Course Recommendation

Removed Sections
----------------
- Current Skills selection has been removed from the website.
- Career Path / Skill Gap Analysis has been removed from this Solution 1 version.
- The website no longer has target career selection, readiness score, matched skills, missing skills, alternative careers, or career source mapping.

Selected Semantic Web Technology
--------------------------------
Category 2: RDF, RDFS and SPARQL

Technology Usage
----------------
- RDF represents students, interests, skills and courses as triples.
- RDFS defines classes and properties such as Student, Course, Skill, Interest, interestedIn, teachesSkill and relatedToInterest.
- SPARQL retrieves courses related to the student's selected interest area.

Main Features
-------------
1. Student selects an interest area only.
2. System stores the selected interest as a temporary RDF triple.
3. System uses SPARQL to recommend courses related to the selected interest.
4. Website displays course description, skills taught, difficulty, credit hour and prerequisite skills.
5. Website displays an RDF/RDFS model preview for demonstration.
6. Website displays a sample SPARQL query used by the system.

Project Structure
-----------------
```
solution1_course_recommendation_interest_only/
|
├── app.py
├── requirements.txt
├── run_tests.py
├── run_windows_cmd.bat
├── README.txt
|
├── data/
│   └── education_rdf_rdfs.ttl
|
├── templates/
│   └── index.html
|
├── static/
│   └── style.css
|
└── docs/
    ├── GUIDELINE_COMPLIANCE_CHECK.txt
    ├── REPORT_SECTION_3_SOLUTION_DEVELOPMENT.txt
    ├── REPORT_SECTION_4_EVALUATION.txt
    ├── SPARQL_EXAMPLES.txt
    └── TEST_CASES.txt
```
How to Run on Windows CMD Manually
-------------------------
1. Open **Command Prompt** in this project folder.
2. Download python version 3.11.0
```
curl -o python-3.11.0.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
```
3. Install python version 3.11.0
```
./python-3.11.0.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
```
4. Create virtual environment:
```
python -m venv venv
```
5. Activate virtual environment (Windows)
```
venv\Scripts\activate.bat
```
6. Install requirements dependencies
```
pip install -r requirements.txt
```
7. Run app.py
```
python app.py
```
8. Open browser and go to:
```
http://127.0.0.1:5000
```
> [!NOTE]
> **Keep Command Prompt open.**

Alternative: Double-click run_windows_cmd.bat
--------------------------------------------
You may also double-click:

   run_windows_cmd.bat

This will create/activate the virtual environment, install requirements and run the website.

PowerShell Note
---------------
If PowerShell blocks venv activation with "running scripts is disabled", use CMD instead, or run:

   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\activate

How to Run Functionality Tests
------------------------------
After installing requirements, run:
```
python run_tests.py
```

Expected result:

   All Solution 1 interest-only course recommendation tests passed.

Suggested Demo Input
--------------------
Interest Area: Artificial Intelligence

Expected output:
- Recommended courses include Introduction to Python Programming, Machine Learning, Deep Learning, Algorithm Design, and Statistics for Data Analytics.
- The website shows RDF/RDFS model preview and SPARQL query examples.

Fix for Param.postParse2 / SPARQL Parser Error
---------------------------------------------
If the browser shows this error:

   TypeError: Param.postParse2() missing 1 required positional argument: 'tokenList'

it is usually caused by an incompatible rdflib / pyparsing package combination inside the virtual environment. The program code is still correct. To repair the local environment on Windows, double-click:

   FIX_DEPENDENCIES_WINDOWS.bat

Or run these commands in CMD inside the project folder:
```
venv\Scripts\activate.bat
```
```
python -m pip uninstall -y rdflib pyparsing
```
```
python -m pip install --no-cache-dir -r requirements.txt
```
```
python run_tests.py
```
```
python app.py
```