"""Chatbot feature for KaranBOT."""

from flask import Blueprint, render_template, request, jsonify
from .models import db, Driver, Truck, Trailer, WorkshopJob

chatbot_bp = Blueprint('chatbot', __name__, template_folder='templates', static_folder='static')

@chatbot_bp.route('/chat')
def chat():
    """Render the main chat interface."""
    return render_template('chatbot/chat.html')

@chatbot_bp.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle incoming chat messages and return a response."""
    data = request.get_json()
    user_message = data.get('message', '').lower().strip()
    
    response = "I'm sorry, I don't understand that question. Try asking something like 'how many trucks are there?' or 'list all drivers'."

    # Simple rule-based logic
    if 'how many' in user_message:
        if 'drivers' in user_message:
            count = Driver.query.count()
            response = f"There are currently {count} drivers in the system."
        elif 'trucks' in user_message:
            count = Truck.query.count()
            response = f"There are currently {count} trucks in the system."
        elif 'trailers' in user_message:
            count = Trailer.query.count()
            response = f"There are currently {count} trailers in the system."
        elif 'workshop jobs' in user_message or 'jobs' in user_message:
            count = WorkshopJob.query.count()
            response = f"There are currently {count} active workshop jobs."

    elif 'list all' in user_message or 'show all' in user_message:
        if 'drivers' in user_message:
            items = Driver.query.all()
            names = [item.name for item in items]
            response = "Here are all the drivers: " + ", ".join(names) if names else "There are no drivers to list."
        elif 'trucks' in user_message:
            items = Truck.query.all()
            names = [item.registration for item in items]
            response = "Here are all the trucks: " + ", ".join(names) if names else "There are no trucks to list."
        elif 'trailers' in user_message:
            items = Trailer.query.all()
            names = [item.registration for item in items]
            response = "Here are all the trailers: " + ", ".join(names) if names else "There are no trailers to list."

    return jsonify({'response': response})
