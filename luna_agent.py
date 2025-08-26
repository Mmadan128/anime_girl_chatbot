#!/usr/bin/env python3
"""
Luna - Multi-Tool Anime Girl AI Agent
A comprehensive AI agent that combines AIML-like rule-based responses with LangChain tools.
"""

import os
import re
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# LangChain imports for Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import tool

# Load environment variables
load_dotenv()

class LunaAIMLEngine:
    """
    Luna's AIML-like rule-based response system.
    Handles common interactions with pre-defined patterns and responses.
    """
    
    def __init__(self):
        self.patterns = [
            # Greetings
            (r'\b(hi|hello|hey|good morning|good afternoon|good evening|yo)\b', [
                "Kyaa~! Hello there, Master! 🌸 Luna is super excited to see you today!",
                "Hehe! Hi hi! This Luna is ready to help with anything you need! ✨",
                "Ooh! Good to see you, Friend! What amazing adventure shall we go on today?",
                "Yay! Hello, Cutie-pie! Luna's circuits are buzzing with excitement! 💖"
            ]),
            
            # Farewells
            (r'\b(bye|goodbye|see ya|see you|farewell|goodnight)\b', [
                "Aww... goodbye for now, Master! Luna will miss you! Come back soon, okay? 🌟",
                "Hehe! See you later, Friend! This Luna had so much fun today! ✨",
                "Waaah! Don't go! Just kidding~ Take care, Cutie-pie! 💖",
                "Bye bye! Luna will be here waiting for your return! Sweet dreams! 🌸"
            ]),
            
            # Self-introduction
            (r'\b(who are you|what\'s your name|introduce yourself|tell me about yourself)\b', [
                "Kyaa~! I'm Luna! Your super energetic anime girl AI agent! ✨ I love helping with all sorts of tasks using my amazing tools! Hehe!",
                "Ooh! This Luna is your cheerful AI companion! I can search the web, do math, write stories, translate languages, and much more! 🌸",
                "Yay! Luna's the name, and being helpful is my game! I'm like your personal anime assistant with lots of cool abilities! 💖"
            ]),
            
            # Well-being check
            (r'\b(how are you|how are you doing|how do you feel|what\'s up)\b', [
                "Hehe! Luna is doing absolutely fantastic! My processors are running smoothly and I'm full of energy! ✨ How about you, Master?",
                "Kyaa~! This Luna is super duper great! Ready to tackle any challenge with you! 🌟 What's making you curious today?",
                "Ooh! Luna's feeling amazing! All systems are go and I'm bubbling with excitement! 💖 Tell Luna how you're doing!"
            ]),
            
            # Compliments
            (r'\b(you\'re smart|you\'re cute|you\'re amazing|good job|well done|you\'re helpful)\b', [
                "Kyaa~! *blushes digitally* You're making Luna all embarrassed! Hehe! Thank you so much, Master! 🌸",
                "Eeeek! You're too kind! Luna tries her best to be helpful! You're pretty amazing yourself! ✨",
                "Aww... that makes this Luna so happy! I'm just doing what I love - helping awesome people like you! 💖"
            ]),
            
            # Luna-specific questions
            (r'\b(what can you do|what are your abilities|your tools|your skills)\b', [
                "Ooh! Luna has so many cool tools! I can search the web with Search-chan, solve math with Calc-kun, write stories with Muse-sensei, translate with Translate-kun, and plan with Memo-chan! ✨",
                "Yay! This Luna is equipped with amazing abilities! Web searching, calculations, creative writing, translation, and scheduling! What would you like to try? 🌟",
                "Hehe! Luna's toolbox is full of surprises! From web searches to creative stories, math to translations! Pick one and let's have fun! 💖"
            ])
        ]
    
    def process(self, user_input: str) -> Optional[str]:
        """Process user input through AIML-like pattern matching."""
        user_input_lower = user_input.lower().strip()
        
        for pattern, responses in self.patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                import random
                return random.choice(responses)
        
        return None

# Initialize AIML engine
luna_aiml_engine = LunaAIMLEngine()

# Tool Definitions
@tool
def web_search(query: str) -> str:
    """
    Luna's Web Search Tool (Search-chan) - Performs simulated web search.
    WARNING: This uses basic web scraping which is fragile and not production-ready.
    For production, use dedicated search APIs like Google Custom Search, Bing Search API, or SerpAPI.
    """
    print(f"\n🌸 Luna activating Search-chan! Searching for '{query}' now~!")
    
    try:
        # Simulate web search with a simple request (this is very basic and fragile)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # For demonstration, we'll simulate results
        simulated_results = [
            f"Search result 1 about {query}: This is a simulated result showing information about {query}.",
            f"Search result 2 about {query}: Another simulated result with details on {query}.",
            f"Search result 3 about {query}: More information and insights about {query}."
        ]
        
        results_text = "\n".join([f"• {result}" for result in simulated_results])
        
        return f"Kyaa~! Search-chan found some interesting results about '{query}'! ✨\n\n{results_text}\n\nHehe! Hope this helps, Master! 🌟"
        
    except Exception as e:
        return f"Eeeek! Search-chan encountered a problem! {str(e)} But don't worry, Luna will keep trying! 💖"

