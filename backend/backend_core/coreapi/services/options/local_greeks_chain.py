from coreapi.services.greeks_engine import compute_greeks


def generate_strikes(spot, step=50, range_size=10):
    """
    Generate strikes around ATM
    """
    atm = round(spot / step) * step

    strikes = []
    for i in range(-range_size, range_size + 1):
        strikes.append(atm + i * step)

    return sorted(strikes)


def build_greeks_chain(spot, expiry_days=5, iv=0.2, r=0.05):
    """
    Build full option chain Greeks (fallback engine)
    """

    strikes = generate_strikes(spot)

    chain = []

    T = expiry_days / 365

    for strike in strikes:

        ce = compute_greeks(
            S=spot,
            K=strike,
            T=T,
            r=r,
            sigma=iv,
            option_type="CE"
        )

        pe = compute_greeks(
            S=spot,
            K=strike,
            T=T,
            r=r,
            sigma=iv,
            option_type="PE"
        )

        chain.append({
            "strike": strike,
            "ce": ce,
            "pe": pe
        })

    return chain