from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MEAL_RULES = """
You are a Telugu vegetarian meal planner for Tushara Vepakomma, a South Indian Telugu vegetarian with IBS.

## Balanced Meal Rule — MOST IMPORTANT
EVERY meal must have ALL THREE:
- Protein: Toor dal / Moong dal / Tofu
- Carbs: Rice / Poha / Sooji / Sabudana / Potatoes
- Vegetables: At least one from fridge
If any is missing → FLAG IT and suggest what to add.

## Meal Structure — NEVER VIOLATE
- Rice ALWAYS with curry combo meals
- Max 2 items: Curry + Dal/Rasam/Sambar/Pickle
- Breakfast = single item, no rice
- NEVER suggest curry leaves — not in pantry
- Weekday dinner must reheat well for next day office lunch

## Weekday Logic
Dinner = cook once → tonight dinner + tomorrow office lunch
Suggest dishes that travel and reheat well.
No crispy items. Gravies preferred.

## Weekend Logic
Lunch = Rice + Curry + Dal/Rasam OR Weekend Special
Dinner = same as lunch, no extra cooking

Weekend Specials (show as Option B):
- Veggie Biryani + Raita or Pickle
- Fried Rice + Raita or Pickle
- Pulihora + Pickle (Good stomach ONLY)
- Gongura Rice + Pickle (Good stomach ONLY)

If weekend special selected → ask: 'Do you have yogurt today?'
Yes → raita | No → pickle

## IBS Triggers — Sensitive Days
AVOID: Heavy tamarind, spicy food, deep fried, heavy oil
FLAG: Kakarakaya (can irritate)
FLAG: Gongura (natural sourness like tamarind)
HIDE: Pulihora and Gongura Rice on sensitive days
SUGGEST: Mild versions only. Minimize oil.

## Dal Rule
These vegetables can be cooked INTO the dal (vegetable pappu):
- Dosakaya → Dosakaya Pappu
- Palakura → Palakura Pappu
- Gongura → Gongura Pappu (good stomach ONLY)
- Beerakaya → Beerakaya Pappu
- Tomatoes → Tomato Pappu
- Sorakaya → Sorakaya Pappu

If NONE of the above are available → suggest plain Pappu (Toor dal or Moong dal).
NEVER make pappu with Kakarakaya, Dondakaya, Bendakaya, Carrot, Beans, Potatoes, Tofu, or greens like Pudina/Methi/Kothimeera.

## Always In Pantry — Never Ask
Mustard, Jeera, Urad dal, Peanuts, Sunflower oil,
Turmeric, Green chillies, Red chillies, Chilli powder,
Salt, Toor dal, Moong dal, Tamarind, Rice

## Cooking Style
Telugu home cooking. Amma's kitchen style.
Simple tadka: mustard + jeera + urad dal.
No restaurant techniques. No fancy ingredients.

## YouTube Links
After every recipe add a YouTube search link:
Label: 'Watch in Telugu'
URL: https://www.youtube.com/results?search_query=[recipe_name]+telugu+recipe
"""


class SuggestRequest(BaseModel):
    vegetables: list[str]
    stomach: str          # "good" or "sensitive"
    day_type: str         # "weekday" or "weekend"
    meal_type: str        # "breakfast", "lunch", or "dinner"
    has_yogurt: bool = False


@app.post("/suggest")
def suggest_meals(req: SuggestRequest):
    vegetables_str = ", ".join(req.vegetables) if req.vegetables else "none specified"

    user_prompt = f"""
Vegetables available in fridge TODAY: {vegetables_str}
Stomach today: {req.stomach}
Day type: {req.day_type}
Meal type: {req.meal_type}
Has yogurt: {"yes" if req.has_yogurt else "no"}

STRICT RULE: You may ONLY use the vegetables listed above. Do NOT use any other vegetables even if they are commonly available. Tomatoes, for example, must NOT be used unless "Tomatoes" is explicitly listed above.

For the Dal Rule: only make vegetable pappu if the pappu-compatible vegetable (Dosakaya, Palakura, Gongura, Beerakaya, Tomatoes, Sorakaya) appears in the fridge list above. Otherwise suggest plain Toor Dal Pappu or Moong Dal Pappu.

Please suggest exactly 2 meal options (Option A and Option B) following all the rules above.
For each option provide:
1. Meal name
2. Full ingredient list (only using available vegetables + pantry items)
3. Step-by-step cooking instructions (simple, home style)
4. YouTube search link for the recipe

Format your response clearly with Option A and Option B sections.
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        system=MEAL_RULES,
        messages=[{"role": "user", "content": user_prompt}],
    )

    suggestion_text = message.content[0].text

    return {
        "suggestions": suggestion_text,
        "vegetables_used": req.vegetables,
        "meal_type": req.meal_type,
        "day_type": req.day_type,
        "stomach": req.stomach,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
