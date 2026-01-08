#!/bin/bash
# Python Quality Gates Script - project-agnostic
# Runs linting, type checking, complexity analysis, hypothesis checks, tests, and docs linting

set -e

EXCLUDES="tests,test,docs,doc,examples,scripts,build,dist,.venv,venv,.tox,.git,node_modules,__pycache__,*.egg-info"

usage() {
    cat <<'EOF'
Usage: ./quality-gates.sh <mode>

Modes:
  unit-tests  Run static gates + unit tests only: ruff, type check, radon, hypothesis checks, pytest (unit/), markdownlint.
  all-tests   Run all gates: ruff, type check, radon, hypothesis checks, pytest (unit/ + integration/), markdownlint.
  no-tests    Run static gates only: ruff, type check, radon, hypothesis checks, markdownlint. No pytest.

For AI agents: choose explicitly to control test scope.
  - unit-tests: fast feedback, catches logic/model errors
  - all-tests: comprehensive validation before merge/deploy
  - no-tests: lint/type/complexity only (when time is critical)
EOF
}

mode="${1:-}"

if [ -z "$mode" ]; then
    usage
    exit 1
fi

echo "Running Python quality gates (${mode})..."

install_test_deps() {
    if ! uv run python -c "import pytest" 2>/dev/null; then
        echo "Installing test dependencies..."
        uv sync --extra test
    fi
}

run_static_gates() {
    echo "Running ruff..."
    if command -v uvx >/dev/null 2>&1; then
        uvx ruff check . --fix
    else
        echo "uvx not found, skipping ruff"
    fi

    echo "Running type checking with pyrefly..."
    if command -v uvx >/dev/null 2>&1; then
        uvx pyrefly check .
    else
        echo "uvx not found, skipping pyrefly"
    fi

    echo "Running radon complexity analysis..."
    if command -v uv >/dev/null 2>&1; then
        radon_output=$(uv run radon cc . --ignore="$EXCLUDES" --min C --total-average --show-complexity 2>/dev/null || echo "radon failed")
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
        echo "uv not found, skipping radon"
    fi

    echo "Checking hypothesis test structure..."
    if [ -f "scripts/check_hypothesis_tests.sh" ]; then
        bash scripts/check_hypothesis_tests.sh
    else
        echo "check_hypothesis_tests.sh not found, skipping hypothesis structure check"
    fi

    echo "Checking hypothesis suppression..."
    if [ -f "scripts/check_suppress_health.sh" ]; then
        bash scripts/check_suppress_health.sh
    else
        echo "check_suppress_health.sh not found, skipping hypothesis suppression check"
    fi
}

run_tests() {
    echo "Running unit tests..."
    if command -v uv >/dev/null 2>&1; then
        uv run python -m pytest tests/unit/ --no-cov -x -W error::DeprecationWarning -W error::PendingDeprecationWarning
    else
        echo "uv not found, skipping pytest"
    fi
}

run_all_tests() {
    echo "Running all tests (unit + integration)..."
    if command -v uv >/dev/null 2>&1; then
        uv run python -m pytest tests/ --no-cov -x -W error::DeprecationWarning -W error::PendingDeprecationWarning
    else
        echo "uv not found, skipping pytest"
    fi
}

run_markdownlint() {
    echo "Running markdownlint..."
    if command -v markdownlint >/dev/null 2>&1; then
        markdownlint --fix .
    else
        echo "markdownlint not found, skipping"
    fi
}

case "$mode" in
    unit-tests)
        install_test_deps
        run_static_gates
        run_tests
        run_markdownlint
        echo "Unit test quality gates passed! ✅"
        ;;
    all-tests)
        install_test_deps
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