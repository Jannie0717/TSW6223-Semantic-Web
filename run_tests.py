"""Automated functionality tests for Solution 1.

Run with:
    python run_tests.py

These tests support the Evaluation section by checking whether RDF/RDFS loading,
SPARQL querying, interest-area input, and course recommendation work as expected.
"""

from app import EX, get_interests, query_schema_summary, run_recommendation


def labels(items):
    return {item["label"] for item in items}


def course_names(result):
    return {item["course"] for item in result["recommended_courses"]}


def assert_contains(actual, expected, field_name):
    missing = set(expected) - set(actual)
    if missing:
        raise AssertionError(f"{field_name} missing expected values: {sorted(missing)}. Actual: {sorted(actual)}")


def run_case(name, interest, expected_courses):
    result = run_recommendation(str(interest))
    courses = course_names(result)
    assert_contains(courses, expected_courses, "Recommended courses")
    print(f"PASS - {name}")


def main():
    assert "Artificial Intelligence" in labels(get_interests())

    schema = query_schema_summary()
    assert len(schema["classes"]) == 4
    assert len(schema["properties"]) >= 8
    print("PASS - RDF/RDFS schema and data loaded")

    run_case(
        "AI course recommendation by interest only",
        EX.ArtificialIntelligence,
        [
            "Introduction to Python Programming",
            "Statistics for Data Analytics",
            "Machine Learning",
            "Deep Learning",
            "Algorithm Design",
        ],
    )

    run_case(
        "Data Science course recommendation by interest only",
        EX.DataScience,
        [
            "Introduction to Python Programming",
            "Database Systems",
            "Statistics for Data Analytics",
            "Machine Learning",
            "Data Visualization",
            "Critical Thinking and Problem Solving",
        ],
    )

    run_case(
        "Cybersecurity course recommendation by interest only",
        EX.Cybersecurity,
        [
            "Computer Networking",
            "Cybersecurity Fundamentals",
            "Critical Thinking and Problem Solving",
        ],
    )

    run_case(
        "Web development course recommendation by interest only",
        EX.WebDevelopmentInterest,
        [
            "Database Systems",
            "Web Design",
            "JavaScript Development",
            "Backend Web Programming",
        ],
    )

    print("\nAll Solution 1 interest-only course recommendation tests passed.")


if __name__ == "__main__":
    main()
