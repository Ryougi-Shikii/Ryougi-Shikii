from flask import Flask, request, jsonify, render_template
import torch
from model import Transformer
from dataset import Vocabulary
from inference import beam_search, greedy_decode

app = Flask(__name__)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Configuration for the models
MODEL_PATHS = {
    "reverse": "saved_models/reverse_model.pt",
    "caesar": "saved_models/caesar_model.pt",
    "sort": "saved_models/sort_model.pt"
}

# Dictionary to hold the loaded resources for each task
models_registry = {}

def load_resources():
    for task, path in MODEL_PATHS.items():
        print(f"Loading {task} model...")
        checkpoint = torch.load(path, map_location=DEVICE)
        
        # Vocab setup
        src_vocab = Vocabulary()
        src_vocab.token2idx = checkpoint["src_token2idx"]
        src_vocab.idx2token = checkpoint["src_idx2token"]
        
        tgt_vocab = Vocabulary()
        tgt_vocab.token2idx = checkpoint["tgt_token2idx"]
        tgt_vocab.idx2token = checkpoint["tgt_idx2token"]
        
        # Model setup
        model = Transformer(**checkpoint["model_config"]).to(DEVICE)
        model.load_state_dict(checkpoint["model_state"])
        model.eval()
        
        models_registry[task] = {
            "model": model,
            "src_vocab": src_vocab,
            "tgt_vocab": tgt_vocab
        }
    print("All models loaded successfully.")

load_resources()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get("text", "")
    task = data.get("task", "reverse")  # Default to reverse
    method = data.get("method", "greedy")
    
    if task not in models_registry:
        return jsonify({"error": "Invalid task selection"}), 400
    if not text:
        return jsonify({"error": "No text provided"}), 400

    res = models_registry[task]
    src = torch.tensor(
        [res["src_vocab"].encode(list(text))], dtype=torch.long, device=DEVICE
    )

    with torch.no_grad():
        if method == "beam":
            ids = beam_search(res["model"], src, Vocabulary.SOS, Vocabulary.EOS, beam_size=4, device=DEVICE)
        else:
            ids = greedy_decode(res["model"], src, Vocabulary.SOS, Vocabulary.EOS, device=DEVICE)

    output = "".join(res["tgt_vocab"].idx2token[i] for i in ids 
                     if i not in {Vocabulary.PAD, Vocabulary.SOS, Vocabulary.EOS, Vocabulary.UNK})

    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)