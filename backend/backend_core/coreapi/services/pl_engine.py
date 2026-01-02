def calculate_pl(entry, exit, target, stoploss, quantity):
    
    pl_value = (exit - entry) * quantity

    status = "profit" if pl_value > 0 else "loss"

    return {
        "entry": entry,
        "exit": exit,
        "target": target,
        "stoploss": stoploss,
        "quantity": quantity,
        "pnl": pl_value,
        "status": status
    }
