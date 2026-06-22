"""Solution 1: Semantic Course Recommendation System.

Selected Semantic Web Technology focus: Category 2 only (RDF, RDFS and SPARQL).
This version removes Career Path / Skill Gap Analysis and keeps the application
focused on course recommendation in the education domain.

The system flow is:
1. Student selects one interest area.
2. Python Flask loads RDF/RDFS Turtle data using RDFLib.
3. SPARQL queries recommend courses related to the selected interest area.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from flask import Flask, render_template, request
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "education_rdf_rdfs.ttl"
EX = Namespace("http://example.org/education#")

DIFFICULTY_RANK = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}


def load_graph() -> Graph:
    """Load the RDF/RDFS Turtle file into an RDFLib graph."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"RDF/RDFS data file was not found: {DATA_FILE}")

    graph = Graph()
    graph.parse(DATA_FILE, format="turtle")
    graph.bind("ex", EX)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    return graph


def label(graph: Graph, uri: URIRef) -> str:
    """Return rdfs:label for a URI; otherwise return the URI local name."""
    value = graph.value(uri, RDFS.label)
    return str(value) if value else str(uri).split("#")[-1]


def description(graph: Graph, uri: URIRef) -> str:
    """Return ex:description for a URI when available."""
    value = graph.value(uri, EX.description)
    return str(value) if value else ""


