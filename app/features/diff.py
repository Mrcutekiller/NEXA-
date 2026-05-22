# app/features/diff.py
import difflib
from typing import Dict, List, Any

class NexaDiff:
    def analyze_diff(self, old_code: str, new_code: str) -> str:
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        
        diff = list(difflib.ndiff(old_lines, new_lines))
        
        added_count = 0
        removed_count = 0
        changed_details = []
        warnings = []
        
        # Parse diff lines
        for i, line in enumerate(diff):
            if line.startswith("+ "):
                added_count += 1
                content = line[2:].strip()
                if "try" in content or "except" in content:
                    changed_details.append(f"Line {i+1}: added error handling (✓ safer)")
                elif "assert" in content or "if not" in content or "raise " in content:
                    changed_details.append(f"Line {i+1}: added validation logic (✓ good addition)")
                elif ":" in content and ("->" in content or "int" in content or "str" in content or "dict" in content):
                    changed_details.append(f"Line {i+1}: added type hints (✓ better)")
            elif line.startswith("- "):
                removed_count += 1
                content = line[2:].strip()
                if "try" in content or "except" in content:
                    warnings.append(f"removed error handling on line {i+1} (⚠ risk: may crash on bad input)")
                    changed_details.append(f"Line {i+1}: removed error handling (⚠ warning)")
                elif "print" in content:
                    changed_details.append(f"Line {i+1}: removed debug print statement")
            elif line.startswith("? "):
                # Meta info from ndiff about inline changes
                pass

        # Risk and verdict calculation
        risk_level = "Low"
        verdict = "Improved ✓"
        recommendations = ["Code structure looks clean and updated."]

        if warnings:
            risk_level = "Medium ⚠"
            verdict = f"Improved ✓ (with {len(warnings)} warning/s)"
            recommendations = [f"Add back the removed logic: {w}" for w in warnings]
        elif added_count == 0 and removed_count > 0:
            verdict = "Simplified ✓"
            recommendations = ["Cleaned up unused code blocks."]

        details_str = "\n  ".join(changed_details[:6]) if changed_details else "No major structural changes found (formatting only)."
        rec_str = "\n  ".join(recommendations)

        return f"""
DIFF ANALYSIS
─────────────
Lines changed:    {added_count + removed_count}
Lines added:      {added_count}
Lines removed:    {removed_count}

WHAT CHANGED:
  {details_str}

OVERALL VERDICT:  {verdict}
RISK LEVEL:       {risk_level}

RECOMMENDATION:
  {rec_str}
"""
