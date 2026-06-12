"""Policies package — track-specific decision adapters.

Policy modules consume shared orchestration output and translate it
into track-specific decisions.  This package is intentionally mixed-purity:

  * policies/manual_report.py  — no execution imports (pure stdlib + contracts)
  * policies/reverse_planner.py — no execution imports (pure stdlib)
  * policies/demo_execution.py — allowed to import RiskManager, PositionManager,
    PortfolioContextBuilder, and other execution-side concerns

Do NOT relax the purity guarantee for manual_report or reverse_planner
without a deliberate architecture discussion.
"""
