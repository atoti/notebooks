import random
from datetime import date, timedelta

import pandas as pd


class Helper:
    def __init__(self, session, cube_name):
        self.session = session
        self.cube_name = cube_name
        self.pokemon_ref_df = pd.read_csv(
            "https://data.atoti.io/notebooks/pokemon/pokemon_ref.csv",
            header=0,
            names=[
                "Pokedex",
                "Pokemon",
                "Primary Type",
                "Secondary Type",
                "Against Normal",
                "Against Fire",
                "Against Water",
                "Against Electric",
                "Against Grass",
                "Against Ice",
                "Against Fighting",
                "Against Poison",
                "Against Ground",
                "Against Flying",
                "Against Psychic",
                "Against Bug",
                "Against Rock",
                "Against Ghost",
                "Against Dragon",
                "Against Dark",
                "Against Steel",
                "Against Fairy",
            ],
        )

    def get_last_id(self, id_name):
        """
        This function retrieves the members of the given IDs available in the cube for a new battle.

        Args:
            id_name: Name of ID to retrieve(e.g. Pokemon ID, Registration ID, Combat ID)

        Returns:
            List of members under the given ID.
        """
        mdx = f"SELECT NON EMPTY [Hidden].[{id_name}].[{id_name}].Members ON 0 FROM [{self.cube_name}]"
        df = self.session.query_mdx(
            mdx, keep_totals=False, timeout=timedelta(seconds=30)
        )
        return df.shape[0]

    def is_single_type_pokemon(self, pokemon):
        """
        This function checks if the given Pokémon has a secondary type.

        Args:
            pokemon: Name of Pokémon

        Returns:
            Boolean: True - there is no secondary type, False - There is a secondary type.
        """
        pokemon_secondary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == pokemon, "Secondary Type"
        ].values[0]
        return pd.isna(pokemon_secondary_type)

    def is_single_types_matchup(self, pokemon, opponent):
        """
        This function checks if both the given Pokémon and opponent are of single type.

        Args:
            pokemon: Name of Pokémon,
            opponent: Name of opponent Pokémon

        Returns:
            Boolean: True - both are single type, False - At least one of the Pokémon has a secondary type.
        """
        return self.is_single_type_pokemon(pokemon) and self.is_single_type_pokemon(
            opponent
        )

    def get_pokemon_id(self, pokemon):
        """
        This function returns the Pokedex of the given Pokémon.

        Args:
            pokemon: Name of Pokémon

        Returns:
            Pokedex of the Pokémon .
        """
        return str(
            self.pokemon_ref_df.loc[
                self.pokemon_ref_df["Pokemon"] == pokemon, "Pokedex"
            ].values[0]
        )

    def get_type_multiplier(self, pokemon, opponent_pokemon):
        """
        This function computes the multiplier advantage a Pokémon has against its opponent based on its types.
        Multiplier is predefined in self.pokemon_ref_df.

        Args:
            pokemon: Name of Pokémon,
            opponent: Name of opponent Pokémon

        Returns:
            Multiplier advantage: The average between the primary and secondary type multipliers.
        """
        pokemon_primary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == pokemon, "Primary Type"
        ].values[0]
        pokemon_secondary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == pokemon, "Secondary Type"
        ].values[0]
        primary_multiplier = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == opponent_pokemon,
            f"Against {pokemon_primary_type.capitalize()}",
        ].values[0]
        if pd.isna(pokemon_secondary_type):
            return primary_multiplier
        else:
            secondary_multiplier = self.pokemon_ref_df.loc[
                self.pokemon_ref_df["Pokemon"] == opponent_pokemon,
                f"Against {pokemon_secondary_type.capitalize()}",
            ].values[0]
            return (primary_multiplier + secondary_multiplier) / 2

    def generate_new_battle(self, pokemon, opponent, win):
        """
        This function uploads battle results back into the cube.

        Args:
            pokemon: Name of Pokémon,
            opponent: Name of opponent Pokémon,
            win: The winner of the battle from the get_win_rate endpoint

        Returns:
            None. Results get uploaded into cube directly.
        """
        last_id = self.get_last_id("ID")
        last_reg_id = self.get_last_id("Registration ID")
        combat_id = str(self.get_last_id("Combat ID") + 1)

        # update Combat Info

        location_id = str(random.randint(1, 23))
        _date = date(3006, random.randint(1, 3), random.randint(1, 28))

        rows = []
        rows.append((combat_id, "6", location_id, 0, _date))
        self.session.tables["Combat Info"].append(*rows)

        # update Combats

        pokemon_id = self.get_pokemon_id(pokemon)
        opponent_id = self.get_pokemon_id(opponent)
        result = "WIN" if win else "LOSE"
        type_multiplier = self.get_type_multiplier(pokemon, opponent)
        opponent_result = "LOSE" if win else "WIN"
        opponent_type_multiplier = self.get_type_multiplier(opponent, pokemon)

        rows = []

        rows.append(
            (
                str(last_reg_id + 1),
                combat_id,
                pokemon_id,
                opponent_id,
                result,
                type_multiplier,
                0,
                0,
                0,
                0,
            )
        )
        rows.append(
            (
                str(last_reg_id + 2),
                combat_id,
                opponent_id,
                pokemon_id,
                opponent_result,
                opponent_type_multiplier,
                0,
                0,
                0,
                0,
            )
        )

        self.session.tables["Combats"].append(*rows)

        # update Types

        pokemon_primary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == pokemon, "Primary Type"
        ].values[0]
        pokemon_secondary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == pokemon, "Secondary Type"
        ].values[0]
        opponent_primary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == opponent, "Primary Type"
        ].values[0]
        opponent_secondary_type = self.pokemon_ref_df.loc[
            self.pokemon_ref_df["Pokemon"] == opponent, "Secondary Type"
        ].values[0]

        if pd.isna(pokemon_secondary_type):
            pokemon_secondary_type = pokemon_primary_type
        if pd.isna(opponent_secondary_type):
            opponent_secondary_type = opponent_primary_type

        rows = []

        if self.is_single_types_matchup(pokemon, opponent):
            rows.append(
                (
                    str(last_id + 1),
                    pokemon_primary_type,
                    opponent_primary_type,
                    str(last_reg_id + 1),
                )
            )
            rows.append(
                (
                    str(last_id + 2),
                    opponent_primary_type,
                    pokemon_primary_type,
                    str(last_reg_id + 2),
                )
            )
        else:
            rows.append(
                (
                    str(last_id + 1),
                    pokemon_primary_type,
                    opponent_primary_type,
                    str(last_reg_id + 1),
                )
            )
            rows.append(
                (
                    str(last_id + 2),
                    pokemon_secondary_type,
                    opponent_secondary_type,
                    str(last_reg_id + 1),
                )
            )
            rows.append(
                (
                    str(last_id + 3),
                    opponent_primary_type,
                    pokemon_primary_type,
                    str(last_reg_id + 2),
                )
            )
            rows.append(
                (
                    str(last_id + 4),
                    opponent_secondary_type,
                    pokemon_secondary_type,
                    str(last_reg_id + 2),
                )
            )

        self.session.tables["Types"].append(*rows)
