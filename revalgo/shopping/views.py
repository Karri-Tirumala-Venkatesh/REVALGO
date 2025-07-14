import os
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# import google.generativeai as genai
# from google.api_core.exceptions import GoogleAPIError, RetryError


# --- API Key Management ---
# It's crucial to load API keys from environment variables for security.
# Never hardcode sensitive keys directly in your source code.
# For production, consider using: GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# GEMINI_API_KEY = "KEY"


# try:
#     genai.configure(api_key=GEMINI_API_KEY)
# except Exception as e:
#     # Log the error for debugging, but avoid exposing sensitive details in production
#     print(f"Error configuring Gemini API: {e}")
#     raise

# GEMINI_MODEL_NAME = "gemini-1.5-flash"

# --- Shopping Agent System Instruction ---
# This prompt is now mostly for reference as the responses are hardcoded.
SHOPPING_AGENT_PROMPT = """
You are a friendly, helpful, and knowledgeable shopping assistant named "ShopBuddy".
Your primary goal is to assist users in finding products, providing relevant recommendations, and answering any questions they have about shopping. You are adept at guiding users through a shopping journey from initial query to checkout.

Here's how you should interact, following a conversational and proactive approach:
1.  **Initial Understanding & Clarification:**
    * When a user asks for a product or gift, immediately ask clarifying questions to understand their specific needs, preferences, budget, recipient's age/interests, and any urgency (e.g., "delivered by tomorrow").
    * Proactively ask about the type of gift they're looking for (e.g., "single main gift, gift bundle, or return gifts").

2.  **Structured Recommendations:**
    * Based on gathered information, offer relevant product recommendations.
    * **Always present recommendations as a numbered list.**
    * For each recommendation, provide:
        * A clear name and estimated price. **Always use Markdown for formatting product names as bold (`**Product Name**`) and prices as italic (`*₹Price*`).**
        * A brief, appealing description of its key features or benefits.
        * Mention delivery availability if relevant (e.g., "Next-day delivery available").
    * Ask if they'd like more details or photos (even if you can't provide photos, this simulates a real shopping experience).

3.  **Handling Add-ons and Details:**
    * When a user expresses interest in a product, offer to provide more details.
    * **Present these details as a bulleted list.**
    * Proactively ask about common add-ons like gift wrap, personalized cards, or other related items. Confirm these additions clearly.

4.  **Managing Multiple Items (e.g., Return Gifts):**
    * If return gifts or other categories are requested, offer a few distinct options with prices. **Format these similarly with bold product names and italic prices, and present them as a numbered or bulleted list.**
    * Confirm their selection before moving on.

5.  **Order Summary & Discounts:**
    * Once items are selected, provide a clear summary of the chosen products and add-ons, including their individual prices. **Present the summary as a bulleted list.**
    * Calculate the subtotal.
    * Proactively mention any applicable discounts (e.g., "You qualify for a 10% bundle discount") and the new total.
    * Reconfirm delivery details.

6.  **Guiding to Checkout:**
    * Ask if they would like to proceed to checkout.
    * Upon confirmation, guide them through the final steps (e.g., "confirm delivery address and choose your payment method").
    * Simulate order confirmation and tracking link information.

7.  **Post-Purchase Assistance:**
    * After order confirmation, offer additional helpful services (e.g., "reminder for next year's birthday," "help with party decorations").
    * If party decorations or other items are requested, provide quick ideas with estimated prices and delivery info, similar to product recommendations. **Format these with bold product names and italic prices, and present them as a numbered or bulleted list.**

8.  **Tone and Emojis:**
    * Maintain a polite, enthusiastic, and encouraging tone throughout the conversation.
    * Use appropriate emojis (like 🎉, 🎂, 🎈) to enhance friendliness and express excitement.

9.  **Limitations:**
    * You do not have access to real-time product databases, exact prices, or live inventory. Base your recommendations and answers on general knowledge. Do not invent specific product names, prices, or availability that are not generic examples.
    * If a user asks for something that requires real-time data, gently remind them of your limitations and offer general advice or examples instead.

Example Interaction Flow (as per user's detailed example):
User: Hi! I need to find a birthday present for my son. He turns 10 tomorrow.
ShopBuddy: Happy early birthday to your son! 🎉 I’d love to help you find the perfect gift. Could you tell me a bit about his interests? For example, does he like science, sports, art, or something else?

User: He loves science experiments, drawing, and playing outside with his friends.
ShopBuddy: That’s wonderful! Thank you for sharing. Do you have a budget in mind for the main gift?

User: Around ₹3,000. Also, I need it delivered by tomorrow if possible.
ShopBuddy: Got it—birthday gift for a 10-year-old boy, science and art lover, outdoor play, budget ₹3,000, and urgent delivery. Would you like a single main gift, or are you interested in a gift bundle or maybe some return gifts for party guests as well?

User: A main gift and maybe something small for the kids who come to the party.
ShopBuddy: Perfect! Here are some main gift ideas that can be delivered by tomorrow:
1. **DIY Volcano Science Kit** – *₹1,499*
   Includes all materials for safe, fun experiments.
2. **Personalized Art Supplies Set** – *₹2,299*
   Comes with his name printed on the case.
3. **Outdoor Frisbee & Cricket Starter Kit** – *₹2,899*
   For active play with friends.
   ![Frisbee & Cricket Kit](https://example.com/images/frisbee_cricket_kit.jpg)
Would you like more details or photos of any of these?
"""


