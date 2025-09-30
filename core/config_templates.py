#!/usr/bin/env python3
"""
Configuration Templates

Provides pre-built configuration templates for common use cases.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json


class ConfigTemplates:
    """Manages configuration templates and presets."""
    
    def __init__(self):
        """Initialize the configuration templates."""
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load default configuration templates."""
        return {
            "portrait_photography": {
                "name": "Portrait Photography",
                "description": "Optimized for high-quality portrait photography",
                "category": "photography",
                "config": {
                    "width": 512,
                    "height": 768,
                    "steps": 30,
                    "cfg_scale": 7.5,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "blurry, low quality, distorted, deformed, bad anatomy",
                    "prompt_template": "professional portrait photography, {subject}, detailed, high quality, 8k, photorealistic"
                },
                "tags": ["portrait", "photography", "realistic", "people"]
            },
            
            "landscape_art": {
                "name": "Landscape Art",
                "description": "Beautiful landscape artwork with natural lighting",
                "category": "art",
                "config": {
                    "width": 768,
                    "height": 512,
                    "steps": 25,
                    "cfg_scale": 8.0,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "people, buildings, artificial, oversaturated",
                    "prompt_template": "beautiful landscape, {scene_description}, natural lighting, detailed, artistic, masterpiece"
                },
                "tags": ["landscape", "nature", "art", "scenic"]
            },
            
            "anime_character": {
                "name": "Anime Character",
                "description": "Anime/manga style character generation",
                "category": "anime",
                "config": {
                    "width": 512,
                    "height": 768,
                    "steps": 28,
                    "cfg_scale": 7.0,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "realistic, photorealistic, 3d, western animation",
                    "prompt_template": "anime style, {character_description}, detailed, high quality, vibrant colors"
                },
                "tags": ["anime", "manga", "character", "2d"]
            },
            
            "concept_art": {
                "name": "Concept Art",
                "description": "Professional concept art and illustration",
                "category": "art",
                "config": {
                    "width": 768,
                    "height": 768,
                    "steps": 35,
                    "cfg_scale": 8.5,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "photorealistic, photograph, low quality, amateur",
                    "prompt_template": "concept art, {subject}, detailed illustration, professional, artistic, creative"
                },
                "tags": ["concept", "illustration", "art", "creative"]
            },
            
            "cyberpunk_scene": {
                "name": "Cyberpunk Scene",
                "description": "Futuristic cyberpunk aesthetic",
                "category": "sci-fi",
                "config": {
                    "width": 768,
                    "height": 512,
                    "steps": 30,
                    "cfg_scale": 7.5,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "medieval, fantasy, natural, organic",
                    "prompt_template": "cyberpunk, {scene_description}, neon lights, futuristic, detailed, high tech"
                },
                "tags": ["cyberpunk", "sci-fi", "futuristic", "neon"]
            },
            
            "fantasy_art": {
                "name": "Fantasy Art",
                "description": "Magical fantasy artwork and scenes",
                "category": "fantasy",
                "config": {
                    "width": 768,
                    "height": 768,
                    "steps": 32,
                    "cfg_scale": 8.0,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "modern, realistic, technology, sci-fi",
                    "prompt_template": "fantasy art, {fantasy_element}, magical, mystical, detailed, epic"
                },
                "tags": ["fantasy", "magic", "medieval", "epic"]
            },
            
            "product_photography": {
                "name": "Product Photography",
                "description": "Clean product photography style",
                "category": "commercial",
                "config": {
                    "width": 512,
                    "height": 512,
                    "steps": 25,
                    "cfg_scale": 7.0,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "blurry, low quality, cluttered background, amateur",
                    "prompt_template": "product photography, {product}, clean background, professional lighting, commercial quality"
                },
                "tags": ["product", "commercial", "clean", "professional"]
            },
            
            "abstract_art": {
                "name": "Abstract Art",
                "description": "Modern abstract artistic expression",
                "category": "abstract",
                "config": {
                    "width": 768,
                    "height": 768,
                    "steps": 40,
                    "cfg_scale": 9.0,
                    "sampler_name": "DPM++ 2M Karras",
                    "negative_prompt": "realistic, photorealistic, recognizable objects, literal",
                    "prompt_template": "abstract art, {abstract_concept}, creative, artistic, modern, unique"
                },
                "tags": ["abstract", "modern", "artistic", "creative"]
            }
        }
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name."""
        return self.templates.get(template_name)
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all templates in a specific category."""
        return [
            {**template, "template_id": name}
            for name, template in self.templates.items()
            if template.get("category") == category
        ]
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates."""
        return [
            {**template, "template_id": name}
            for name, template in self.templates.items()
        ]
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set()
        for template in self.templates.values():
            category = template.get("category", "uncategorized")
            categories.add(category)
        return sorted(list(categories))
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        
        for name, template in self.templates.items():
            # Check name
            if query in template.get("name", "").lower():
                results.append({**template, "template_id": name})
                continue
            
            # Check description
            if query in template.get("description", "").lower():
                results.append({**template, "template_id": name})
                continue
            
            # Check tags
            tags = template.get("tags", [])
            if any(query in tag.lower() for tag in tags):
                results.append({**template, "template_id": name})
                continue
        
        return results
    
    def create_config_from_template(self, template_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a configuration from a template with optional custom parameters."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Start with template config
        config = template["config"].copy()
        
        # Apply custom parameters if provided
        if custom_params:
            config.update(custom_params)
        
        return config
    
    def get_template_suggestions(self, current_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest templates based on current configuration parameters."""
        suggestions = []
        
        for name, template in self.templates.items():
            template_config = template["config"]
            similarity_score = self._calculate_similarity(current_config, template_config)
            
            if similarity_score > 0.3:  # Threshold for similarity
                suggestions.append({
                    **template,
                    "template_id": name,
                    "similarity_score": similarity_score
                })
        
        # Sort by similarity score
        suggestions.sort(key=lambda x: x["similarity_score"], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_similarity(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> float:
        """Calculate similarity between two configurations."""
        common_keys = set(config1.keys()) & set(config2.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if config1[key] == config2[key]:
                matches += 1
        
        return matches / len(common_keys)


# Global templates instance
_templates = None


def get_config_templates() -> ConfigTemplates:
    """Get the global config templates instance."""
    global _templates
    if _templates is None:
        _templates = ConfigTemplates()
    return _templates
