#!/bin/bash
# Python Quality Gates Script - project-agnostic
# Runs linting, type checking, complexity analysis, hypothesis checks, tests, and docs linting

set -e

EXCLUDES="tests,test,docs,doc,examples,scripts,build,dist,.venv,venv,.tox,.git,node_modules,__pycache__,*.egg-info"

usage() {
    cat <<'USAGE'
Usage: ./quality-gates.sh <mode>

Modes:
  unit-tests  Run static gates + unit tests only: ruff, type check, radon, hypothesis checks, pytest (unit/), markdownlint.
  all-tests   Run all gates: ruff, type check, radon, hypothesis checks, pytest (unit/ + integration/), markdownlint.
  no-tests    Run static gates only: ruff, type check, radon, hypothesis checks, markdownlint. No pytest.

For AI agents: choose explicitly to control test scope.
  - unit-tests: fast feedback, catches logic/model errors
  - all-tests: comprehensive validation before merge/deploy
  - no-tests: lint/type/complexity only (when time is critical)
USAGE
}

mode="${1:-}"

if [ -z "$mode" ]; then
    usage
    exit 1
fi

echo "Running Python quality gates (${mode})..."

run_static_gates() {
    echo "Running ruff..."
    if command -v uvx >/dev/null 2>&1; then
        uvx ruff check . --fix
    else
        echo "uvx not fINSTALL TO CONTINUE"
        exit 1
    fi

    echo "Running type checking with pyrefly..."
    if command -v uvx >/dev/null 2>&1; then
        uvx pyrefly check . --project-excludes="tests" --project-excludes="test_*.py"
    else
        echo "uvx not found, INSTALL TO CONTINUE"
        exit 1 
    fi

    echo "Running radon complexity analysis..."
    if command -v uvx >/dev/null 2>&1; then
        radon_output=$(uvx radon cc . --ignore="$EXCLUDES" --min C --total-average --show-complexity 2>/dev/null || echo "radon failed")
        complexity_issues=$(echo "$radon_output" | grep -v "blocks (classes, functions, methods) analyzed" | grep -v "Average complexity:" | grep -E "[CDF]" || true)
        if [ -n "$complexity_issues" ]; then
            echo "$radon_output"
            echo ""
            echo "❌ Error: Code complexity issues detected (C, D, or F grades)."
            echo "   C = Moderate complexity - MUST be refactored"
            echo "   D = High complexity - MUST be refactored"
            echo "   F = Very high complexity - MUST be refactored"
            echo ""
            echo "Please refactor the above methods to reduce complexity before committing."
            exit 1
        else
            echo "$radon_output"
        fi
    else
        echo "uvx not found, INSTALL TO CONTINUE"
        exit 1 
    fi

    echo "Checking for hypothesis @given tests outside of *_property.py files..."
    violations=$(grep -r "@given" tests/ --include="*.py" 2>/dev/null | grep -v "_property.py" || true)
    if [ -n "$violations" ]; then
        echo "❌ Error: Hypothesis @given tests found outside of *_property.py files. Property tests must be in dedicated *_property.py files."
        echo "$violations"
        exit 1
    fi

    echo "Checking for suppress_health decorators in non-test files..."
    # Check for suppress_health decorators in test files
    if grep -r "suppress_health\|@suppress()" tests/ --include="*.py" 2>/dev/null; then
        echo "❌ Error: suppress_health decorator found in test files. Tests should be properly written without suppressors."
        exit 1
    fi

}

run_tests() {
    echo "Running unit tests..."
    if command -v uv >/dev/null 2>&1; then
        uvx run python -m pytest tests/unit/ --no-cov -x -W error::DeprecationWarning -W error::PendingDeprecationWarning
    else
        echo "uv not found, INSTALL TO CONTINUE"
        exit 1 
    fi
}

run_all_tests() {
    echo "Running all tests (unit + integration)..."
    if command -v uvx >/dev/null 2>&1; then
        uvx run python -m pytest tests/ --no-cov -x -W error::DeprecationWarning -W error::PendingDeprecationWarning
    else
        echo "uv not found, INSTALL TO CONTINUE"
        exit 1 
    fi
}

run_markdownlint() {
    echo "Running markdownlint..."
    if command -v markdownlint >/dev/null 2>&1; then
        markdownlint --fix .
    else
        echo "markdownlint not found, INSTALL TO CONTINUE"
        exit 1 
    fi
}

case "$mode" in
    unit-tests)
        run_static_gates
        run_tests
        run_markdownlint
        echo "Unit test quality gates passed! ✅"
        ;;
    all-tests)
        run_static_gates
        run_all_tests
        run_markdownlint
        echo "All quality gates passed! ✅"
        ;;
    no-tests)
        run_static_gates
        run_markdownlint
        echo "Non-test quality gates passed! ✅"
        ;;
    *)
        usage
        exit 1
        ;;
esac
