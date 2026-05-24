#!/usr/bin/env python3
"""
Stage 3: Deep Synthesis (Agent mode)
Synthesis is performed by the Hermes agent, not via API.
This module is a placeholder for future standalone LLM integration.
"""

import logging

logger = logging.getLogger(__name__)


def run_synthesis(topic: str, tweets_data: list, web_data: list, config: dict):
    """
    Placeholder: synthesis is delegated to Hermes agent.
    The agent reads HERMES_SYNTHESIS_PROMPT.md and writes synthesis.json.
    """
    logger.info("Synthesis delegated to agent. Write synthesis.json to resume.")
    return {}
