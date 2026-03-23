"""
Backend API Server

Flask REST API for frontend communication
"""
import sys
from pathlib import Path

# Add src path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

from orchestrator import AgentOrchestrator
from session.manager import SessionManager
from knowledge.store import KnowledgeStore
from agents.chat import ChatAgent
from agents.researcher import ResearcherAgent
from core.config import Config

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize components
session_manager = SessionManager()
knowledge_store = KnowledgeStore()
chat_agent = ChatAgent()
researcher_agent = ResearcherAgent(knowledge_store=knowledge_store)
orchestrator = AgentOrchestrator(
    chat_agent=chat_agent,
    researcher_agent=researcher_agent,
    session_manager=session_manager,
)


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint

    Request:
        {
            "message": "user input",
            "session_id": "optional session ID"
        }

    Response:
        {
            "response": "AI response",
            "session_id": "session ID",
            "agent": "agent used"
        }
    """
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id')

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    try:
        # Process message
        response, agent_used = orchestrator.process_message(
            message=message,
            session_id=session_id,
        )

        # Get or create session_id
        if not session_id:
            sessions = session_manager.list_sessions()
            if sessions:
                session_id = sessions[0]['id']

        return jsonify({
            'response': response,
            'session_id': session_id,
            'agent': agent_used,
        })

    except Exception as e:
        app.logger.error(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    sessions = session_manager.list_sessions()
    return jsonify({'sessions': sessions})


@app.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    success = session_manager.delete_session(session_id)
    if success:
        return jsonify({'message': 'Session deleted'})
    return jsonify({'error': 'Session not found'}), 404


@app.route('/knowledge/add', methods=['POST'])
def add_knowledge():
    """
    Add knowledge to knowledge base

    Request:
        {
            "text": "text content",
            "metadata": {}  # optional metadata
        }
    """
    data = request.json
    text = data.get('text', '')
    metadata = data.get('metadata', {})

    if not text:
        return jsonify({'error': 'Text cannot be empty'}), 400

    try:
        from knowledge.loader import DocumentLoader

        loader = DocumentLoader()
        documents = loader.load_from_text(text, metadata)

        knowledge_store.add_documents(
            documents=[d['content'] for d in documents],
            ids=[d['id'] for d in documents],
            metadatas=[d['metadata'] for d in documents],
        )

        return jsonify({
            'message': f'Successfully added {len(documents)} document(s)',
            'count': len(documents),
        })

    except Exception as e:
        app.logger.error(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/knowledge/status', methods=['GET'])
def knowledge_status():
    """Get knowledge base status"""
    return jsonify({
        'document_count': knowledge_store.get_document_count(),
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Agent Hub API Server")
    print("=" * 60)
    print(f"Running at: http://localhost:8080")
    print()
    print("API Endpoints:")
    print("  POST /chat         - Chat")
    print("  GET  /sessions     - Get sessions list")
    print("  DELETE /sessions/:id - Delete session")
    print("  POST /knowledge/add - Add knowledge")
    print("  GET  /knowledge/status - Knowledge base status")
    print("=" * 60)

    # Validate configuration
    if not Config.DASHSCOPE_API_KEY or Config.DASHSCOPE_API_KEY == "your-api-key-here":
        print("Warning: Please configure DASHSCOPE_API_KEY")
    else:
        print("API Key: Configured")

    app.run(debug=True, host='0.0.0.0', port=8080)
