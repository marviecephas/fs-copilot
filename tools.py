import json

def get_rules_from_db(query: str):
    """
    Smarter Search: Prioritizes pages with dense information,
    strictly removes Table of Contents.
    """
    print(f"🔍 SEARCHING PDF for: '{query}'")
    
    try:
        with open("knowledge_base.json", "r") as f:
            rules_db = json.load(f)
    except FileNotFoundError:
        return "Error: Database not found."

    query_words = query.lower().split()
    scored_results = []

    for page in rules_db:
        content = page["text"].lower()
        
        # --- CODE TO REMOVE TABLE OF CONTENTS ---
        # If the page mentions "Table of Contents" or has dotted lines "....."
        if "table of contents" in content or "....." in content:
            continue # Skip this page entirely!
        # ----------------------------------------
        
        # 1. Count how many keywords appear on this page
        score = 0
        for word in query_words:
            if len(word) > 3: # Ignore small words like "the", "for"
                score += content.count(word)

        # 2. If relevant, save it
        if score > 0:
            scored_results.append((score, page))

    # 3. Sort by highest score (Most matches first!)
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # 4. Return the top 3 BEST pages
    if scored_results:
        top_hits = scored_results[:10]
        result_text = f"FOUND {len(scored_results)} MATCHES. TOP 10:\n\n"
        for score, page in top_hits:
            # Clean up newlines for easier reading
            clean_text = page['text'].replace('\n', ' ') 
            result_text += f"--- [Page {page['id']} | Score: {score}] ---\n{clean_text}...\n\n"
        return result_text
    
    return "No relevant rules found."