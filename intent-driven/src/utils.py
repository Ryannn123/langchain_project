from decimal import Decimal, getcontext, ROUND_HALF_UP

from pydantic import BaseModel, create_model

from src.schemas import IntentItem, CourseDetail, PathwayDetail, UniversityDetail, RegistrationDetail, Area, IntentType
from src.state import AgentState
from src.types import Area as AreaEnum

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

def dict_to_yaml_like(data, indent=0, exclude_empty=False):
    lines = []
    space = "  " * indent

    if isinstance(data, dict):
        for key, val in data.items():
            # Check for empty or null values if exclusion is enabled
            if exclude_empty:
                if val is None:
                    continue
                if isinstance(val, (dict, list)) and not val:
                    continue

            # Format the value based on its type
            if val is None:
                lines.append(f"{space}{key}: null")
            elif isinstance(val, dict):
                if not val:
                    lines.append(f"{space}{key}: {{}}")
                else:
                    lines.append(f"{space}{key}:")
                    subtree = dict_to_yaml_like(val, indent + 1, exclude_empty)
                    if subtree:  # Only append if the nested dict wasn't completely emptied
                        lines.append(subtree)
                    else:
                        # If the subtree became empty due to filtering, remove the header
                        lines.pop()
            elif isinstance(val, list):
                if not val:
                    lines.append(f"{space}{key}: []")
                else:
                    lines.append(f"{space}{key}:")
                    for item in val:
                        lines.append(f"{space}  - {item}")
            elif isinstance(val, bool):
                lines.append(f"{space}{key}: {str(val).lower()}")
            else:
                lines.append(f"{space}{key}: {val}")

    return "\n".join(lines)

def merge_schema(*schemas: type[BaseModel]) -> type[BaseModel]:
    combined_base = type("CombinedBase", schemas, {})
    return create_model('MergedSchema', __base__=combined_base)

def area_to_schema(areas: list[str]) -> list[type[BaseModel]]:
    mapping: dict[str, type[BaseModel]] = {
        AreaEnum.REGISTRATION.value: RegistrationDetail,
        AreaEnum.COURSE.value: CourseDetail,
        AreaEnum.PATHWAY.value: PathwayDetail,
        AreaEnum.UNI.value: UniversityDetail
    }
    
    return [mapping[area] for area in areas]

def get_profile(state: AgentState, *schemas: type[BaseModel]):
    profile = {}
    for schema in schemas:
        profile[schema.__name__] = schema.model_validate(state).model_dump(exclude_unset=True)
    return profile

def has_intent(intents: list[IntentItem], areas: list[Area] | None = None, intent_types: list[IntentType] | None = None) -> bool:
	if areas is None and intent_types is None:
		return len(intents) > 0
    
	for item in intents:
		matches_area = areas is None or item.area in areas
		matches_type = intent_types is None or item.intent_type in intent_types
		if matches_area and matches_type:
			return True

	return False