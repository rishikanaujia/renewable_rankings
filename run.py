#!/usr/bin/env python3
"""Simple run script for the Gradio UI."""

if __name__ == "__main__":
    # Load environment variables FIRST, before any imports
    from dotenv import load_dotenv
    load_dotenv()

    # Now import and run the app
    from src.ui.app import main
    main()
