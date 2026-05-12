"""NLP Feature Extractor - Extracts risk indicators from accident narratives"""
import re
from typing import Dict, Tuple, List

class FeatureExtractor:
    def __init__(self):
        self.high_risk_patterns = {
            'behavioural': {
                'drunk': 1.0, 'drinking': 1.0, 'dwi': 1.0, 'dui': 1.0,
                'racing': 1.0, 'street racing': 1.0,
                'speeding': 0.8, 'excessive speed': 0.8,
                'reckless': 0.9, 'careless': 0.7,
                'distracted': 0.6, 'phone': 0.5, 'texting': 0.6
            },
            'environmental': {
                'rain': 0.7, 'heavy rain': 0.9, 'flood': 0.8,
                'fog': 0.8, 'foggy': 0.8,
                'dark': 0.5, 'night': 0.5,
                'ice': 0.9, 'slippery': 0.7
            },
            'time': {
                'late night': 0.7, '2am': 0.9, '3am': 0.9,
                'rush hour': 0.5, 'peak hour': 0.5,
                'weekend night': 0.6
            },
            'vehicle': {
                'brake failure': 0.9, 'brakes failed': 0.9,
                'tyre burst': 0.7, 'blowout': 0.7,
                'overloaded': 0.8, 'mechanical fault': 0.6
            },
            'location': {
                'junction': 0.5, 'intersection': 0.5,
                'highway': 0.4, 'rural': 0.3,
                'blind corner': 0.7, 'mountain pass': 0.6,
                'urban': 0.3, 'city': 0.3
            }
        }
        self.matched_keywords = []
    
    def extract_features(self, text: str) -> Tuple[Dict[str, float], bool]:
        """Extract risk features from text. Returns (features_dict, extreme_risk_flag)"""
        features = {
            'behavioural': 0.0,
            'environmental': 0.0,
            'time': 0.0,
            'vehicle': 0.0,
            'location': 0.0
        }
        
        text_lower = text.lower()
        self.matched_keywords = []
        extreme_risk = False
        
        for category, patterns in self.high_risk_patterns.items():
            max_weight = 0.0
            for keyword, weight in patterns.items():
                if keyword in text_lower:
                    max_weight = max(max_weight, weight)
                    self.matched_keywords.append(keyword)
                    if weight >= 0.9:
                        extreme_risk = True
            features[category] = max_weight
        
        for key in features:
            features[key] = min(features[key], 1.0)
        
        return features, extreme_risk
    
    def get_matched_keywords(self, text: str = None) -> List[str]:
        """Return list of matched keywords (deduplicated)"""
        return list(set(self.matched_keywords))


def extract_features(tokens: list) -> dict:
    """Map tokens → legacy flag vector consumed by calculate_risk_score."""
    from app.nlp.analysis import analyze_tokens

    result = analyze_tokens(tokens or [])
    return result["legacy_features"]