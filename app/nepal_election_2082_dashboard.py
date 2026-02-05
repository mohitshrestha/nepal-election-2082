# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "duckdb==1.4.4",
#     "marimo>=0.19.7",
#     "pandas==3.0.0",
#     "pydantic-ai==1.54.0",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pandas as pd
    return duckdb, mo, pd


@app.cell
def _(duckdb, mo, pd):
    # 1. Construct the path (works locally and in WASM)
    # This will be a Path object locally and a URL string in WASM
    path = mo.notebook_location() / "public" / "data" / "election.json"


    def load_con():
        con = duckdb.connect()

        # 2. Let Pandas handle the fetch
        # Pandas is "WASM-aware" and knows how to download from a URL
        # or read from a local file automatically.
        df = pd.read_json(str(path), compression=None)

        # 3. Register the DataFrame into DuckDB
        con.register("election", df)
        return con
    return (load_con,)


@app.cell
def _(load_con):
    # Step 1: Load Data into DuckDB
    con = load_con()
    return (con,)


@app.cell
def _(con, mo, pd):
    # 1. SQL Query with Gender Breakdown
    election_stats = con.execute("""
        SELECT 
            COUNT(*) AS total_candidates, 
            COUNT(DISTINCT political_party_name) AS political_parties,
            COUNT(DISTINCT district) AS districts,
            COUNT(DISTINCT state) AS provinces,
        FROM election;
    """).fetchall()

    # 2. Convert the query result into a pandas DataFrame
    election_stats_df = pd.DataFrame(
        election_stats,
        columns=[
            "total_candidates",
            "political_parties",
            "districts",
            "provinces",
        ],
    )

    # 3. Stop if the election stats DataFrame is empty or None
    mo.stop(election_stats_df is None or election_stats_df.empty)

    # 4. Create stat cards for each statistic (total candidates, political parties, gender breakdown, etc.)
    _cards = [
        mo.stat(
            label=label.title().replace(
                "_", " "
            ),  # Format the label (capitalize and replace underscores)
            value=election_stats_df[label][
                0
            ],  # Extract value from the DataFrame (first row)
            bordered=True,  # Add a border around the card
        )
        for label in election_stats_df.columns  # Loop through the DataFrame columns
    ]

    # 5. Set the title for the stats cards
    _title = "### **Election Statistics**"

    # 6. Now display the stats with a markdown title and a horizontal stack of stat cards
    mo.vstack(
        [
            mo.md(_title),  # Display the markdown title
            mo.hstack(
                _cards, widths="equal", align="center"
            ),  # Stack the stat cards horizontally
        ]
    )
    return


@app.cell
def _(con, mo, pd):
    # ------------------------
    # Gender Breakdown Analysis with Percentages and Comma Formatting
    # ------------------------

    # Query to get the gender breakdown (Male vs Female)
    gender_breakdown_stats = con.execute("""
        SELECT 
            gender, COUNT(*) AS count
        FROM election
        GROUP BY gender
        ORDER BY gender;
    """).fetchall()

    # Convert the result into a pandas DataFrame
    gender_breakdown_df = pd.DataFrame(
        gender_breakdown_stats, columns=["gender", "count"]
    )

    # Stop if the gender breakdown DataFrame is empty or None
    mo.stop(gender_breakdown_df is None or gender_breakdown_df.empty)

    # Calculate the total number of candidates
    total_candidates = gender_breakdown_df["count"].sum()

    # Reorder gender_breakdown_df to place "अन्य" (Other) candidates at the end
    ordered_gender_breakdown = gender_breakdown_df.sort_values(
        by="gender", ascending=True
    )

    # Now manually move the "अन्य" (Other) candidates to the last position
    ordered_gender_breakdown = ordered_gender_breakdown[
        ordered_gender_breakdown["gender"] != "अन्य"
    ]
    other_candidates = gender_breakdown_df[gender_breakdown_df["gender"] == "अन्य"]
    ordered_gender_breakdown = pd.concat(
        [ordered_gender_breakdown, other_candidates]
    )

    # Create stat cards for gender breakdown
    gender_cards = [
        mo.stat(
            label=f"{row['gender'].title()} Candidates",  # Capitalize the gender
            value=f"{row['count']:,} ({row['count'] / total_candidates * 100:.1f}%)",  # Value with comma formatting
            bordered=True,  # Add border for visual clarity
        )
        for _, row in ordered_gender_breakdown.iterrows()  # Loop through rows of the DataFrame
    ]

    # Title for the gender breakdown stats
    _gender_title = "### **Gender Breakdown**"

    # Display the gender breakdown stats with a markdown title and horizontal stack of stat cards
    mo.vstack(
        [
            mo.md(_gender_title),  # Display the title
            mo.hstack(
                gender_cards, widths="equal", align="center"
            ),  # Stack the stat cards horizontally
        ]
    )
    return


