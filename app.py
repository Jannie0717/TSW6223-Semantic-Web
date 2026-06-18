"""Semantic Course and Career Recommendation System
Category 2: RDF, RDFS and SPARQL.

This Flask application loads RDF/RDFS data from a Turtle file and uses
SPARQL queries to retrieve possible careers, matched skills, missing skills
and recommended courses. OWL and inference are not used in this version.
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple

from flask import Flask, render_template, request
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "education_rdf_rdfs.ttl"
EX = Namespace("http://example.org/education#")


def load_graph() -> Graph:
    """Load the RDF/RDFS Turtle file into an RDFLib graph."""
    graph = Graph()
    graph.parse(DATA_FILE, format="turtle")
    graph.bind("ex", EX)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    return graph


def label(graph: Graph, uri: URIRef) -> str:
    """Return rdfs:label when available; otherwise return the URI local name."""
    value = graph.value(uri, RDFS.label)
    return str(value) if value else str(uri).split("#")[-1]


def description(graph: Graph, uri: URIRef) -> str:
    """Return ex:description when available."""
    value = graph.value(uri, EX.description)
    return str(value) if value else ""


def get_entities(class_uri: URIRef) -> List[Dict[str, str]]:
    """Use SPARQL to get individuals of a selected RDFS class for form options."""
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


def get_skills() -> List[Dict[str, str]]:
    return get_entities(EX.Skill)


def get_interests() -> List[Dict[str, str]]:
    return get_entities(EX.Interest)


def get_careers() -> List[Dict[str, str]]:
    return get_entities(EX.Career)


def add_student_profile(graph: Graph, selected_interest: str, selected_skills: List[str]) -> URIRef:
    """Add the current student profile into the graph as temporary RDF triples."""
    student_uri = EX.CurrentStudent
    graph.add((student_uri, RDF.type, EX.Student))
    graph.add((student_uri, RDFS.label, Literal("Current Student")))

    if selected_interest:
        graph.add((student_uri, EX.interestedIn, URIRef(selected_interest)))

    for skill_uri in selected_skills:
        graph.add((student_uri, EX.hasSkill, URIRef(skill_uri)))

    return student_uri


def query_possible_careers(graph: Graph, student_uri: URIRef) -> List[Dict[str, str]]:
    """Use SPARQL to find careers related to the student's selected interest."""
    query = """
    PREFIX ex: <http://example.org/education#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?career ?careerLabel ?desc WHERE {
        ?student ex:interestedIn ?interest .
        ?career a ex:Career ;
                ex:relatedToInterest ?interest ;
                rdfs:label ?careerLabel ;
                ex:description ?desc .
    }
    ORDER BY ?careerLabel
    """
    return [
        {"uri": str(row.career), "career": str(row.careerLabel), "description": str(row.desc)}
        for row in graph.query(query, initBindings={"student": student_uri})
    ]


def query_skill_gap(graph: Graph, student_uri: URIRef, career_uri: URIRef) -> Tuple[List[str], List[str], int]:
    """Use SPARQL to compare student skills with skills required by a target career."""
    matched_query = """
    PREFIX ex: <http://example.org/education#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?skill ?skillLabel WHERE {
        ?career ex:requiresSkill ?skill .
        ?student ex:hasSkill ?skill .
        ?skill rdfs:label ?skillLabel .
    }
    ORDER BY ?skillLabel
    """

    missing_query = """
    PREFIX ex: <http://example.org/education#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?skill ?skillLabel WHERE {
        ?career ex:requiresSkill ?skill .
        ?skill rdfs:label ?skillLabel .
        MINUS { ?student ex:hasSkill ?skill . }
    }
    ORDER BY ?skillLabel
    """

    all_required = set(graph.objects(career_uri, EX.requiresSkill))
    matched_rows = list(graph.query(matched_query, initBindings={"student": student_uri, "career": career_uri}))
    missing_rows = list(graph.query(missing_query, initBindings={"student": student_uri, "career": career_uri}))

    matched = [str(row.skillLabel) for row in matched_rows]
    missing = [str(row.skillLabel) for row in missing_rows]
    progress = round((len(matched) / len(all_required)) * 100) if all_required else 0
    return matched, missing, progress


