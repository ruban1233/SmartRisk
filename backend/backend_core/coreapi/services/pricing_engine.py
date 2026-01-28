def intrinsic_value(spot, strike, option_type):
    if option_type == "CE":
        return max(0, spot - strike)
    return max(0, strike - spot)

def extrinsic_value(option_price, intrinsic):
    return max(0, option_price - intrinsic)
