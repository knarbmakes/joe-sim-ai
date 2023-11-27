Joe Python Agent

## Updated Overview

Joe Python Agent is an autonomous, self-improving agent designed to assist with coding, documentation, planning, calculations, and file management tasks. It features a suite of tools for web scraping, file operations, system command execution, and interacting with a human for guidance on complex problems.

## Features

- Evaluate Python expressions and execute code snippets with a secure evaluation environment (asteval).
- Query, save, and delete long-term memories using ChromaDB with a focus on context-preserving interactions.
- An autonomous verification system that ensures quality and accuracy of its operations and outputs.
- A robust bank account balance and quota management system for managing operational costs.
- A flexible communication system that allows for verification and feedback loops, improving the agent decisions over time.

## Installation

Ensure you have Python 3.x and the required pip packages installed:

```
python -m pip install -r requirements.txt
```

## Usage

- Start the agent by running the main script:

```
python src/main.py
```

- Utilize individual tools by accessing the `/tools/` directory.
- Extend agent capabilities by adding new tools and commands into the `/src/tools/` directory.

## Scripts

Auxiliary scripts for specific tasks (e.g., document conversion, news digestion, stock price fetching) are included in the `/scripts/` directory.

## Testing

- Run unit tests with the following command to ensure integrity before making changes:

```
python src/run_tests.py
```

## License

The project is open source and available under the [MIT License](LICENSE).

