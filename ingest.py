import json
from pypdf import PdfReader

def ingest_rules():
    pdf_path = "rules.pdf" # Make sure your file is named this!
    print(f"📖 Opening {pdf_path}...")
    
    try:
        reader = PdfReader(pdf_path)
    except FileNotFoundError:
        print("❌ Error: 'rules.pdf' not found. Please upload the PDF.")
        return

    knowledge_base = []
    
    print("⚙️ Processing pages... (This might take a moment)")
    
    # Loop through every page
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # We only care about pages with actual text
        if text and len(text) > 50:
            # Create a simple "Chunk" of knowledge
            entry = {
                "id": f"page_{i+1}",
                "text": text,  # The raw content
                "section": f"Page {i+1}" # Citation
            }
            knowledge_base.append(entry)

    # Save to a generic JSON file (Our "Database")
    with open("knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2)
        
    print(f"✅ Success! Extracted {len(knowledge_base)} pages.")
    print("💾 Saved to 'knowledge_base.json'. Your bot can now read this!")

if __name__ == "__main__":
    ingest_rules()