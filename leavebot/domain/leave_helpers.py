from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class LeaveHelpers:
    def __init__(self, leave_balances: Dict[str, Any], leave_types: List[Dict[str, Any]]):
        self.leave_balances = leave_balances
        self.leave_types = {lt["code"]: lt for lt in leave_types}
        self.code_to_desc = {lt["code"]: lt["desc"] for lt in leave_types}
        self.desc_to_code = {lt["desc"].lower(): lt["code"] for lt in leave_types}

    def can_apply_for(self, leave_query: str) -> Tuple[bool, str]:
        """Check if user can apply for a leave type (by code or description)."""
        code = self._resolve_code(leave_query)
        if not code:
            return False, f"Leave type '{leave_query}' not found."
        info = self.leave_balances.get(code)
        if not info or info.get("balance", 0) <= 0:
            return False, f"You do not have sufficient balance for {self.code_to_desc[code]}."
        return True, f"You can apply for {self.code_to_desc[code]}. Your balance: {info.get('balance')} days."

    def air_ticket_with(self, leave_query: str) -> Tuple[bool, str]:
        """Check if the leave type grants air ticket."""
        code = self._resolve_code(leave_query)
        if not code:
            return False, f"Leave type '{leave_query}' not found."
        info = self.leave_balances.get(code)
        if info and info.get("air_ticket"):
            return True, f"Air ticket is granted with {self.code_to_desc[code]} ({info.get('air_ticket_percent', 0)}%)."
        return False, f"Air ticket is NOT granted with {self.code_to_desc.get(code, leave_query)}."

    def leave_types_on_workday(self) -> List[Dict[str, Any]]:
        """List leaves that are eligible to be applied on workdays."""
        return [
            {"code": lt["code"], "desc": lt["desc"]}
            for lt in self.leave_types.values()
            if lt.get("eligibility_on_workdays")
        ]

    def needs_attachment(self, leave_query: str) -> Tuple[Optional[bool], str]:
        """Check if the leave type needs an attachment."""
        code = self._resolve_code(leave_query)
        if not code:
            return None, f"Leave type '{leave_query}' not found."
        attach_required = self.leave_types[code].get("attach_required", False)
        msg = (
            f"{self.code_to_desc[code]} requires an attachment."
            if attach_required
            else f"{self.code_to_desc[code]} does NOT require an attachment."
        )
        return attach_required, msg

    def is_self_service(self, leave_query: str) -> Tuple[Optional[bool], str]:
        """Check if a leave is self-service."""
        code = self._resolve_code(leave_query)
        if not code:
            return None, f"Leave type '{leave_query}' not found."
        self_service = self.leave_types[code].get("self_service", False)
        msg = (
            f"{self.code_to_desc[code]} can be applied by self-service."
            if self_service
            else f"{self.code_to_desc[code]} requires manager processing."
        )
        return self_service, msg

    def all_air_ticket_leaves(self) -> List[Dict[str, Any]]:
        """List all leave types that provide air ticket."""
        return [
            {"code": code, "desc": self.code_to_desc.get(code, code), "percent": info.get("air_ticket_percent", 0)}
            for code, info in self.leave_balances.items()
            if info.get("air_ticket")
        ]

    def leaves_requiring_attachment(self) -> List[Dict[str, Any]]:
        """List all leave types that require an attachment."""
        return [
            {"code": code, "desc": lt["desc"]}
            for code, lt in self.leave_types.items()
            if lt.get("attach_required", False)
        ]

    def leave_balances_summary(self) -> List[Dict[str, Any]]:
        """Summary of all leave types with balances."""
        summary = []
        for code, info in self.leave_balances.items():
            summary.append({
                "code": code,
                "desc": self.code_to_desc.get(code, code),
                "balance": info.get("balance", 0),
                "eligible": info.get("eligible", 0),
                "air_ticket": info.get("air_ticket", False),
                "attach_required": self.leave_types[code].get("attach_required", False),
            })
        return summary

    def next_eligible_date(self, leave_query: str) -> Tuple[str, str]:
        """
        Returns (date string or 'Now', message) when user can next apply for this leave.
        Considers anniv_date and zero balance.
        """
        code = self._resolve_code(leave_query)
        if not code:
            return "", f"Leave type '{leave_query}' not found."
        info = self.leave_balances.get(code)
        if not info:
            return "", f"No balance info for {code}."
        if info.get("balance", 0) > 0:
            return "Now", f"You can apply for {self.code_to_desc[code]} immediately."
        anniv = info.get("anniv_date")
        if anniv:
            try:
                anniv_dt = datetime.strptime(anniv, "%d-%b-%Y")
                if anniv_dt > datetime.now():
                    return anniv, f"You can apply for {self.code_to_desc[code]} after {anniv}."
            except Exception:
                pass
        return "", f"You are not eligible for {self.code_to_desc[code]} at the moment."

    def suggest_alternative_leave(self, leave_query: str) -> Tuple[Optional[str], str]:
        """
        Suggests another leave type if the requested leave has zero balance.
        """
        code = self._resolve_code(leave_query)
        if not code or self.leave_balances.get(code, {}).get("balance", 0) > 0:
            return None, ""
        # Find alternative
        alternatives = [
            self.code_to_desc.get(c, c)
            for c, info in self.leave_balances.items()
            if info.get("balance", 0) > 0 and c != code
        ]
        if alternatives:
            return alternatives[0], f"You have no balance in {self.code_to_desc.get(code, code)}. Consider applying for {alternatives[0]} instead."
        else:
            return None, "You do not have sufficient balance in any leave type."

    def _resolve_code(self, leave_query: str) -> Optional[str]:
        """Resolves leave code from code or description (case-insensitive, substring allowed)."""
        q = leave_query.strip().upper()
        if q in self.leave_types:
            return q
        # Try by description (case-insensitive, substring match)
        q_lower = leave_query.strip().lower()
        for code, desc in self.code_to_desc.items():
            if q_lower in desc.lower():
                return code
        return None

# --- Usage Example (for CLI/manual tests) ---
if __name__ == "__main__":
    import json

    with open("leavebot/data/mapped_context.json", "r", encoding="utf-8") as f:
        ctx = json.load(f)

    helper = LeaveHelpers(ctx["leave_balances"], ctx["leave_types"])

    # 1. Can I apply for casual leave?
    print(helper.can_apply_for("casual leave"))    # Or helper.can_apply_for("CL")

    # 2. Can I get air ticket with casual leave?
    print(helper.air_ticket_with("casual leave"))

    # 3. Which leaves can I apply on workday?
    print("Leaves you can apply on workday:")
    for lt in helper.leave_types_on_workday():
        print(f"- {lt['code']}: {lt['desc']}")

    # 4. Does the leave I am applying for need an attachment?
    print(helper.needs_attachment("casual leave"))
    print(helper.needs_attachment("annual leave"))

    # 5. Is annual leave self-service?
    print(helper.is_self_service("annual leave"))

    # 6. Show all leave types that provide air ticket
    print(helper.all_air_ticket_leaves())

    # 7. List leave types requiring attachment
    print(helper.leaves_requiring_attachment())

    # 8. Show leave balance summary
    print(helper.leave_balances_summary())

    # 9. When can I next apply for 'annual leave'
    print(helper.next_eligible_date("annual leave"))

    # 10. Suggest alternative if 'CL' balance is zero
    print(helper.suggest_alternative_leave("CL"))
