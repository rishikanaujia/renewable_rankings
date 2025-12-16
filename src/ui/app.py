"""Main Gradio application for Renewable Energy Rankings."""
import gradio as gr
from typing import List
import os
from pathlib import Path

from .handlers.chat_handler import chat_handler
from .utils.formatters import format_rankings_table
from ..services.mock_service import mock_service
from ..core.config_loader import config_loader
from ..core.logger import setup_logger, get_logger

# Setup logging
setup_logger(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/app.log")
)
logger = get_logger(__name__)


class RankingsApp:
    """Main Gradio application."""

    def __init__(self):
        """Initialize the application."""
        self.config = config_loader.get_app_config()
        self.service = mock_service
        logger.info("RankingsApp initialized")

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface.
        
        Returns:
            Gradio Blocks interface
        """

        with gr.Blocks(
                title=self.config['ui']['title'],
        ) as interface:
            # Header
            gr.Markdown(f"""
            # 🌍 {self.config['app']['name']}
            **{self.config['app']['description']}**
            
            *Version {self.config['app']['version']} - Phase 1 UI Demo*
            """)

            # Main tabs
            with gr.Tabs():
                # Tab 1: Chat Interface
                with gr.TabItem("💬 Chat Assistant"):
                    gr.Markdown("""
                    ### Ask questions in natural language!
                    
                    **Try these:**
                    - "Show me top 10 countries"
                    - "What's Brazil's score?"
                    - "Compare Germany and USA"
                    """)

                    chatbot = gr.Chatbot(
                        label="Rankings Assistant",
                        height=500,
                        show_label=True
                    )

                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Ask me anything about renewable energy rankings...",
                            scale=4
                        )
                        submit = gr.Button("Send", variant="primary", scale=1)

                    with gr.Row():
                        clear = gr.Button("Clear Chat")

                    # Example buttons
                    gr.Markdown("**Quick Examples:**")
                    with gr.Row():
                        ex1 = gr.Button("Show top 10")
                        ex2 = gr.Button("Show me Brazil")
                        ex3 = gr.Button("Compare Brazil and Germany")
                        ex4 = gr.Button("Help")

                    # Chat handling
                    def respond(message: str, history: List):
                        """Handle chat message."""
                        response = chat_handler.process_message(message, history)
                        # Gradio 4.0+ format: list of dicts with 'role' and 'content'
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": response})
                        return "", history

                    # Event handlers
                    msg.submit(respond, [msg, chatbot], [msg, chatbot])
                    submit.click(respond, [msg, chatbot], [msg, chatbot])
                    clear.click(lambda: None, None, chatbot, queue=False)

                    # Example button handlers
                    def set_example(example_text: str, history: List):
                        """Set example text and empty history for fresh start."""
                        return example_text, []

                    ex1.click(lambda h: set_example("Show top 10", h), [chatbot], [msg, chatbot]).then(
                        respond, [msg, chatbot], [msg, chatbot]
                    )
                    ex2.click(lambda h: set_example("Show me Brazil", h), [chatbot], [msg, chatbot]).then(
                        respond, [msg, chatbot], [msg, chatbot]
                    )
                    ex3.click(lambda h: set_example("Compare Brazil and Germany", h), [chatbot], [msg, chatbot]).then(
                        respond, [msg, chatbot], [msg, chatbot]
                    )
                    ex4.click(lambda h: set_example("Help", h), [chatbot], [msg, chatbot]).then(
                        respond, [msg, chatbot], [msg, chatbot]
                    )

                # Tab 2: Rankings Table
                with gr.TabItem("📊 Global Rankings"):
                    gr.Markdown("### View and explore global renewable market rankings")

                    with gr.Row():
                        period_dropdown = gr.Dropdown(
                            choices=["Q3 2024", "Q2 2024", "Q1 2024"],
                            value="Q3 2024",
                            label="Period"
                        )
                        top_n_slider = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=5,
                            label="Number of countries to show"
                        )
                        refresh_btn = gr.Button("Refresh", variant="secondary")

                    rankings_display = gr.Markdown(
                        value=self._get_initial_rankings()
                    )

                    def update_rankings(period: str, top_n: int):
                        """Update rankings display."""
                        rankings = self.service.get_rankings(period)
                        return format_rankings_table(rankings, top_n=int(top_n))

                    # Event handlers
                    period_dropdown.change(
                        update_rankings,
                        [period_dropdown, top_n_slider],
                        rankings_display
                    )
                    top_n_slider.change(
                        update_rankings,
                        [period_dropdown, top_n_slider],
                        rankings_display
                    )
                    refresh_btn.click(
                        update_rankings,
                        [period_dropdown, top_n_slider],
                        rankings_display
                    )

                # Tab 3: Country Details
                with gr.TabItem("🔍 Country Details"):
                    gr.Markdown("### Deep dive into individual country rankings")

                    with gr.Row():
                        country_search = gr.Textbox(
                            label="Search Country",
                            placeholder="Type country name...",
                            scale=3
                        )
                        search_btn = gr.Button("Search", variant="primary", scale=1)

                    country_display = gr.Markdown(
                        value="*Select a country to view details*"
                    )

                    # Quick access buttons
                    gr.Markdown("**Quick Access:**")
                    with gr.Row():
                        for country in ["Brazil", "Germany", "USA", "China", "India"]:
                            btn = gr.Button(country, size="sm")
                            btn.click(
                                lambda c=country: self._get_country_details(c),
                                None,
                                country_display
                            )

                    def search_country(name: str):
                        """Search and display country."""
                        return self._get_country_details(name)

                    country_search.submit(search_country, country_search, country_display)
                    search_btn.click(search_country, country_search, country_display)

                # Tab 4: About & Documentation
                with gr.TabItem("ℹ️ About"):
                    gr.Markdown("""
                    ## About This System
                    
                    This is the **Phase 1 UI Demo** of the Global Renewable Market Rankings System.
                    
                    ### Features
                    
                    **Current (Phase 1):**
                    - ✅ Interactive chat interface
                    - ✅ Global rankings view
                    - ✅ Country detail pages
                    - ✅ Natural language queries
                    - ✅ Mock data for testing
                    
                    **Coming Soon (Phase 2):**
                    - 🔄 Real AI agents (21 parameter analysts)
                    - 🔄 Expert correction workflow
                    - 🔄 Domain rule creation
                    - 🔄 Memory system integration
                    - 🔄 Report generation (PDF/Excel)
                    
                    **Future (Phase 3):**
                    - 📅 Voice input
                    - 📅 Mobile optimization
                    - 📅 Advanced analytics
                    - 📅 Batch operations
                    
                    ### Architecture
                    
                    - **21 Parameters** across 6 subcategories
                    - **3 Priority Levels** (Critical, Important, Modifiers)
                    - **32 AI Agents** (multi-agent system)
                    - **5 Memory Types** (knowledge capture)
                    
                    ### Technology Stack
                    
                    - **UI:** Gradio 4.0
                    - **Backend:** Python + FastAPI (Phase 2)
                    - **AI:** LangChain + LangGraph (Phase 2)
                    - **Memory:** PostgreSQL + Redis + ChromaDB (Phase 2)
                    - **LLM:** Azure OpenAI / Claude (Phase 2)
                    
                    ### Contact & Feedback
                    
                    This system is being developed to help renewable energy investors
                    make better decisions with AI-powered analysis.
                    
                    **Version:** {version}  
                    **Status:** Phase 1 - UI Demo  
                    **Next Update:** Phase 2 - Agent Integration
                    """.format(version=self.config['app']['version']))

            # Footer
            gr.Markdown("""
            ---
            *Built with ❤️ for renewable energy investors. Powered by AI.*
            """)

        return interface

    def _get_initial_rankings(self) -> str:
        """Get initial rankings display."""
        rankings = self.service.get_rankings()
        return format_rankings_table(rankings, top_n=10)

    def _get_country_details(self, country_name: str) -> str:
        """Get country details for display."""
        from .utils.formatters import format_country_detail

        ranking = self.service.get_country_ranking(country_name)
        if ranking:
            return format_country_detail(ranking)
        else:
            return f"❌ Country not found: {country_name}"

    def launch(
            self,
            server_name: str = "0.0.0.0",
            server_port: int = 7860,
            share: bool = False,
            debug: bool = False
    ):
        """Launch the Gradio application.
        
        Args:
            server_name: Server hostname
            server_port: Server port
            share: Whether to create a public link
            debug: Enable debug mode
        """
        interface = self.create_interface()
        # Custom CSS for better styling
        custom_css = """
                .gradio-container {
                    font-family: 'Arial', sans-serif;
                }
                .chat-message {
                    padding: 10px;
                    border-radius: 5px;
                    margin: 5px 0;
                }
                .highlight {
                    background-color: #e3f2fd;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
                """

        logger.info(f"Launching app on {server_name}:{server_port}")

        interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug,
            show_error=True,
            theme=self.config["ui"]["theme"],  # ✅ moved here
            css=custom_css,  # ✅ moved here

        )


def main():
    """Main entry point."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Create and launch app
    app = RankingsApp()
    app.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", 7860)),
        share=os.getenv("GRADIO_SHARE", "False").lower() == "true",
        debug=os.getenv("DEBUG", "False").lower() == "true"
    )


if __name__ == "__main__":
    main()
