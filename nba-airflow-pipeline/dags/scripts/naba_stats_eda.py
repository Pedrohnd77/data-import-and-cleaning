"""
NBA Stats EDA - 2022-2023 Season
Converted from: code/notebook_eda.ipynb
Source repo:    https://github.com/Pedrohnd77/nba-stats-eda

This script performs exploratory data analysis on NBA player statistics,
identifying the best players by position in regular season and playoffs,
and the statistically best team.

Data files required (place in the data/ folder):
  - 2022-2023 NBA Player Stats - Regular.csv
  - 2022-2023 NBA Player Stats - Playoffs.csv

Source: https://www.kaggle.com/datasets/vivovinco/20222023-nba-player-stats-regular/data
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend (required for server/Docker environments)
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths — configurable via environment variables
# ---------------------------------------------------------------------------
DATA_PATH   = os.environ.get('NBA_DATA_PATH',   '/opt/airflow/data')
OUTPUT_PATH = os.environ.get('NBA_OUTPUT_PATH', '/opt/airflow/outputs')

REGULAR_CSV  = os.path.join(DATA_PATH, '2022-2023 NBA Player Stats - Regular.csv')
PLAYOFFS_CSV = os.path.join(DATA_PATH, '2022-2023 NBA Player Stats - Playoffs.csv')

# ---------------------------------------------------------------------------
# Position analysis configuration
# ---------------------------------------------------------------------------
POSITIONS_CONFIG = {
    'PG': {
        'label':     'Point Guard',
        'cols':      ['Player', 'Pos', 'PTS', 'AST', 'STL', 'TOV'],
        'sort_by':   ['PTS', 'AST', 'STL', 'TOV'],
        'ascending': [False, False, False, True],   # TOV: lower is better
    },
    'SG': {
        'label':     'Shooting Guard',
        'cols':      ['Player', 'Pos', 'PTS', '3P%', 'STL', 'TRB'],
        'sort_by':   ['PTS', '3P%', 'STL', 'TRB'],
        'ascending': [False, False, False, False],
    },
    'SF': {
        'label':     'Small Forward',
        'cols':      ['Player', 'Pos', 'PTS', 'TRB', 'AST', 'STL'],
        'sort_by':   ['PTS', 'TRB', 'AST', 'STL'],
        'ascending': [False, False, False, False],
    },
    'PF': {
        'label':     'Power Forward',
        'cols':      ['Player', 'Pos', 'TRB', 'PTS', 'BLK', '2P%'],
        'sort_by':   ['TRB', 'PTS', 'BLK', '2P%'],
        'ascending': [False, False, False, False],
    },
    'C': {
        'label':     'Center',
        'cols':      ['Player', 'Pos', 'TRB', 'BLK', 'PTS', '2P%'],
        'sort_by':   ['TRB', 'BLK', 'PTS', '2P%'],
        'ascending': [False, False, False, False],
    },
}


# ===========================================================================
# 1. LOAD DATA
# ===========================================================================
def load_data():
    """Load the two NBA stats CSV files."""
    logger.info("Loading data from: %s", DATA_PATH)

    for path in [REGULAR_CSV, PLAYOFFS_CSV]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"CSV not found: {path}\n"
                "Please place the data files in the data/ folder."
            )

    stats_regular  = pd.read_csv(REGULAR_CSV,  delimiter=';', index_col='Rk', encoding='ISO-8859-1')
    stats_playoffs = pd.read_csv(PLAYOFFS_CSV, delimiter=';', index_col='Rk', encoding='ISO-8859-1')

    logger.info("Regular season loaded  → %d rows, %d columns", *stats_regular.shape)
    logger.info("Playoffs loaded        → %d rows, %d columns", *stats_playoffs.shape)

    return stats_regular, stats_playoffs


# ===========================================================================
# 2. EXPLORE DATA
# ===========================================================================
def explore_data(df_regular, df_playoffs):
    """Log basic structure and statistical summary of both datasets."""
    logger.info("=" * 60)
    logger.info("REGULAR SEASON — first 5 rows")
    logger.info("\n%s", df_regular.head(5).to_string())
    logger.info("\nData types:\n%s", df_regular.dtypes.to_string())
    logger.info("\nStatistical description:\n%s", df_regular.describe().to_string())
    logger.info("\nColumns: %s", df_regular.columns.tolist())

    logger.info("=" * 60)
    logger.info("PLAYOFFS — first 5 rows")
    logger.info("\n%s", df_playoffs.head(5).to_string())
    logger.info("\nData types:\n%s", df_playoffs.dtypes.to_string())
    logger.info("\nStatistical description:\n%s", df_playoffs.describe().to_string())
    logger.info("\nColumns: %s", df_playoffs.columns.tolist())


# ===========================================================================
# 3. DATA QUALITY CHECK
# ===========================================================================
def check_data_quality(df_regular, df_playoffs):
    """Check for duplicates and missing values in both datasets."""
    logger.info("=" * 60)
    logger.info("DATA QUALITY CHECK")

    # Unique values per column
    logger.info("\nRegular season — unique values per column:\n%s", df_regular.nunique().to_string())
    logger.info("\nPlayoffs — unique values per column:\n%s", df_playoffs.nunique().to_string())

    # Duplicate rows
    dup_reg  = df_regular[df_regular.duplicated()]
    dup_play = df_playoffs[df_playoffs.duplicated()]
    logger.info("\nRegular season duplicate rows: %d", dup_reg.shape[0])
    logger.info("Playoffs duplicate rows:        %d", dup_play.shape[0])

    # Missing values
    logger.info("\nRegular season — missing values:\n%s", df_regular.isnull().sum().to_string())
    logger.info("\nPlayoffs — missing values:\n%s",       df_playoffs.isnull().sum().to_string())


# ===========================================================================
# 4. CLEAN DATA
# ===========================================================================
def clean_data(df_regular, df_playoffs):
    """
    Clean both datasets.
    Main treatment: multi-position players (e.g. 'PG-SG') → keep primary position ('PG').
    """
    logger.info("=" * 60)
    logger.info("CLEANING DATA")

    def clean_pos(x):
        if isinstance(x, str) and '-' in x:
            return x.split('-')[0]
        return x

    df_regular['Pos']  = df_regular['Pos'].apply(clean_pos)
    df_playoffs['Pos'] = df_playoffs['Pos'].apply(clean_pos)

    logger.info("Unique positions (regular):  %s", sorted(df_regular['Pos'].dropna().unique().tolist()))
    logger.info("Unique positions (playoffs): %s", sorted(df_playoffs['Pos'].dropna().unique().tolist()))

    return df_regular, df_playoffs


# ===========================================================================
# 5. ANALYZE BY POSITION
# ===========================================================================
def analyze_by_position(df_regular, df_playoffs):
    """Rank top players per position for regular season and playoffs."""
    logger.info("=" * 60)
    logger.info("PLAYER ANALYSIS BY POSITION")

    results = {}

    for pos, cfg in POSITIONS_CONFIG.items():
        # --- Regular season ---
        df_reg = (
            df_regular[df_regular['Pos'] == pos][cfg['cols']]
            .sort_values(by=cfg['sort_by'], ascending=cfg['ascending'])
        )

        # --- Playoffs ---
        mask_play = df_playoffs['Pos'] == pos
        if mask_play.any():
            df_play = (
                df_playoffs[mask_play][cfg['cols']]
                .sort_values(by=cfg['sort_by'], ascending=cfg['ascending'])
            )
        else:
            df_play = pd.DataFrame()

        results[pos] = {'regular': df_reg, 'playoffs': df_play, 'label': cfg['label']}

        logger.info("\n--- TOP 10 %s (%s) — Regular Season ---\n%s",
                    pos, cfg['label'], df_reg.head(10).to_string())

        if not df_play.empty:
            logger.info("\n--- TOP 10 %s (%s) — Playoffs ---\n%s",
                        pos, cfg['label'], df_play.head(10).to_string())

    return results


# ===========================================================================
# 6. TEAM ANALYSIS
# ===========================================================================
def analyze_teams(df_regular):
    """Find the statistically best team based on average key metrics."""
    logger.info("=" * 60)
    logger.info("TEAM ANALYSIS")

    team_stats = (
        df_regular
        .groupby('Tm')[['PTS', 'AST', 'TRB', 'STL', 'BLK']]
        .mean()
        .round(2)
    )

    # Simple composite score: weighted sum of key metrics
    team_stats['score'] = (
        team_stats['PTS'] * 0.4 +
        team_stats['AST'] * 0.2 +
        team_stats['TRB'] * 0.2 +
        team_stats['STL'] * 0.1 +
        team_stats['BLK'] * 0.1
    )

    team_ranking = team_stats.sort_values('score', ascending=False)
    logger.info("\nTeam ranking (composite score):\n%s", team_ranking.head(10).to_string())

    return team_ranking


# ===========================================================================
# 7. GENERATE CHARTS
# ===========================================================================
def generate_charts(results, team_ranking):
    """Generate and save bar charts for each position and team ranking."""
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    logger.info("=" * 60)
    logger.info("GENERATING CHARTS → %s", OUTPUT_PATH)

    for pos, data in results.items():
        for season, df in [('regular', data['regular']), ('playoffs', data['playoffs'])]:
            if df.empty:
                continue

            top10        = df.head(10)
            metric       = df.columns[2]   # First stat column (after Player, Pos)
            position_lbl = data['label']

            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.barh(top10['Player'], top10[metric], color='royalblue' if season == 'regular' else 'darkorange')
            ax.set_xlabel(metric, fontsize=12)
            ax.set_title(f'Top 10 {position_lbl} — {season.title()} Season 2022-2023  |  Metric: {metric}', fontsize=13)
            ax.invert_yaxis()

            for bar, val in zip(bars, top10[metric]):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                        f'{val:.1f}', va='center', fontsize=9)

            plt.tight_layout()
            fname = os.path.join(OUTPUT_PATH, f'top10_{pos.lower()}_{season}.png')
            plt.savefig(fname, dpi=150, bbox_inches='tight')
            plt.close()
            logger.info("  Saved: %s", fname)

    # Team ranking chart
    top10_teams = team_ranking.head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    top10_teams['score'].plot(kind='bar', ax=ax, color='mediumseagreen')
    ax.set_title('Top 10 Teams — Composite Score (Regular Season 2022-2023)', fontsize=13)
    ax.set_xlabel('Team')
    ax.set_ylabel('Score')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    fname = os.path.join(OUTPUT_PATH, 'top10_teams_score.png')
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info("  Team chart saved: %s", fname)


# ===========================================================================
# 8. SAVE RESULTS
# ===========================================================================
def save_results(results, team_ranking):
    """Export top-player tables and team ranking to CSV files."""
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    logger.info("=" * 60)
    logger.info("SAVING RESULTS → %s", OUTPUT_PATH)

    for pos, data in results.items():
        for season, df in [('regular', data['regular']), ('playoffs', data['playoffs'])]:
            if df.empty:
                continue
            fname = os.path.join(OUTPUT_PATH, f'top_players_{pos.lower()}_{season}.csv')
            df.head(10).to_csv(fname)
            logger.info("  Saved: %s", fname)

    fname = os.path.join(OUTPUT_PATH, 'team_ranking.csv')
    team_ranking.to_csv(fname)
    logger.info("  Team ranking saved: %s", fname)


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    logger.info("╔══════════════════════════════════════════════════════╗")
    logger.info("║       NBA STATS EDA PIPELINE — 2022-2023            ║")
    logger.info("╚══════════════════════════════════════════════════════╝")

    df_regular, df_playoffs = load_data()
    explore_data(df_regular, df_playoffs)
    check_data_quality(df_regular, df_playoffs)
    df_regular, df_playoffs = clean_data(df_regular, df_playoffs)
    results      = analyze_by_position(df_regular, df_playoffs)
    team_ranking = analyze_teams(df_regular)
    generate_charts(results, team_ranking)
    save_results(results, team_ranking)

    logger.info("✅  Pipeline completed successfully!")


if __name__ == '__main__':
    main()