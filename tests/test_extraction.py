from src.extraction import extract_brands

def test_extract_simple():
    data = {"brand": "Nike"}
    assert extract_brands(data) == ["Nike"]

def test_extract_deeply_nested_user_sample():
    """Test using the specific JSON structure provided by the user."""
    data = {
      "shoe_brands": {
        "athletic_and_performance": [
          {
            "brand": "Hoka",
            "specialty": "Maximalist cushioning and stability",
            "popular_models": ["Clifton 10", "Bondi 9", "Speedgoat 6"],
            "best_for": "Long-distance running, walking, and standing all day."
          },
          {
            "brand": "Brooks",
            "specialty": "Reliable support and durability",
            "popular_models": ["Ghost 17", "Glycerin 22", "Adrenaline GTS"],
            "best_for": "Daily training and runners needing consistent arch support."
          },
          {
            "brand": "New Balance",
            "specialty": "Blending performance tech with lifestyle aesthetics",
            "popular_models": ["Fresh Foam X 1080", "990 series", "2002R"],
            "best_for": "Versatile wear and wide-foot options."
          },
          {
            "brand": "On Running",
            "specialty": "CloudTec cushioning and sleek design",
            "popular_models": ["Cloud 6", "Cloudrock Mid", "Cloudmonster"],
            "best_for": "Urban commuting, light trail hiking, and modern style."
          }
        ],
        "lifestyle_and_casual": [
          {
            "brand": "Nike",
            "specialty": "Global leader in innovation and style",
            "popular_models": ["Air Force 1", "Dunk Low", "Motiva"],
            "best_for": "Streetwear, trend-focused casual wear, and gym training."
          },
          {
            "brand": "Adidas",
            "specialty": "Retro-heritage and energy-return foam",
            "popular_models": ["Samba", "Ultraboost Light", "Evo SL"],
            "best_for": "Casual fashion and high-energy walking."
          },
          {
            "brand": "Allbirds",
            "specialty": "Eco-friendly materials and machine-washability",
            "popular_models": ["Tree Runner", "Wool Runner"],
            "best_for": "Sustainable fashion and lightweight travel."
          },
          {
            "brand": "Salomon",
            "specialty": "Technical 'Gorpcore' aesthetic and rugged grip",
            "popular_models": ["XT-6", "Speedcross 6"],
            "best_for": "Outdoor adventure and technical streetwear."
          }
        ],
        "premium_and_dress": [
          {
            "brand": "Alden",
            "specialty": "Heritage American shoemaking and Shell Cordovan leather",
            "popular_models": ["Indy Boot", "Tassel Loafer"],
            "best_for": "Investment-grade dress shoes that last decades."
          },
          {
            "brand": "Crockett & Jones",
            "specialty": "High-end British Goodyear-welted footwear",
            "popular_models": ["Chelsea 5", "Cavendish Loafer"],
            "best_for": "Formal business wear and classic elegance."
          },
          {
            "brand": "Common Projects",
            "specialty": "Minimalist luxury sneakers",
            "popular_models": ["Original Achilles Low"],
            "best_for": "Clean, understated luxury that pairs with suits or denim."
          },
          {
            "brand": "Cole Haan",
            "specialty": "Hybrid dress-sneaker comfort",
            "popular_models": ["ØriginalGrand", "2.Zerøgrand"],
            "best_for": "Office professionals needing sneaker-like comfort in a dress shoe."
          }
        ]
      },
      "market_trends_2026": {
        "sustainability": "Increased use of bio-based foams and recycled textiles.",
        "hybrid_styling": "Growth in 'dress sneakers' and technical trail shoes worn as fashion statements.",
        "comfort_first": "Mainstream adoption of recovery-focused footwear (Hoka, Oofos) for daily use."
      }
    }
    
    expected = sorted([
        "Hoka", "Brooks", "New Balance", "On Running",
        "Nike", "Adidas", "Allbirds", "Salomon",
        "Alden", "Crockett & Jones", "Common Projects", "Cole Haan"
    ])
    
    assert extract_brands(data) == expected

def test_extract_empty():
    assert extract_brands({}) == []

def test_extract_no_brands_found():
    data = {"other_key": "other_value", "nested": [{"id": 1}]}
    assert extract_brands(data) == []

def test_extract_handles_non_string_brand_value_gracefully():
    # If "brand" key exists but value is not a string (e.g. nested dict), it should be ignored or recursed
    data = {"brand": {"sub_brand": "ignored"}}
    # Our logic enforces isinstance(value, str) for extraction, but recurses into value
    # So "ignored" won't be picked up unless its key is "brand"
    assert extract_brands(data) == []
    
    data_nested_hit = {"brand": {"brand": "RealBrand"}}
    assert extract_brands(data_nested_hit) == ["RealBrand"]
