from datetime import datetime


def evaluate_claim_period(claim):
    incident_date = datetime.strptime(claim["incident_date"], "%Y-%m-%d")
    if incident_date >= datetime(2023, 1, 1):
        return True
    return False
