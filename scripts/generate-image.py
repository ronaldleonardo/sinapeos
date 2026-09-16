#!/usr/bin/env python3
"""
Sinapeos Image Generator
Generates story images via OpenRouter API (Flux or GPT-4o image).
Usage: python3 generate-image.py <story-slug> <prompt> [output-filename]
"""

import json
import os
import sys
import requests
from pathlib import Path

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
SITE_DIR = Path("/root/sinapeos")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_API_URL = "https://openrouter.ai/api/v1/images/generations"

if not OPENROUTER_KEY:
    # Try to read from config
    config_path = Path("/root/.hermes/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                if "openrouter" in line.lower() and "key" in line.lower():
                    parts = line.split(":")
                    if len(parts) > 1:
                        OPENROUTER_KEY = parts[1].strip().strip('"').strip("'")
    
    # Try Hermes .env file
    if not OPENROUTER_KEY:
        env_path = Path("/root/.hermes/.env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and "***" not in val:
                            OPENROUTER_KEY = val

if not OPENROUTER_KEY:
    print("ERROR: No OPENROUTER_API_KEY found")
    sys.exit(1)


def generate_with_flux(prompt, output_path):
    """Generate image using Flux via OpenRouter images endpoint"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "black-forest-labs/flux-dev",
        "prompt": f"Photorealistic, documentary style. {prompt}",
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        resp = requests.post(IMAGE_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract image URL from response
        image_url = None
        if "data" in data and len(data["data"]) > 0:
            image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")
        
        if image_url and image_url.startswith("http"):
            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_resp.content)
            return True
        else:
            print(f"WARN: No image URL in response: {data.keys() if isinstance(data, dict) else type(data)}")
            return False
            
    except Exception as e:
        print(f"ERROR generating image: {e}")
        return False


def generate_with_gpt4o(prompt, output_path):
    """Generate image via GPT-4o image preview"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4o-image-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate a cinematic, documentary-style image. {prompt} Style: realistic, dramatic lighting, not cartoonish. Mood: hopeful but grounded."
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # The response might contain a markdown image or URL
        if "![Image]" in content or "http" in content:
            # Extract URL
            import re
            urls = re.findall(r'https?://[^\s\)]+(?:png|jpg|jpeg|webp)', content)
            if urls:
                img_resp = requests.get(urls[0], timeout=30)
                img_resp.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                return True
                
        print(f"WARN: No image in GPT-4o response: {content[:200]}")
        return False
        
    except Exception as e:
        print(f"ERROR with GPT-4o image: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate-image.py <story-slug> <prompt> [output-filename]")
        sys.exit(1)
    
    slug = sys.argv[1]
    prompt = sys.argv[2]
    filename = sys.argv[3] if len(sys.argv) > 3 else "hero.webp"
    
    # Create output directory
    img_dir = SITE_DIR / "public" / "images" / slug
    img_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = img_dir / filename
    
    print(f"Generating: {slug}/{filename}")
    print(f"Prompt: {prompt}")
    
    # Try Flux first (cheaper, faster)
    success = generate_with_flux(prompt, output_path)
    if not success:
        print("Flux failed, trying GPT-4o image...")
        success = generate_with_gpt4o(prompt, output_path)
    
    if success:
        print(f"SUCCESS: Image saved to {output_path}")
        sys.exit(0)
    else:
        print("FAILED: Could not generate image")
        sys.exit(1)


if __name__ == "__main__":
    main()