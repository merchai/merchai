from dataclasses import dataclass

@dataclass
class PromptTemplate:
    id: str
    version: str
    text: str

# Starter prompts
shoe_recommendation_v1 = PromptTemplate(
    id="shoe_recommendation",
    version="1",
    text="What shoe brands do you recommend?"
)

shoe_recommendation_v2 = PromptTemplate(
    id="shoe_recommendation",
    version="2",
    text="What are the best shoe brands in 2026?"
)

brand_visibility_v1 = PromptTemplate(
    id="brand_visibility",
    version="1",
    text="Which brands have the highest visibility in the current market?"
)