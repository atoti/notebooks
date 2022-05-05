import pandas as pd
from tqdm import tqdm
from datetime import datetime
import os

data_path = "s3://data.atoti.io/notebooks/french-presidential-election-2022/"
output_path = "data/"


def translate_labels(_df_results, result_date):
    _df_results["Liste des candidats"] = _df_results["Liste des candidats"].str.title()
    _df_results["Liste des candidats"] = (
        _df_results["Liste des candidats"]
        .str.replace("M. ", "", regex=True)
        .replace("Mme ", "", regex=True)
    )

    _df_results["Voix"] = _df_results["Voix"].str.replace(" ", "").astype(int)
    _df_results["Result date"] = result_date  # datetime.today().strftime("%Y-%m-%d")

    _df_results.rename(
        columns={
            "Liste des candidats": "Candidate name",
            "Voix": "Votes",
            "% Inscrits": "% votes against registered voters",
            "% Exprimés": "% valid votes",
        },
        inplace=True,
    )

    return _df_results


def get_poll_results(link):
    _df_results = pd.read_html(
        link,
        attrs={"class": "tableau-resultats-listes-ER"},
        encoding="iso-8859-15",
        decimal=",",
        thousands=".",
    )

    if len(_df_results) > 1:
        df_round2 = translate_labels(_df_results[0], "2022-04-24")
        df_round1 = translate_labels(_df_results[1], "2022-04-10")

        return pd.concat([df_round2, df_round1], ignore_index=True)
    else:
        return translate_labels(_df_results[1], "2022-04-10")


def transform_stats(_df_turnout, result_date):
    _df_turnout.rename(
        columns={
            "Unnamed: 0": "Voting status",
            "Nombre": "Vote count",
            "% Inscrits": "% votes against registed voters",
            "% Votants": "% voters",
        },
        inplace=True,
    )

    _df_turnout["Vote count"] = (
        _df_turnout["Vote count"].str.replace(" ", "").astype(int)
    )
    _df_turnout["Result date"] = result_date  # datetime.today().strftime("%Y-%m-%d")

    # reference https://en.wikipedia.org/wiki/2022_French_presidential_election
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Nuls", "Voting status (EN)"
    ] = "Null ballots"
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Blancs", "Voting status (EN)"
    ] = "Blank ballots"
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Votants", "Voting status (EN)"
    ] = "Valid votes"
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Abstentions", "Voting status (EN)"
    ] = "Abstentions"
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Inscrits", "Voting status (EN)"
    ] = "Registered voters"
    _df_turnout.loc[
        _df_turnout["Voting status"] == "Exprimés", "Voting status (EN)"
    ] = "Turnout"

    return _df_turnout


def get_poll_statistics(link):
    _df_turnout = pd.read_html(
        link,
        attrs={"class": "tableau-mentions"},
        encoding="iso-8859-15",
        decimal=",",
        thousands=".",
    )

    _df_turnout_final = pd.DataFrame()

    if len(_df_turnout) > 1:
        df_turnout_round2 = transform_stats(_df_turnout[0], "2022-04-24")
        df_turnout_round1 = transform_stats(_df_turnout[1], "2022-04-10")

        _df_turnout_final = pd.concat(
            [df_turnout_round2, df_turnout_round1], ignore_index=True
        )
    else:
        _df_turnout_final = transform_stats(_df_turnout[0], "2022-04-10")

    return _df_turnout_final.pivot(
        index="Result date", columns="Voting status (EN)", values="Vote count"
    )


def get_states_poll():
    df_departments = pd.read_csv(f"{data_path}states.csv")
    print("No. of departments:", len(df_departments))

    df_departments_dict = df_departments.to_dict("records")

    for row in tqdm(df_departments_dict):
        df_state_results = get_poll_results(row["Link"])

        if df_state_results is not None:
            df_state_results["Region"] = row["Region"]
            df_state_results["Department"] = row["Department"]

        with open(f"{output_path}states_results.csv", mode="a") as f:
            df_state_results.to_csv(
                f, header=f.tell() == 0, index=False, line_terminator="\n"
            )

        df_state_stats = get_poll_statistics(row["Link"])

        if df_state_stats is not None:
            df_state_stats["Region"] = row["Region"]
            df_state_stats["Department"] = row["Department"]

        with open(f"{output_path}states_statistics.csv", mode="a") as f:
            df_state_stats.to_csv(f, header=f.tell() == 0, line_terminator="\n")


def get_overall_poll():
    link = (
        "https://www.resultats-elections.interieur.gouv.fr/presidentielle-2022/FE.html"
    )

    df_overall_results = get_poll_results(link)
    with open(f"{output_path}overall_results.csv", mode="a") as f:
        df_overall_results.to_csv(
            f, header=f.tell() == 0, index=False, line_terminator="\n"
        )

    df_overall_stats = get_poll_statistics(link)
    with open(f"{output_path}overall_statistics.csv", mode="a") as f:
        df_overall_stats.to_csv(f, header=f.tell() == 0, line_terminator="\n")
