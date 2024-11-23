
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Tuple, Dict, Any

class LLMUtils:
    def __init__(self, model_config: Dict[str, Any]):
        """Initialize LLM utilities"""
        self.config = model_config
        self.model, self.tokenizer = self._load_model()

    def _load_model(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load the LLM model and tokenizer"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.config['name'])
            model = AutoModelForCausalLM.from_pretrained(
                self.config['name'],
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_4bit=self.config.get('load_in_4bit', True)
            )
            return model, tokenizer
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")

    def generate_response(self, prompt: str) -> str:
        """Generate response from the model"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=self.config.get('max_length', 512),
            temperature=self.config.get('temperature', 0.7),
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def analyze_maritime_query(self, query: str) -> Dict[str, Any]:
        """Analyze maritime query and extract key components"""
        prompt = f"""
        Analyze this maritime data query and extract key components:
        Query: {query}
        
        Identify:
        1. Query type (vessel tracking, port analysis, speed analysis)
        2. Time range
        3. Specific vessels or vessel types
        4. Geographic area
        5. Required visualization
        """
        
        response = self.generate_response(prompt)
        # Process response to structured format
        return self._parse_analysis(response)

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse model response into structured format"""
        # Add parsing logic here
        return {
            "query_type": "vessel_tracking",  # Example
            "time_range": "24h",
            "vessel_filter": None,
            "area": None,
            "visualization": "map"
        }

def load_llm_model(config: Dict[str, Any]) -> LLMUtils:
    """Helper function to load LLM model"""
    return LLMUtils(config)
