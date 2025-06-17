# leavebot/domain/air_ticket.py

from typing import Dict, List, Any

class AirTicketEligibility:
    """
    Check air ticket eligibility based on mapped context.
    """

    def __init__(self, leave_balances: Dict[str, Any], leave_types: List[Dict[str, Any]]):
        self.leave_balances = leave_balances
        self.leave_types = leave_types
        self.code_to_desc = {lt["code"]: lt["desc"] for lt in leave_types}

    def eligible_leaves(self) -> List[Dict[str, Any]]:
        """
        Returns list of leave codes/descriptions where air_ticket is True.
        """
        eligible = []
        for code, info in self.leave_balances.items():
            if info.get("air_ticket"):
                eligible.append({
                    "code": code,
                    "desc": self.code_to_desc.get(code, code),
                    "percent": info.get("air_ticket_percent", 0),
                })
        return eligible

    from typing import Tuple

    def is_eligible(self, leave_query: str) -> Tuple[bool, str]:
        """
        Query by leave code (e.g., 'AL') or description.
        Returns (True/False, message).
        """
        q = leave_query.strip().upper()
        info = self.leave_balances.get(q)
        if not info:
            # Try match on description
            q_lower = leave_query.strip().lower()
            for code, desc in self.code_to_desc.items():
                if q_lower in desc.lower():
                    info = self.leave_balances.get(code)
                    q = code
                    break
        if info and info.get("air_ticket"):
            return True, f"Eligible for air ticket on {self.code_to_desc.get(q, q)} ({info.get('air_ticket_percent', 0)}%)."
        elif info:
            return False, f"Not eligible for air ticket on {self.code_to_desc.get(q, q)}."
        return False, "Leave type not found."

    def percent_for(self, leave_query: str) -> float:
        """
        Return air ticket percent for the given leave (if eligible), else 0.
        """
        q = leave_query.strip().upper()
        info = self.leave_balances.get(q)
        if not info:
            # Try by description
            q_lower = leave_query.strip().lower()
            for code, desc in self.code_to_desc.items():
                if q_lower in desc.lower():
                    info = self.leave_balances.get(code)
                    break
        if info and info.get("air_ticket"):
            return info.get("air_ticket_percent", 0)
        return 0

# --- Usage Example (for manual/CLI testing) ---
if __name__ == "__main__":
    import json

    # Load your mapped context
    with open("leavebot/data/mapped_context.json", "r", encoding="utf-8") as f:
        context = json.load(f)

    helper = AirTicketEligibility(
        leave_balances=context["leave_balances"],
        leave_types=context["leave_types"]
    )

    print("All leaves with air ticket eligibility:")
    for leave in helper.eligible_leaves():
        print(leave)

    print("\nCheck eligibility for 'annual leave':")
    print(helper.is_eligible("annual leave"))

    print("\nCheck eligibility for 'CL':")
    print(helper.is_eligible("CL"))

    print("\nAir ticket percent for 'AL':")
    print(helper.percent_for("AL"))