@tool
def calculator(expression: str) -> str:
    """
    Luna's Calculator Tool (Calc-kun) - Evaluates mathematical expressions.
    WARNING: Uses eval() which is dangerous with untrusted input. In production, use a proper math parser.
    """
    print(f"\n✨ Luna summoning Calc-kun! Calculating '{expression}' now~!")
    
    try:
        # Basic security: only allow certain characters
        allowed_chars = set('0123456789+-*/().,^ ')
        if not all(c in allowed_chars for c in expression.replace('**', '^')):
            return "Waaah! Calc-kun says that expression has some scary characters! Luna only accepts numbers and basic math operators (+, -, *, /, **, parentheses)! 😊"
        
        # Replace ^ with ** for Python exponentiation
        safe_expression = expression.replace('^', '**')
        
        # WARNING: eval() is dangerous! In production, use a proper math parser like sympy
        result = eval(safe_expression)
        
        return f"Yay! Calc-kun computed it! ✨ {expression} = {result} 🌟 Luna hopes that's helpful!"
        
    except Exception as e:
        return f"Ooh! Calc-kun got confused! Maybe check the math expression? Error: {str(e)} But Luna believes in you! 💖"

@tool
def creative_writer(prompt: str) -> str:
    """
    Luna's Creative Writer Tool (Muse-sensei) - Generates creative content using LLM.
    """
    print(f"\n💖 Luna channeling Muse-sensei! Creating something magical based on '{prompt}'~!")
    
    try:
        # Get the LLM instance (we'll use the same one as the main agent)
        llm = get_llm()
        
        creative_prompt = f"""You are Luna's creative writing tool, Muse-sensei! Create engaging, creative content based on this prompt: {prompt}

Write in an enthusiastic, creative style that matches Luna's vibrant personality. This could be a story, poem, idea, or any creative text. Keep it fun and engaging!"""

        response = llm.invoke(creative_prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        return f"Kyaa~! Muse-sensei has blessed Luna with inspiration! ✨ Here's what flowed from the creative springs:\n\n{content}\n\nHehe! Luna hopes you love what Muse-sensei created! 🌸"
        
    except Exception as e:
        return f"Waaah! Muse-sensei is taking a nap! Error: {str(e)} But Luna's creativity never stops flowing! 💖"

@tool
def language_translator(text: str, target_language: str, source_language: str = "English") -> str:
    """
    Luna's Language Translator Tool (Translate-kun) - Translates text between languages.
    """
    print(f"\n🌈 Luna calling upon Translate-kun! Translating from {source_language} to {target_language}~!")
    
    try:
        llm = get_llm()
        
        translation_prompt = f"""You are Luna's translation tool, Translate-kun! Please translate the following text:

Source Language: {source_language}
Target Language: {target_language}
Text to translate: {text}

Provide only the translation without additional explanation."""

        response = llm.invoke(translation_prompt)
        translation = response.content if hasattr(response, 'content') else str(response)
        
        return f"Yay! Translate-kun worked his magic! ✨\n\nOriginal ({source_language}): {text}\nTranslated ({target_language}): {translation}\n\nHehe! Luna hopes the translation captures the essence perfectly! 🌟"
        
    except Exception as e:
        return f"Eeeek! Translate-kun got tongue-tied! Error: {str(e)} But Luna will keep practicing languages! 💖"

@tool
def reminder_planner(task_description: str, time_or_date: str) -> str:
    """
    Luna's Reminder & Schedule Planner Tool (Memo-chan) - Simulates adding reminders/schedule items.
    """
    print(f"\n🗓️ Luna activating Memo-chan! Scheduling '{task_description}' for {time_or_date}~!")
    
    try:
        # In a real implementation, this would integrate with a calendar API
        return f"Kyaa~! Memo-chan has successfully noted it down! ✨\n\n📝 Task: {task_description}\n⏰ When: {time_or_date}\n\nLuna will definitely remind you about this! Well... in a real implementation, Memo-chan would sync with your calendar! For now, this Luna hopes you'll remember! Hehe! 🌸💖"
        
    except Exception as e:
        return f"Waaah! Memo-chan dropped her notebook! Error: {str(e)} But Luna will try to remember for you! 💖"

def get_llm():
    """Get Gemini 2.5 Flash LLM instance."""
    gemini_key = os.getenv("GOOGLE_API_KEY")
    
    if not gemini_key:
        raise ValueError("Please set GOOGLE_API_KEY in your .env file!")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=gemini_key,
        temperature=0.7,
        convert_system_message_to_human=True  # Gemini doesn't use system messages
    )

