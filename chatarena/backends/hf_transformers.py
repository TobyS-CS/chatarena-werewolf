import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from tenacity import retry, stop_after_attempt, wait_random_exponential

from ..message import SYSTEM_NAME as SYSTEM
from ..message import Message
from .base import IntelligenceBackend, register_backend

@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout and stderr."""
    with open(os.devnull, "w") as fnull, redirect_stderr(fnull), redirect_stdout(fnull):
        yield

with suppress_stdout_stderr():
    try:
        tokenizer = AutoTokenizer.from_pretrained("allenai/llama-3")
        model = AutoModelForCausalLM.from_pretrained("allenai/llama-3")
        is_model_available = True
    except ImportError:
        is_model_available = False

@register_backend
class LLaMAConversational(IntelligenceBackend):
    """Interface to the LLaMA model configured for conversational tasks."""

    stateful = False
    type_name = "llama:conversational"

    def __init__(self, model_name: str, device: int = -1, **kwargs):
        super().__init__(model=model_name, device=device, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device=device)
        assert is_model_available, "LLaMA model is not installed."

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
    def _get_response(self, input_text):
        """Generate response using the LLaMA model."""
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True)
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def query(self, agent_name: str, role_desc: str, history_messages: List[Message], global_prompt: str = None, request_msg: Message = None, *args, **kwargs) -> str:
        """Generate a response based on the conversational context."""
        conversation_history = []

        if global_prompt:
            conversation_history.append(f"{SYSTEM}: {global_prompt}")
        conversation_history.append(f"{SYSTEM}: {role_desc}")

        for msg in history_messages:
            conversation_history.append(f"{msg.agent_name}: {msg.content}")
        
        if request_msg:
            conversation_history.append(f"{SYSTEM}: {request_msg.content}")

        # Combine all parts into a single text blob to feed into the model
        full_conversation = "\n".join(conversation_history)
        
        # Get response from the model
        response = self._get_response(full_conversation)
        return response

# Example usage:
# backend = LLaMAConversational("allenai/llama-3")
# response = backend.query("Assistant", "Your role here", [Message("User", "Hello!")])
# print(response)