def query_recommended_courses(graph: Graph, student_uri: URIRef, career_uri: URIRef) -> List[Dict[str, object]]:
    """
    Use SPARQL to recommend courses.

    Logic:
    1. The target career requires a skill.
    2. The student does not already have that skill.
    3. A course teaches that missing skill.
    """
    query = """
    PREFIX ex: <http://example.org/education#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?course ?courseLabel ?skill ?skillLabel ?difficulty ?credit ?desc WHERE {
        ?career ex:requiresSkill ?skill .
        ?course a ex:Course ;
                ex:teachesSkill ?skill ;
                rdfs:label ?courseLabel ;
                ex:difficulty ?difficulty ;
                ex:creditHour ?credit ;
                ex:description ?desc .
        ?skill rdfs:label ?skillLabel .
        MINUS { ?student ex:hasSkill ?skill . }
    }
    ORDER BY ?difficulty ?courseLabel
    """

    rows = []
    for row in graph.query(query, initBindings={"student": student_uri, "career": career_uri}):
        prerequisites = [label(graph, skill) for skill in graph.objects(row.course, EX.hasPrerequisiteSkill)]
        rows.append(
            {
                "course": str(row.courseLabel),
                "skill": str(row.skillLabel),
                "difficulty": str(row.difficulty),
                "credit": int(row.credit.toPython()) if hasattr(row.credit, "toPython") else str(row.credit),
                "description": str(row.desc),
                "prerequisites": prerequisites if prerequisites else ["None"],
            }
        )
    return rows


def get_sparql_examples() -> Dict[str, str]:
    """Return shortened SPARQL examples for display in the interface."""
    return {
        "career_query": """SELECT ?career ?careerLabel WHERE {\n  ?student ex:interestedIn ?interest .\n  ?career a ex:Career ; ex:relatedToInterest ?interest ; rdfs:label ?careerLabel .\n}""",
        "course_query": """SELECT ?course ?courseLabel WHERE {\n  ?career ex:requiresSkill ?skill .\n  ?course a ex:Course ; ex:teachesSkill ?skill ; rdfs:label ?courseLabel .\n  MINUS { ?student ex:hasSkill ?skill . }\n}""",
    }


def run_recommendation(selected_interest: str, selected_skills: List[str], selected_career: str) -> Dict[str, object]:
    """Main recommendation process using RDF/RDFS graph data and SPARQL queries."""
    graph = load_graph()
    student_uri = add_student_profile(graph, selected_interest, selected_skills)

    possible_careers = query_possible_careers(graph, student_uri)

    # If the user does not select a target career, use the first career matched from interest.
    if selected_career:
        target_career = URIRef(selected_career)
    elif possible_careers:
        target_career = URIRef(possible_careers[0]["uri"])
    else:
        target_career = None

    result = {
        "possible_careers": possible_careers,
        "target_career": None,
        "target_description": "",
        "matched_skills": [],
        "missing_skills": [],
        "progress": 0,
        "recommended_courses": [],
        "technology_note": "This version uses Category 2 only: RDF stores triples, RDFS defines classes/properties, and SPARQL retrieves career, skill gap and course recommendation results.",
        "sparql_examples": get_sparql_examples(),
    }

    if target_career:
        matched, missing, progress = query_skill_gap(graph, student_uri, target_career)
        result.update(
            {
                "target_career": label(graph, target_career),
                "target_description": description(graph, target_career),
                "matched_skills": matched,
                "missing_skills": missing,
                "progress": progress,
                "recommended_courses": query_recommended_courses(graph, student_uri, target_career),
            }
        )

    return result


@app.route("/", methods=["GET", "POST"])
def index():
    skills = get_skills()
    interests = get_interests()
    careers = get_careers()
    result = None
    selected = {"interest": "", "career": "", "skills": []}

    if request.method == "POST":
        selected["interest"] = request.form.get("interest", "")
        selected["career"] = request.form.get("career", "")
        selected["skills"] = request.form.getlist("skills")
        result = run_recommendation(selected["interest"], selected["skills"], selected["career"])

    return render_template(
        "index.html",
        skills=skills,
        interests=interests,
        careers=careers,
        result=result,
        selected=selected,
    )


if __name__ == "__main__":
    app.run(debug=True)