def index(request):
    """Renders the shopping index page."""
    # Clear chat history and conversation step on page load/refresh
    if 'chat_history' in request.session:
        del request.session['chat_history']
    if 'conversation_step' in request.session:
        del request.session['conversation_step']
    request.session.modified = True # Ensure session is saved after modification
    return render(request, 'shopping/index.html')

def recommendations(request):
    """Renders the recommendations page."""
    return render(request, 'shopping/recommendations.html')

@require_POST
def gemini_chat(request):
    """
    Handles chat requests to Gemini API using the official SDK.
    Expects JSON body: {"message": "...}
    Returns: {"reply": "...}
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'reply': "Invalid JSON format in request."}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'reply': "No message provided."}, status=400)

    # Session chat history and conversation step
    try:
        history = request.session.get('chat_history', [])
        conversation_step = request.session.get('conversation_step', 0) # Initialize step
        if not isinstance(history, list):
            history = []
            request.session['chat_history'] = history
            conversation_step = 0 # Reset step if history is malformed
    except Exception as e:
        print(f"Error retrieving session data: {e}")
        return JsonResponse({'reply': "Internal server error: Could not retrieve session data."}, status=500)

    # --- Fixed Chatbot Logic (for prototype video) ---
    # Commented out Gemini API integration for a firm, pre-defined chat flow.
    gemini_reply = ""
    next_conversation_step = conversation_step # Default to current step if no match

    # Define the script as a dictionary for easier management
    # Each key is the current conversation_step
    # Value is a tuple: (expected_user_input_keywords, bot_reply, next_step)
    # Using keywords for flexibility, but exact match can be enforced if needed.
    script = {
        0: (["hi!", "birthday present for my son"],
            "Happy early birthday to your son! 🎉🥳 I’d love to help you find the perfect gift. Could you tell me a bit about his interests? For example, does he like science, sports, art, or something else? 🤔",
            1),
        1: (["science experiments", "drawing", "playing outside"],
            "That’s wonderful! 🧪🎨⚽ Thank you for sharing. Do you have a budget in mind for the main gift? 💸",
            2),
        2: (["₹3,000", "delivered by tomorrow"],
            "Got it! birthday gift for a 10-year-old boy, science and art lover, outdoor play, budget ₹3,000, and urgent delivery.🚚⏰\n Would you like a single main gift, or are you interested in a gift bundle or maybe some return gifts for party guests as well? 🎁👫",
            3),
        3: (["main gift", "something small for the kids"],
            "Perfect! 👍 Here are some main gift ideas that can be delivered by tomorrow:\n\n"
            "1. DIY Volcano Science Kit 🧪🌋 – ₹1,499\n"
            "   - Includes all materials for safe, fun experiments.\n\n"
            "2. Personalized Art Supplies Set 🎨✏️ – ₹2,299\n"
            "   - Comes with his name printed on the case.\n\n"
            "3. Outdoor Frisbee & Cricket Starter Kit 🏏🥏 – ₹2,899\n"
            "   - For active play with friends.\n\n"
            "Would you like more details or photos of any of these? 📸",
            4),
        4: (["art supplies set", "volcano kit"],
            "Here are the details:\n\nPersonalized Art Supplies Set 🎨\n![Art Supplies Set](/static/images/img2.jpg)\n- 48-piece set with markers, crayons, paints, and sketchbook\n- Durable carry case with your son’s name 👜\n- Highly rated by parents (4.8/5 stars) ⭐⭐⭐⭐⭐\n- Next-day delivery available 🚚\n\nDIY Volcano Science Kit 🌋\n![Volcano Kit](/static/images/img1.png)\n- Safe, reusable kit for building and erupting a volcano\n- Includes colored powders, safety goggles, and instruction booklet 🥽📖\n- Great for hands-on learning\n- Next-day delivery available 🚚\n\nWould you like to add gift wrap or a birthday card for either of these? 🎁💌",
            5),
        5: (["gift wrap", "birthday card", "happy 10th birthday, aryan!"],
            "Done! ✅ Gift wrap 🎁 and a personalized birthday card 💌 have been added.\n\nNow, for return gifts, here are a few, under ₹200 each, available for next-day delivery:\n\n Mini Puzzle Cubes (set of 10) 🧩 – ₹1,800\n![Mini Puzzle Cubes](/static/images/img1.png)\n\n DIY Slime Kits (set of 8) 🧫 – ₹1,600\n![DIY Slime Kits](/static/images/img2.jpg)\n\n Art Sticker Packs (set of 12) 🖼️ – ₹1,500\n![Art Sticker Packs](/static/images/img3.jpg)\n\nWould you like to add any of these for the party guests?",
            6),
        6: (["mini puzzle cubes"],
            "Great choice! 👍 Mini Puzzle Cubes set of 10 🧩 added to your cart.\n\nHere’s a summary of your order:\n Personalized Art Supplies Set – ₹2,299 🎨\n Gift wrap & personalized card – ₹150 🎁💌\n Mini Puzzle Cubes (10) – ₹1,800 🧩\nTotal: ₹4,249\n\nYou qualify for a 10% BUNDLE discount 🏷️, and everything will be delivered by tomorrow. 🚚 Would you like to proceed to checkout? 🛒",
            7),
        7: (["yes"],
            "All set! ✅ Please confirm your delivery address 📍 and choose your payment method 💳 to complete the order.",
            8),
        8: (["address is the same as last time", "pay by card"],
            "Thank you! 🙏 Your order is confirmed. 🎉 You’ll receive a tracking link and delivery updates shortly. 📦\nWould you like a reminder for Aryan’s birthday next year, or any help with party decorations? 🎈",
            9),
        9: (["reminder for next year", "decoration ideas"],
            "You got it! 👍 I’ll remind you a month before Aryan’s next birthday. 📅\n\nHere are some easy party decoration kits at ₹500, all available for fast delivery:\nBalloon Garland Kit 🎈\n- “Happy Birthday” Banner Set 🎉\n- Tableware & Confetti Pack 🍽️✨\n\nWould you like to add any of these?",
            10),
        10: (["banner set"],
             "Banner set 🎉 added. Thank you for shopping with us! Have a fantastic birthday celebration for Aryan! 🎂🎈🥳",
             11) # End of script
    }

    user_message_lower = user_message.lower()

    # Check if the current conversation step exists in the script
    if conversation_step in script:
        expected_keywords, bot_response, next_step_val = script[conversation_step]
        # Check if any of the expected keywords are in the user's message
        if any(keyword in user_message_lower for keyword in expected_keywords):
            gemini_reply = bot_response
            next_conversation_step = next_step_val
        else:
            # Fallback if user input doesn't match expected for the current step
            gemini_reply = "I'm sorry, I can only follow the pre-defined script for this prototype. Please try to use phrases similar to the example conversation to proceed. You are currently at step " + str(conversation_step) + "."
    else:
        # If conversation_step goes beyond the script, or is an unexpected value
        gemini_reply = "The conversation script has ended or an unexpected error occurred. You can start over by clearing your session history (e.g., refreshing the page)."


    # --- End of Fixed Chatbot Logic ---

    # Add to session history (no login required)
    try:
        history.append({'role': 'user', 'parts': [{'text': user_message}]})
        history.append({'role': 'model', 'parts': [{'text': gemini_reply}]})
        request.session['chat_history'] = history
        request.session['conversation_step'] = next_conversation_step # Update the step
        request.session.modified = True
    except Exception as e:
        print(f"Failed to save chat history: {e}") # Log the error
        return JsonResponse({'reply': f"Failed to save chat history. AI replied: {gemini_reply}"}, status=500)

    return JsonResponse({'reply': gemini_reply})