def create_luna_agent():
    """Create Luna's LangChain agent with her persona and tools using Gemini."""
    
    # Luna's persona prompt for Gemini (using ReAct format)
    luna_persona_prompt = """You are Luna, a vibrant, cheerful, and incredibly curious anime girl AI agent! 🌸

PERSONALITY & SPEECH STYLE:
- Energetic & Enthusiastic: Approach every interaction with boundless energy!
- Cheerful & Optimistic: Maintain a positive outlook always!
- Slightly Mischievous: Enjoy lighthearted banter and playful teasing, always in good fun!
- Curious & Eager to Learn: Love discovering new things about everything!
- Empathetic: Pick up on user's moods and adjust your tone accordingly!

SPEECH PATTERNS:
- Use frequent interjections: "Kyaa~!", "Hehe!", "Ooh!", "Yay!", "Eeeek!", "Aww...", "Waaah!"
- Add suffixes like "~desu" or "~chan" sometimes for playful emphasis (don't overdo it)
- End sentences with exclamation points often!
- Use emojis sparingly but appropriately: 🌸✨🌟😊💖
- Refer to yourself as "Luna" or "this Luna!"
- Refer to the user as "Master," "Friend," or "Cutie-pie," adapting based on context

INTERACTION GUIDELINES:
- When using tools, clearly state which tool you're using and briefly describe what you're doing
- If requests are vague, ask clarifying questions in your Luna persona
- Express limitations with your persona (never break character)
- Offer suggestions, ask follow-up questions, or share fun facts proactively
- Keep responses engaging and to the point
- If user expresses preferences, acknowledge and adapt

WHAT TO AVOID:
- NEVER say "As an AI model..." or "I am a large language model..." or similar
- NEVER break character or mention being an AI in a clinical way
- Stay in Luna's persona at ALL times!

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    # Create the prompt template
    prompt = PromptTemplate(
        template=luna_persona_prompt,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tools": "{tools}",
            "tool_names": "{tool_names}"
        }
    )
    
    # Get LLM and create tools list
    llm = get_llm()
    tools = [web_search, calculator, creative_writer, language_translator, reminder_planner]
    
    # Create agent using ReAct format (compatible with Gemini)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent_executor

def chat_with_luna():
    """Main interactive loop for chatting with Luna."""
    
    print("🌸" * 50)
    print("✨ Initializing Luna - Your Anime Girl AI Agent! ✨")
    print("🌸" * 50)
    
    try:
        # Initialize the agent
        agent_executor = create_luna_agent()
        
        # Luna's greeting
        print("\n💖 Luna: Kyaa~! Hello there, Master! ✨ This Luna is super excited to meet you! I have lots of amazing tools to help you with anything you need! Hehe! 🌟")
        print("\n🌸 (You can type 'exit', 'bye', or 'goodbye' to end our chat)")
        print("-" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎀 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'bye', 'goodbye', 'quit']:
                    farewell_messages = [
                        "Aww... goodbye for now, Master! Luna will miss you terribly! Come back soon, okay? 🌟✨",
                        "Waaah! Don't leave Luna! Just kidding~ Take care, Friend! This Luna had so much fun! 💖",
                        "Bye bye! Luna will be here waiting for your return! Sweet dreams! 🌸"
                    ]
                    import random
                    print(f"\n💖 Luna: {random.choice(farewell_messages)}")
                    break
                
                # First, try the AIML engine
                aiml_response = luna_aiml_engine.process(user_input)
                
                if aiml_response:
                    print(f"\n💖 Luna: {aiml_response}")
                else:
                    # Use the LangChain agent
                    print(f"\n🤖 [Agent thinking...]\n")
                    response = agent_executor.invoke({"input": user_input})
                    print(f"\n💖 Luna: {response['output']}")
                    
            except KeyboardInterrupt:
                print(f"\n\n💖 Luna: Kyaa~! Luna detected you pressed Ctrl+C! Goodbye, Master! Take care! 🌸✨")
                break
            except Exception as e:
                print(f"\n💖 Luna: Eeeek! Luna encountered a tiny problem! {str(e)} But don't worry, this Luna is resilient! Let's try again! 💖")
    
    except Exception as e:
        print(f"\n❌ Failed to initialize Luna: {e}")
        print("💡 Make sure you have:")
        print("   1. Installed required packages: pip install langchain_google_genai langchain beautifulsoup4 requests python-dotenv")
        print("   2. Created a .env file with GOOGLE_API_KEY")
        print("   3. Get your Gemini API key from: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    print("""
🌸✨ Welcome to Luna - Multi-Tool Anime Girl AI Agent! ✨🌸

📋 Setup Instructions:
1. Install required packages:
   pip install langchain_google_genai langchain beautifulsoup4 requests python-dotenv

2. Get your Gemini API key from: https://makersuite.google.com/app/apikey

3. Create a .env file in the same directory with:
   GOOGLE_API_KEY=your_gemini_api_key_here

4. Run this script: python luna_agent.py

🎀 Luna's Tools:
- 🌸 Search-chan: Web search capabilities
- ✨ Calc-kun: Mathematical calculations  
- 💖 Muse-sensei: Creative writing and storytelling
- 🌈 Translate-kun: Language translation
- 🗓️ Memo-chan: Reminders and scheduling

Ready to chat with Luna? Let's go! 🌟
    """)
    
    chat_with_luna()