import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, BANNED_WORDS

class AuroraEngine:
    def __init__(self, api_key, model_name):
        try:
            self.model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=1.0,
                api_key=api_key
            )
            self.chat_history = []
        except ValueError as e:
            raise ValueError(f"Invalid API key or model configuration: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to initialize model: {str(e)}")

    def _extract_text(self, content):
        """Extract text from content (handles both string and list formats)"""
        try:
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                return ''.join(part.get('text', '') if isinstance(part, dict) else str(part) for part in content)
            return str(content)
        except Exception as e:
            return f"[Error extracting response: {str(e)}]"

    def validate_response(self, text):
        try:
            text = self._extract_text(text)
            for word in BANNED_WORDS:
                if word.lower() in text.lower():
                    return False
            return True
        except Exception as e:
            print(f"Error validating response: {str(e)}")
            return True

    def get_response(self, user_query):
        try:
            if not user_query or not user_query.strip():
                return "Please provide a valid query."
            
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            
            # Add Few-Shot Examples
            for example in FEW_SHOT_EXAMPLES:
                try:
                    role = example["role"]
                    text = example["parts"][0]["text"]

                    if role == "user":
                        messages.append(HumanMessage(content=text))
                    elif role == "model":
                        messages.append(AIMessage(content=text))
                except KeyError as e:
                    print(f"Error processing example: {str(e)}")
                    continue

            # add current chat history and new user query    
            messages.extend(self.chat_history)
            messages.append(HumanMessage(content=user_query))

            response = self.model.invoke(messages)
            response_text = self._extract_text(response.content)
            
            if self.validate_response(response_text):
                self.chat_history.append(HumanMessage(content=user_query))
                self.chat_history.append(AIMessage(content=response_text))
                return response_text
            return "[System Notice]: This request does not align with our premium standards."
        
        except ValueError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return "[Error]: API quota exceeded. Please wait a moment and try again, or check your API plan at https://ai.google.dev"
            elif "401" in str(e) or "UNAUTHENTICATED" in str(e):
                return "[Error]: Invalid API key. Please check your credentials."
            else:
                return f"[Error]: {str(e)}"
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "[Error]: API quota exceeded. Please wait a moment before trying again."
            else:
                return f"[Error]: An unexpected error occurred. Please try again. ({type(e).__name__})"

    def reset_chat(self):
        try:
            self.chat_history = []
        except Exception as e:
            print(f"Error resetting chat: {str(e)}")