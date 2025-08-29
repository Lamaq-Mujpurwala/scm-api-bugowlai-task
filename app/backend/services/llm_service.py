import os
import json
from typing import Dict, Any, Optional
import httpx
from abc import ABC, abstractmethod
import google.genai as genai
from google.genai import types

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        pass

class OpenAIService(LLMProvider):
    """OpenAI GPT-4 service for content moderation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content using OpenAI GPT-4"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
            
        prompt = f"""
        Analyze the following text for content moderation. Classify it as one of: toxic, spam, harassment, or safe.
        Provide a confidence score (0-1) and reasoning.
        
        Text: {text}
        
        Respond in JSON format:
        {{
            "classification": "toxic|spam|harassment|safe",
            "confidence": 0.95,
            "reasoning": "Explanation here"
        }}
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")
                
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return {
                    "classification": "safe",
                    "confidence": 0.5,
                    "reasoning": "Unable to parse LLM response"
                }
    
    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze image content using OpenAI GPT-4 Vision"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
            
        prompt = """
        Analyze this image for content moderation. Classify it as one of: toxic, spam, harassment, or safe.
        Provide a confidence score (0-1) and reasoning.
        
        Respond in JSON format:
        {
            "classification": "toxic|spam|harassment|safe",
            "confidence": 0.95,
            "reasoning": "Explanation here"
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")
                
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "classification": "safe",
                    "confidence": 0.5,
                    "reasoning": "Unable to parse LLM response"
                }

class GeminiService(LLMProvider):
    """Google Gemini 2.5 Pro service for content moderation with reasoning capabilities"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not configured")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Define the reasoning tool
        self.reasoning_tool = {
            "name": "content_moderation_tool",
            "description": "Analyze content for moderation and provide detailed reasoning",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "classification": {
                        "type": "STRING",
                        "description": "Content classification: toxic, spam, harassment, or safe",
                        "enum": ["toxic", "spam", "harassment", "safe"]
                    },
                    "confidence": {
                        "type": "NUMBER",
                        "description": "Confidence score between 0 and 1"
                    },
                    "reasoning": {
                        "type": "STRING",
                        "description": "Detailed reasoning for the classification"
                    }
                },
                "required": ["classification", "confidence", "reasoning"]
            }
        }
        
        self.tools = types.Tool(function_declarations=[self.reasoning_tool])
        
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content using Google Gemini 2.5 Pro with reasoning"""
        prompt = f"""
        Analyze the following text for content moderation. Classify it as one of: toxic, spam, harassment, or safe.
        Provide a confidence score (0-1) and detailed reasoning for your classification.
        
        Text to analyze: {text}
        
        Use the content_moderation_tool to provide your analysis with classification, confidence, and reasoning.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                    tools=[self.tools]
                )
            )
            
            # Extract the function call response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    args = part.function_call.args
                    return {
                        "classification": args.get("classification", "safe"),
                        "confidence": float(args.get("confidence", 0.5)),
                        "reasoning": args.get("reasoning", "No reasoning provided"),
                        "llm_provider": "gemini"
                    }
            
            # Fallback if no function call found
            return {
                "classification": "safe",
                "confidence": 0.5,
                "reasoning": "Unable to parse LLM response - no function call found",
                "llm_provider": "gemini"
            }
            
        except Exception as e:
            return {
                "classification": "safe",
                "confidence": 0.5,
                "reasoning": f"Error analyzing content: {str(e)}",
                "llm_provider": "gemini"
            }
    
    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze image content using Google Gemini 2.5 Pro with reasoning"""
        import base64
        import tempfile
        
        prompt = """
        Analyze this image for content moderation. Classify it as one of: toxic, spam, harassment, or safe.
        Provide a confidence score (0-1) and detailed reasoning for your classification.
        
        Use the content_moderation_tool to provide your analysis with classification, confidence, and reasoning.
        """
        
        try:
            # Convert base64 to temporary file for Gemini API
            image_bytes = base64.b64decode(image_data)
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name
            
            # Upload file to Gemini
            uploaded_file = self.client.files.upload(file=temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Generate content with image
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                    tools=[self.tools]
                )
            )
            
            # Extract the function call response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    args = part.function_call.args
                    return {
                        "classification": args.get("classification", "safe"),
                        "confidence": float(args.get("confidence", 0.5)),
                        "reasoning": args.get("reasoning", "No reasoning provided"),
                        "llm_provider": "gemini"
                    }
            
            # Fallback if no function call found
            return {
                "classification": "safe",
                "confidence": 0.5,
                "reasoning": "Unable to parse LLM response - no function call found",
                "llm_provider": "gemini"
            }
            
        except Exception as e:
            return {
                "classification": "safe",
                "confidence": 0.5,
                "reasoning": f"Error analyzing image: {str(e)}",
                "llm_provider": "gemini"
            }

class LLMService:
    """Main LLM service that manages different providers"""
    
    def __init__(self):
        self.providers = {}
        
        # Initialize available providers with valid API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            self.providers["openai"] = OpenAIService()
            
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            try:
                self.providers["gemini"] = GeminiService()
            except Exception as e:
                print(f"Failed to initialize Gemini service: {e}")
    
    def get_provider(self, provider_name: str = None) -> LLMProvider:
        """Get the specified provider or default to first available"""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        # Return first available provider
        if self.providers:
            return list(self.providers.values())[0]
        
        raise ValueError("No LLM providers configured")
    
    async def analyze_text(self, text: str, provider: str = None) -> Dict[str, Any]:
        """Analyze text using specified or default provider"""
        llm_provider = self.get_provider(provider)
        result = await llm_provider.analyze_text(text)
        result["llm_provider"] = provider or list(self.providers.keys())[0]
        return result
    
    async def analyze_image(self, image_data: str, provider: str = None) -> Dict[str, Any]:
        """Analyze image using specified or default provider"""
        llm_provider = self.get_provider(provider)
        result = await llm_provider.analyze_image(image_data)
        result["llm_provider"] = provider or list(self.providers.keys())[0]
        return result
