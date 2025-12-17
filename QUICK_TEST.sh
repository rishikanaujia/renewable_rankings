#!/bin/bash
# Quick test to verify Brazil scores 7.0
python -c "from src.agents.parameter_agents import analyze_ambition; result = analyze_ambition('Brazil'); print(f'Brazil: {result.score}/10'); assert result.score == 7.0, 'FAIL: Expected 7.0'; print('✅ TEST PASSED!')"
