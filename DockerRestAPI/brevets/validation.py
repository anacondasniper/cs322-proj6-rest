def validate_controls(rows, brevet_dist):
    """Return an error message string, or None if everything is valid."""
    if not rows:
        return "No controls to submit"
    for row in rows:
        try:
            km = float(row["km"])
        except (ValueError, KeyError, TypeError):
            return "Invalid km value"
        if km < 0:
            return "Km cannot be negative"
        if km > brevet_dist * 1.2:
            return "Control at {} km is more than 20% past the {} km brevet".format(
                row["km"], brevet_dist)
    return None