def get_entities(class_uri: URIRef) -> List[Dict[str, str]]:
    """Retrieve all instances of an RDFS class using SPARQL."""
    graph = load_graph()
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?item ?itemLabel WHERE {
        ?item rdf:type ?class .
        ?item rdfs:label ?itemLabel .
    }
    ORDER BY ?itemLabel
    """
    return [
        {"uri": str(row.item), "label": str(row.itemLabel)}
        for row in graph.query(query, initBindings={"class": class_uri})
    ]


def get_interests() -> List[Dict[str, str]]:
    """Return all available interest areas for the dropdown input."""
    return get_entities(EX.Interest)


def query_schema_summary() -> Dict[str, List[Dict[str, str]]]:
    """Return RDFS classes and RDF properties for website demonstration."""
    graph = load_graph()

    class_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?class ?classLabel ?comment WHERE {
        ?class a rdfs:Class .
        OPTIONAL { ?class rdfs:label ?classLabel . }
        OPTIONAL { ?class rdfs:comment ?comment . }
    }
    ORDER BY ?classLabel
    """

    property_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?property ?propertyLabel ?domainLabel ?rangeLabel WHERE {
        ?property a rdf:Property .
        OPTIONAL { ?property rdfs:label ?propertyLabel . }
        OPTIONAL {
            ?property rdfs:domain ?domain .
            OPTIONAL { ?domain rdfs:label ?domainLabel . }
        }
        OPTIONAL {
            ?property rdfs:range ?range .
            OPTIONAL { ?range rdfs:label ?rangeLabel . }
        }
    }
    ORDER BY ?propertyLabel
    """

    classes = [
        {
            "uri": str(row["class"]),
            "label": str(row.classLabel) if row.classLabel else label(graph, row["class"]),
            "comment": str(row.comment) if row.comment else "",
        }
        for row in graph.query(class_query)
    ]

    properties = [
        {
            "uri": str(row.property),
            "label": str(row.propertyLabel) if row.propertyLabel else label(graph, row.property),
            "domain": str(row.domainLabel) if row.domainLabel else "-",
            "range": str(row.rangeLabel) if row.rangeLabel else "-",
        }
        for row in graph.query(property_query)
    ]

    return {"classes": classes, "properties": properties}


def add_student_profile(graph: Graph, selected_interest: str) -> URIRef:
    """Add current user interest input into the RDF graph as temporary triples."""
    student_uri = EX.CurrentStudent
    graph.add((student_uri, RDF.type, EX.Student))
    graph.add((student_uri, RDFS.label, Literal("Current Student")))

    if selected_interest:
        graph.add((student_uri, EX.interestedIn, URIRef(selected_interest)))

    return student_uri


def course_prerequisites(graph: Graph, course_uri: URIRef) -> List[str]:
    """Return prerequisite skill labels for a course."""
    prerequisites = [label(graph, skill_uri) for skill_uri in graph.objects(course_uri, EX.hasPrerequisiteSkill)]
    return prerequisites if prerequisites else ["None"]


def merge_course_row(courses: Dict[str, Dict[str, object]], row, graph: Graph) -> None:
    """Group SPARQL rows by course URI because one course may teach multiple skills."""
    uri = str(row.course)
    if uri not in courses:
        difficulty = str(row.difficulty)
        courses[uri] = {
            "course": str(row.courseLabel),
            "description": str(row.desc) if row.desc else "",
            "difficulty": difficulty,
            "difficulty_rank": DIFFICULTY_RANK.get(difficulty, 99),
            "credit": int(row.credit.toPython()),
            "skills": [],
            "prerequisites": course_prerequisites(graph, row.course),
            "reason": "",
        }

    skill_label = str(row.skillLabel)
    if skill_label not in courses[uri]["skills"]:
        courses[uri]["skills"].append(skill_label)


def query_recommended_courses(graph: Graph, student_uri: URIRef) -> List[Dict[str, object]]:
    """Use SPARQL to recommend courses related to the selected interest area."""
    query = """
    PREFIX ex: <http://example.org/education#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?course ?courseLabel ?skill ?skillLabel ?difficulty ?credit ?desc WHERE {
        ?student ex:interestedIn ?interest .
        ?course a ex:Course ;
                ex:relatedToInterest ?interest ;
                ex:teachesSkill ?skill ;
                rdfs:label ?courseLabel ;
                ex:difficulty ?difficulty ;
                ex:creditHour ?credit .
        ?skill rdfs:label ?skillLabel .
        OPTIONAL { ?course ex:description ?desc . }
    }
    ORDER BY ?courseLabel ?skillLabel
    """

    courses: Dict[str, Dict[str, object]] = {}
    for row in graph.query(query, initBindings={"student": student_uri}):
        merge_course_row(courses, row, graph)

    result = list(courses.values())
    for course in result:
        course["reason"] = "Recommended because it is related to the selected interest area and teaches: " + ", ".join(course["skills"]) + "."
    result.sort(key=lambda item: (item["difficulty_rank"], item["course"]))
    return result



def get_sparql_examples() -> Dict[str, str]:
    """Return sample SPARQL query displayed in the website."""
    return {
        "recommendation_query": """PREFIX ex: <http://example.org/education#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?course ?courseLabel ?skillLabel WHERE {
  ?student ex:interestedIn ?interest .
  ?course a ex:Course ;
          ex:relatedToInterest ?interest ;
          ex:teachesSkill ?skill ;
          rdfs:label ?courseLabel .
  ?skill rdfs:label ?skillLabel .
}
ORDER BY ?courseLabel ?skillLabel""",
    }


def run_recommendation(selected_interest: str) -> Dict[str, object]:
    """Run Solution 1 course recommendation using selected interest area only."""
    graph = load_graph()
    student_uri = add_student_profile(graph, selected_interest)
    selected_interest_uri = URIRef(selected_interest) if selected_interest else None

    return {
        "interest_label": label(graph, selected_interest_uri) if selected_interest_uri else "",
        "interest_description": description(graph, selected_interest_uri) if selected_interest_uri else "",
        "recommended_courses": query_recommended_courses(graph, student_uri),
        "technology_note": (
            "Solution 1 uses Category 2 only. RDF represents interests, skills and courses as triples; "
            "RDFS defines classes/properties with domain and range; SPARQL retrieves courses related to the selected interest area. "
            "The current skills checkbox and Career Path / Skill Gap Analysis have been removed."
        ),
        "sparql_examples": get_sparql_examples(),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    """Main web page for Solution 1."""
    interests = get_interests()
    schema_summary = query_schema_summary()
    result = None
    selected = {"interest": ""}

    if request.method == "POST":
        selected["interest"] = request.form.get("interest", "")
        result = run_recommendation(selected["interest"])

    return render_template(
        "index.html",
        interests=interests,
        schema_summary=schema_summary,
        result=result,
        selected=selected,
    )


if __name__ == "__main__":
    app.run(debug=True)
