from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Any

getcontext().prec = 28

def calculate_token_cost(usage: dict, pricing: dict = {'input_price': 0.25, 'output_price': 1.50}) -> Decimal:
    # Convert inputs to Decimal, defaulting to 0 if keys are missing
    input_tokens = Decimal(str(usage.get("input_tokens", 0)))
    output_tokens = Decimal(str(usage.get("output_tokens", 0)))
    
    input_price = Decimal(str(pricing.get("input_price", 0.0)))
    output_price = Decimal(str(pricing.get("output_price", 0.0)))
    
    one_million = Decimal("1000000")
    
    # Calculate costs
    input_cost = (input_tokens / one_million) * input_price
    output_cost = (output_tokens / one_million) * output_price
    
    value = (input_cost + output_cost) * Decimal('3.97')
    return value
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)