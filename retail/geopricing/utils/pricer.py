def pricing_function(price: float, cluster: int) -> float:
    if cluster == 0:
        return price * 1.07
    elif cluster == 1:
        return price * 1.08
    elif cluster == 2:
        return price * 1.05
    elif cluster == 3:
        return price * 1.07
    elif cluster == 4:
        return price * 1.07
    else:
        return price
