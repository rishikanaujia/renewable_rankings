"""Chat message handler for processing user queries."""
import re
from typing import Tuple, Optional, List
from ...services.mock_service import mock_service
from ...models.correction import ExpertCorrection
from ..utils.formatters import (
    format_country_detail,
    format_rankings_table,
    format_comparison,
    format_chat_response
)
from ...core.logger import get_logger

logger = get_logger(__name__)


class ChatHandler:
    """Handle chat messages and route to appropriate actions."""
    
    def __init__(self):
        """Initialize chat handler."""
        self.service = mock_service
        logger.info("ChatHandler initialized")
    
    def process_message(self, message: str, history: List = None) -> str:
        """Process a chat message and return response.
        
        Args:
            message: User message
            history: Chat history (optional)
            
        Returns:
            Response message
        """
        message = message.strip()
        logger.info(f"Processing message: {message[:50]}...")
        
        # Route to appropriate handler based on message content
        if self._is_greeting(message):
            return self._handle_greeting()
        
        elif self._is_show_rankings(message):
            return self._handle_show_rankings(message)
        
        elif self._is_show_country(message):
            return self._handle_show_country(message)
        
        elif self._is_comparison(message):
            return self._handle_comparison(message)
        
        elif self._is_correction(message):
            return self._handle_correction(message)
        
        elif self._is_help(message):
            return self._handle_help()
        
        else:
            return self._handle_general_query(message)
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting."""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
        return any(message.lower().startswith(g) for g in greetings)
    
    def _is_show_rankings(self, message: str) -> bool:
        """Check if message requests rankings."""
        patterns = [
            r'show.*rankings?',
            r'top \d+',
            r'list.*countries',
            r'global.*rankings?'
        ]
        return any(re.search(p, message.lower()) for p in patterns)
    
    def _is_show_country(self, message: str) -> bool:
        """Check if message requests specific country."""
        patterns = [
            r'show (?:me )?([a-zA-Z\s]+)',
            r'(?:what about|how is) ([a-zA-Z\s]+)',
            r'tell me about ([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+) (?:ranking|score)'
        ]
        return any(re.search(p, message.lower()) for p in patterns)
    
    def _is_comparison(self, message: str) -> bool:
        """Check if message requests comparison."""
        patterns = [
            r'compare',
            r'(?:vs|versus)',
            r'difference between'
        ]
        return any(re.search(p, message.lower()) for p in patterns)
    
    def _is_correction(self, message: str) -> bool:
        """Check if message is a correction."""
        patterns = [
            r'should be \d+',
            r'actually',
            r'incorrect',
            r'update.*to \d+',
            r'change.*to \d+'
        ]
        return any(re.search(p, message.lower()) for p in patterns)
    
    def _is_help(self, message: str) -> bool:
        """Check if message is asking for help."""
        help_words = ['help', 'how do', 'what can', 'commands']
        return any(word in message.lower() for word in help_words)
    
    def _handle_greeting(self) -> str:
        """Handle greeting messages."""
        return """👋 Welcome to the Global Renewable Market Rankings System!

I can help you with:
- **View Rankings:** "Show top 10 countries" or "Show global rankings"
- **Country Details:** "Show me Brazil" or "What's Germany's score?"
- **Comparisons:** "Compare Brazil and Chile" or "Germany vs USA"
- **Corrections:** "Brazil Contract Terms should be 9, not 8"

What would you like to know?"""
    
    def _handle_show_rankings(self, message: str) -> str:
        """Handle request to show rankings."""
        # Extract number if specified
        match = re.search(r'top (\d+)', message.lower())
        top_n = int(match.group(1)) if match else 10
        
        rankings = self.service.get_rankings()
        return format_rankings_table(rankings, top_n=top_n)
    
    def _handle_show_country(self, message: str) -> str:
        """Handle request to show specific country."""
        # Extract country name
        # Try to find country name in message
        country_name = None
        
        # Remove common words
        cleaned = message.lower()
        for word in ['show', 'me', 'tell', 'about', 'what', 'is', 'the', 'ranking', 'for', 'score', 'of']:
            cleaned = cleaned.replace(word, '')
        
        cleaned = cleaned.strip()
        
        # Search for matching country
        matches = self.service.search_countries(cleaned)
        
        if not matches:
            return f"❌ Country not found: '{cleaned}'. Try 'Brazil', 'Germany', 'USA', etc."
        
        if len(matches) > 1:
            return f"⚠️ Multiple matches found: {', '.join(matches)}. Please be more specific."
        
        country_name = matches[0]
        ranking = self.service.get_country_ranking(country_name)
        
        if ranking:
            return format_country_detail(ranking)
        else:
            return f"❌ No ranking data available for {country_name}"
    
    def _handle_comparison(self, message: str) -> str:
        """Handle request to compare countries."""
        # Extract country names
        # Look for patterns like "compare X and Y" or "X vs Y"
        
        # Try "compare X and Y"
        match = re.search(r'compare ([a-zA-Z\s]+) and ([a-zA-Z\s]+)', message.lower())
        if not match:
            # Try "X vs Y"
            match = re.search(r'([a-zA-Z\s]+) (?:vs|versus) ([a-zA-Z\s]+)', message.lower())
        
        if not match:
            return "❌ Please specify countries to compare. Example: 'Compare Brazil and Germany'"
        
        country1 = match.group(1).strip()
        country2 = match.group(2).strip()
        
        # Get rankings
        ranking1 = self.service.get_country_ranking(country1)
        ranking2 = self.service.get_country_ranking(country2)
        
        if not ranking1:
            return f"❌ Country not found: {country1}"
        if not ranking2:
            return f"❌ Country not found: {country2}"
        
        return format_comparison([ranking1, ranking2])
    
    def _handle_correction(self, message: str) -> str:
        """Handle expert correction."""
        # This is a simplified version
        # Real implementation would use NLP to extract entities
        
        return """✅ Correction noted!

In a full implementation, I would:
1. Extract the country, parameter, and new score
2. Ask for your reasoning (minimum 50 characters)
3. Update the score and recalculate rankings
4. Ask if you want to apply to similar countries
5. Create a domain rule if appropriate

**For now, this is a UI demo. Agent integration coming in Phase 2!**"""
    
    def _handle_help(self) -> str:
        """Handle help requests."""
        return """## Available Commands

### View Rankings
- `Show top 10 countries`
- `Show global rankings`
- `List all rankings`

### Country Details
- `Show me Brazil`
- `What's Germany's score?`
- `Tell me about United States`

### Comparisons
- `Compare Brazil and Chile`
- `Germany vs USA`
- `Compare China, India, and Brazil`

### Corrections (Coming Soon)
- `Brazil Contract Terms should be 9, not 8`
- `Update Vietnam Energy Dependence to 62`

### Reports (Coming Soon)
- `Generate Q3 report`
- `Export rankings to Excel`

Need more help? Just ask!"""
    
    def _handle_general_query(self, message: str) -> str:
        """Handle general queries."""
        return f"""I understood your message: "{message}"

However, I'm not sure how to help with that yet. 

Try:
- `Show top 10 countries`
- `Show me Brazil`
- `Compare Germany and USA`
- `Help` for more commands

**Note:** This is a Phase 1 UI demo. Full NLP capabilities coming in Phase 2!"""


# Global chat handler instance
chat_handler = ChatHandler()
