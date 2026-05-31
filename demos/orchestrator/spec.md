# Orchestrator Demo Specification

## Objective

Build a simple Python script that reads a CSV file containing names and outputs a JSON file with those names grouped alphabetically by the first letter of each name.

## Requirements

- **Input**: CSV file with a `name` column
- **Output**: JSON file with structure: `{"A": ["Alice", "Andrew"], "B": ["Bob"], ...}`
- **Processing**: Group names by first character (case-insensitive)
- **Error Handling**: Handle missing files and invalid input gracefully

## Acceptance Criteria

- [ ] Script reads CSV without crashing on missing file
- [ ] Names are correctly grouped by first letter
- [ ] Output JSON is valid and well-formatted
- [ ] Empty groups are excluded
- [ ] Script logs each step to stdout
