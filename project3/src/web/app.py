"""Flask web application for relationship generation."""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from ..clients import OpenAIClient, Project1Client
from ..clients.ollama_client import OllamaClient
from ..clients.deepseek_client import DeepSeekClient
from ..config import load_config
from ..services import NodeService, RelationshipService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

# Load configuration
config = load_config()

# Initialize clients (lazy loading pattern)
_openai_client = None
_project1_client = None
_node_service = None
_relationship_service = None


def get_llm_client():
    """Get or create LLM client based on provider."""
    global _openai_client
    if _openai_client is None:
        provider = config["llm_provider"]
        
        if provider == "openai":
            _openai_client = OpenAIClient(
                api_key=config["openai_api_key"],
                model=config["openai_model"],
            )
        elif provider == "ollama":
            _openai_client = OllamaClient(
                base_url=config["ollama_base_url"],
                model=config["ollama_model"],
            )
        elif provider == "deepseek":
            _openai_client = DeepSeekClient(
                api_key=config["deepseek_api_key"],
                model=config["deepseek_model"],
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"Initialized LLM client: {provider}")
    
    return _openai_client


def get_project1_client() -> Project1Client:
    """Get or create Project1 client."""
    global _project1_client
    if _project1_client is None:
        _project1_client = Project1Client(
            base_url=config["project1_api_url"],
            token=config.get("project1_api_token"),
        )
    return _project1_client


def get_node_service() -> NodeService:
    """Get or create node service."""
    global _node_service
    if _node_service is None:
        _node_service = NodeService(
            project1_client=get_project1_client(),
            openai_client=get_llm_client(),
        )
    return _node_service


def get_relationship_service() -> RelationshipService:
    """Get or create relationship service."""
    global _relationship_service
    if _relationship_service is None:
        _relationship_service = RelationshipService(
            project1_client=get_project1_client(),
            openai_client=get_llm_client(),
            node_service=get_node_service(),
        )
    return _relationship_service


@app.route("/")
def index():
    """Main page for generating relationships."""
    return render_template("index.html")


@app.route("/review")
def review():
    """Review page for approving relationships."""
    return render_template("review.html")


@app.route("/api/validate-ticker", methods=["POST"])
def api_validate_ticker():
    """Validate a ticker and get/generate company info."""
    try:
        data = request.json
        ticker = data.get("ticker", "").strip().upper()
        
        if not ticker:
            return jsonify({"error": "Ticker is required"}), 400
        
        node_service = get_node_service()
        
        # Validate ticker format
        if not node_service.validate_ticker(ticker):
            return jsonify({"error": "Invalid ticker format (1-5 letters)"}), 400
        
        # Check if node exists
        existing_node = node_service.get_or_create_node(ticker)
        
        if existing_node:
            logger.info(f"Ticker {ticker} exists in database")
            return jsonify({
                "exists": True,
                "company": existing_node,
            })
        else:
            # Generate company info using AI
            logger.info(f"Generating info for ticker {ticker}")
            company_info = node_service.generate_company_info(ticker)
            
            return jsonify({
                "exists": False,
                "generated_info": company_info,
            })
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate relationships API endpoint."""
    try:
        data = request.json
        source_company = data.get("source_company")
        count = data.get("count", 5)
        include_metadata = data.get("include_metadata", True)
        
        if not source_company:
            return jsonify({"error": "source_company is required"}), 400
        
        # Validate count
        if count < 1 or count > 20:
            return jsonify({"error": "count must be between 1 and 20"}), 400
        
        relationship_service = get_relationship_service()
        
        # Generate relationships
        logger.info(f"Generating {count} relationships for {source_company.get('id')} (metadata: {include_metadata})")
        relationships = relationship_service.generate_relationships(
            source_company=source_company,
            count=count,
            include_metadata=include_metadata,
        )
        
        return jsonify({
            "success": True,
            "relationships": relationships,
            "source_company": source_company,
        })
        
    except ValueError as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/approve", methods=["POST"])
def api_approve():
    """Approve and submit relationships to project1."""
    try:
        data = request.json
        relationships = data.get("relationships", [])
        approved_indices = data.get("approved_indices", [])
        source_company = data.get("source_company", {})
        
        if not relationships:
            return jsonify({"error": "relationships is required"}), 400
        
        if not approved_indices:
            return jsonify({"error": "No relationships approved"}), 400
        
        source_id = source_company.get("id")
        if not source_id:
            return jsonify({"error": "source_company.id is required"}), 400
        
        node_service = get_node_service()
        relationship_service = get_relationship_service()
        
        # Ensure source node exists
        existing_source = node_service.get_or_create_node(source_id)
        if not existing_source:
            # Source node doesn't exist, create it
            logger.info(f"Creating source node: {source_id}")
            node_service.create_node(source_company)
        
        # Process each approved relationship
        results = []
        for idx in approved_indices:
            if idx >= len(relationships):
                continue
            
            rel_data = relationships[idx]
            target_company = rel_data.get("target_company", {})
            relationship = rel_data.get("relationship", {})
            
            logger.info(f"Creating relationship: {source_id} -> {target_company.get('id')}")
            result = relationship_service.create_relationship(
                source_id=source_id,
                target_company=target_company,
                relationship=relationship,
            )
            result["index"] = idx
            results.append(result)
        
        success_count = len([r for r in results if r["status"] == "success"])
        logger.info(f"Successfully created {success_count}/{len(results)} relationships")
        
        return jsonify({
            "success": True,
            "results": results,
        })
        
    except Exception as e:
        logger.error(f"Approval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/existing-companies", methods=["GET"])
def api_existing_companies():
    """Get existing companies from project1."""
    try:
        node_service = get_node_service()
        companies = node_service.get_all_companies()
        
        return jsonify({
            "success": True,
            "companies": companies,
        })
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "project3-web",
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="127.0.0.1", port=port)
