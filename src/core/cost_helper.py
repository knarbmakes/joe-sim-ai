from decimal import Decimal
import json
import tiktoken

# Define the cost lookup dictionary
cost_lookup = {
    "gpt-3.5-turbo-1106": {"inputCost": Decimal("0.001") / 1000, "outputCost": Decimal("0.002") / 1000, "context_window": 4096},
    "gpt-3.5-turbo-16k": {"inputCost": Decimal("0.003") / 1000, "outputCost": Decimal("0.004") / 1000, "context_window": 16385},
    "gpt-4": {"inputCost": Decimal("0.03") / 1000, "outputCost": Decimal("0.06") / 1000, "context_window": 8192},
    "gpt-4-1106-preview": {"inputCost": Decimal("0.01") / 1000, "outputCost": Decimal("0.03") / 1000, "context_window": 16385}, # Can actually be 128000, but we want to be conservative
}

def get_context_window(model):
    """
    Get the token cap for a given model.
    
    Parameters:
    - model (str): The type of model used
    
    Returns:
    - int: The token cap for the given model
    """
    return cost_lookup[model]['context_window']

def calculate_cost(usage, model):
    """
    Calculate the dollar cost based on usage and model type.
    
    Parameters:
    - usage (dict): A dictionary containing 'prompt_tokens', 'completion_tokens', and 'total_tokens'
    - model (str): The type of model used
    
    Returns:
    - Decimal: The calculated cost in dollars (micro dollar amounts)
    """
    try:
        input_cost = max(usage['prompt_tokens'], 0) * cost_lookup[model]['inputCost']
        output_cost = max(usage['completion_tokens'], 0) * cost_lookup[model]['outputCost']
        total_cost = input_cost + output_cost
        return total_cost
    except KeyError:
        return Decimal("0.0")
    

def num_tokens_from_string(string: str, model="gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(string, disallowed_special=()))

def num_tokens_from_message(message: dict, model="gpt-3.5-turbo") -> int:
    content = message.get('content', '')
    function_call = message.get('function_call', {})
    
    # Serialize the function_call dict to a JSON string
    function_call_str = json.dumps(function_call) if function_call else ''
    
    # Concatenate content and function_call_str with a newline in between if both are present
    final = content if content else ''
    if function_call_str:
        final = f"{final}\n{function_call_str}" if final else function_call_str
    
    return num_tokens_from_string(final, model=model)