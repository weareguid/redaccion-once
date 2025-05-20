import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import os
from tqdm import tqdm

def load_model_and_tokenizer(model_path):
    print("Loading model and tokenizer...")
    try:
        # Force CPU usage
        device = "cpu"
        print(f"Using device: {device}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with CPU
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # Use float32 for CPU
            device_map="cpu"
        )
        
        return model, tokenizer, device
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def generate_text(model, tokenizer, prompt, device, max_length=512):
    try:
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate with more conservative parameters
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3
        )
        
        # Decode and clean output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        return None

def main():
    # Model path
    model_path = "deepseek-ai/deepseek-coder-1.3b-base"
    
    try:
        # Load model and tokenizer
        model, tokenizer, device = load_model_and_tokenizer(model_path)
        
        # Test prompts
        test_prompts = [
            "Escribe un artículo sobre la importancia de la educación financiera",
            "Explica los beneficios de invertir en el mercado de valores",
            "Describe las mejores prácticas para ahorrar dinero"
        ]
        
        print("\nGenerating responses...")
        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            response = generate_text(model, tokenizer, prompt, device)
            if response:
                print(f"Response: {response}")
            else:
                print("Failed to generate response")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 