![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Holingo - Harry Potter Spell Pronunciation System

This project is a multi-container application that displays Harry Potter spells in a web interface and allows users to assess their spell pronunciation using Azure Cognitive Services.


## Configuration

This project uses a .env file for database and Azure configuration.
An example file is provided as env.example with dummy values. The actual env file values will be sent to graders directly.

## How to Run

From the root directory run 
```bash
docker compose up --build
```
This will:
    - start a local MongoDB container
    - automatically load spell data from seed/spells.json
    - start up the Flask web app
No manual database setup is required — the seed container inserts data on startup.


## Team Assoc

| Name | GitHub |
|------|--------|
| Sean Tang | [@plant445](https://github.com/plant445) |
| Morin Zhou | [@Morinzzz](https://github.com/Morinzzz) |
| May Zhou | [@zz4206](https://github.com/zz4206) |
| Howard Appel | [@hna2019](https://github.com/hna2019) |
| Leo Fu | [@LeoFYH](https://github.com/LeoFYH) |


