# NBA 40-20 Rule Analysis

An end-to-end data engineering project that investigates Phil Jackson's famous **40-20 rule** in the NBA: A team must reach 40 wins before losing 20 games to be a legitimate championship contender.

## Overview

**The Question:** How many NBA champions actually satisfied the 40-20 rule?

**The Finding:** Historically, **17 of the last 20 NBA champions** met this criterion. From 1984 to 2026 there have been 5 notable exceptions (1995 Rockets, 2004 Pistons, 2006 Heat, 2021 Bucks, 2026 Knicks).

This project builds a complete data pipeline to verify this claim across all NBA seasons from 1983-84 to 2025-26.

## Architecture & Stack

The project follows a **medallion architecture** (bronze → silver → gold):

- **Data Ingestion:** Apache Airflow + [nba_api](https://github.com/swar/nba_api)
- **Data Warehouse:** PostgreSQL
- **Transformations:** dbt (with Postgres)
- **Visualization:** Streamlit
- **Containerization:** Docker Compose

## Data Model

### Bronze Layer (Raw)
- `bronze.game_logs` — One row per team per regular season game
- `bronze.team_season_stats` — One row per team per season with playoff results

### Silver Layer (Cleaned)
- `silver.game_logs_with_cumulative` — Game logs with running win/loss totals per team per season
- `silver.team_season_with_playoff_round` — Team season stats with classified playoff rounds
- `silver.dim_teams` — SCD Type 2 team dimension tracking name/city changes over time

### Gold Layer (Analytics)
- `gold.rule_40_20` — Did each team achieve 40 Wins before 20 Losses?
- `gold.playoff_results` — Playoff round reached by each team each season
- `gold.champion_40_20` — **Key output:** Champions and their 40-20 rule status