@app.cell
def _(con, mo, pd):
    # Query main parties + aggregate "स्वतन्त्र"
    party_breakdown_stats = con.execute("""
        SELECT 
            political_party_name,
            CASE 
                WHEN political_party_name = 'स्वतन्त्र' THEN NULL 
                ELSE MAX(symbol_image) 
            END AS symbol_image,
            CASE 
                WHEN political_party_name = 'स्वतन्त्र' THEN 'स्वतन्त्र'
                ELSE MAX(symbol_name) 
            END AS symbol_name,
            SUM(count) AS count
        FROM (
            SELECT political_party_name, symbol_image, symbol_name, COUNT(*) AS count
            FROM election
            GROUP BY political_party_name, symbol_image, symbol_name
        ) sub
        GROUP BY political_party_name
        ORDER BY count DESC;
    """).fetchall()

    party_breakdown_df = pd.DataFrame(
        party_breakdown_stats,
        columns=["political_party_name", "symbol_image", "symbol_name", "count"],
    )

    mo.stop(party_breakdown_df.empty)

    total_candidates_main = party_breakdown_df["count"].sum()

    # Create cards
    party_cards = []

    for _, row in party_breakdown_df.iterrows():
        is_independent = row["political_party_name"] == "स्वतन्त्र"

        # Symbol block
        if is_independent:
            symbol_html = """
            <div style="text-align:center;">
                <div style="
                    width:50px;
                    height:50px;
                    border-radius:50%;
                    background:#e0e0e0;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    margin:0 auto 4px auto;
                    font-weight:bold;
                    color:#555;
                    font-size:0.75em;
                ">
                    स्वतन्त्र
                </div>
                <em style="font-size:0.85em; color:#555;">स्वतन्त्र</em>
            </div>
            """
        else:
            symbol_html = f"""
            <div style="text-align:center;">
                <img src="{row["symbol_image"]}"
                     alt="{row["symbol_name"]}"
                     width="50" height="50"
                     style="border-radius:50%; display:block; margin:0 auto 4px auto;">
                <em style="font-size:0.85em; color:#555;">{row["symbol_name"]}</em>
            </div>
            """

        card = mo.md(
            f"""
            <div style="
                border:1px solid #ccc;
                border-radius:8px;
                padding:8px;
                text-align:center;
                margin:4px;
                width:150px;
            ">
                <h3 style="margin-bottom:10px;">
                    {row["political_party_name"]}
                </h3>

                <div style="margin-bottom:10px;">
                    <strong style="font-size:1.2em;">
                        {row["count"]:,}
                    </strong><br>
                    <span style="font-size:1em; color:#555;">
                        {row["count"] / total_candidates_main * 100:.1f}%
                    </span>
                </div>

                {symbol_html}
            </div>
            """
        )

        party_cards.append(card)

    # Display in rows of 4
    rows = [party_cards[i : i + 4] for i in range(0, len(party_cards), 4)]

    main_title = mo.md("## Political Party Breakdown")

    mo.vstack(
        [
            main_title,
            *[
                mo.hstack(row, widths="equal", align="center", wrap=True, gap=1)
                for row in rows
            ],
        ],
        gap=1,
    )
    return


@app.cell
def _(con, mo, pd):
    # Query for the "स्वतन्त्र" party breakdown
    indenpendent_party_breakdown_stats = con.execute("""
        SELECT political_party_name,
               symbol_image AS symbol_image,
               symbol_name AS symbol_name,
               COUNT(*) AS count
        FROM election
        WHERE political_party_name='स्वतन्त्र'
        GROUP BY political_party_name, symbol_image, symbol_name
        ORDER BY count DESC;
    """).fetchall()

    # Convert the results to DataFrame
    indenpendent_party_breakdown_df = pd.DataFrame(
        indenpendent_party_breakdown_stats,
        columns=["political_party_name", "symbol_image", "symbol_name", "count"],
    )

    # Stop if the dataframe is empty
    mo.stop(indenpendent_party_breakdown_df.empty)

    # Rename total_candidates_main to total_candidates_independent
    total_candidates_independent = indenpendent_party_breakdown_df["count"].sum()

    # Create cards for the independent party
    independent_party_cards = []
    for _, independent_row in indenpendent_party_breakdown_df.iterrows():
        independent_card = mo.md(
            f"""
            <div style="border:1px solid #ccc; border-radius:8px; padding:1px; text-align:center; margin:1px; width:150px;">
                <h3 style="margin-bottom:10px;">{independent_row["political_party_name"]}</h3>
                <div style="text-align:center; margin-bottom:10px;">
                    <strong style="font-size:1.2em;">{independent_row["count"]:,}</strong><br>
                    <span style="font-size:1em; color:#555;">{independent_row["count"] / total_candidates_independent * 100:.1f}%</span>
                </div>
                <div style="text-align:center;">
                    <img src="{independent_row["symbol_image"]}" alt="{independent_row["symbol_name"]}" width="50" height="50" style="border-radius:50%; display:block; margin:0 auto 1px auto;">
                    <em style="font-size:0.85em; color:#555;">{independent_row["symbol_name"]}</em>
                </div>
            </div>
            """
        )
        independent_party_cards.append(independent_card)

    # Create rows for displaying the independent party cards
    independent_party_rows = [
        independent_party_cards[i : i + 4]
        for i in range(0, len(independent_party_cards), 4)
    ]

    # Define the title for the breakdown
    independent_party_title = mo.md("## Independent Party Breakdown")

    # Display the independent party cards in a vertical stack
    mo.vstack(
        [
            independent_party_title,
            *[
                mo.hstack(
                    independent_row,
                    widths="equal",
                    align="center",
                    wrap=True,
                    gap=1,
                )
                for independent_row in independent_party_rows
            ],
        ],
        gap=1,
    )
    return


if __name__ == "__main__":
    app.run()
