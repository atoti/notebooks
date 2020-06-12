import pandas


def optimize_prices(
    initial_price_list: pandas.DataFrame, store_features_with_clusters: pandas.DataFrame
) -> pandas.DataFrame:
    """
    This pricing function has been made very simple as the main purpose is to serve the use case example.
    In real life this would typically be replaced by a more flexible price optimization engine with several parameters,
    such as that of ActiveViam.
    
    Args:
        initial_price_list: The initial SellingPrice list
        sotre_features_with_clusters: A dataframe containing informations about the stores, including their cluster
        
    Returns:
        A new SellingPrice list with an optimized price stores with low competition have increased prices while those with high competition have competitive prices.
    """
    new_price_list = initial_price_list.merge(
        store_features_with_clusters, left_on="StoreId", right_on="StoreId"
    )
    new_price_list.loc[(new_price_list["cluster"] == 0), "SellingPrice"] = (
        new_price_list["SellingPrice"] * 0.97
    )
    new_price_list.loc[(new_price_list["cluster"] == 1), "SellingPrice"] = (
        new_price_list["SellingPrice"] * 1.08
    )
    new_price_list.loc[(new_price_list["cluster"] == 2), "SellingPrice"] = (
        new_price_list["SellingPrice"] * 0.95
    )
    new_price_list.loc[(new_price_list["cluster"] == 3), "SellingPrice"] = (
        new_price_list["SellingPrice"] * 1.00
    )
    new_price_list.loc[(new_price_list["cluster"] == 4), "SellingPrice"] = (
        new_price_list["SellingPrice"] * 1.01
    )
    return new_price_list[["ProductId", "StoreId", "SellingPrice"]]
