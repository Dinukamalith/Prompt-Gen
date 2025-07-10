from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.prompt import GeneratedPrompt, PromptTemplate, db
from src.prompt_engine import PromptEngine
import json

prompt_bp = Blueprint('prompt', __name__)
engine = PromptEngine()

@prompt_bp.route('/generate', methods=['POST'])
@cross_origin()
def generate_prompt():
    """Generate a new prompt from user input"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['user_input', 'ai_tool', 'output_style', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        user_input = data['user_input']
        ai_tool = data['ai_tool']
        output_style = data['output_style']
        category = data['category']
        seo_keywords = data.get('seo_keywords', '')
        
        # Generate the prompt
        result = engine.generate_prompt(
            user_input=user_input,
            ai_tool=ai_tool,
            output_style=output_style,
            category=category,
            seo_keywords=seo_keywords,
            operation='generate'
        )
        
        # Save to database
        generated_prompt = GeneratedPrompt(
            original_input=user_input,
            ai_tool=ai_tool,
            output_style=output_style,
            category=category,
            seo_keywords=seo_keywords,
            generated_prompt=result['generated_prompt'],
            analysis=result['analysis'],
            score=result['score']
        )
        
        db.session.add(generated_prompt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': generated_prompt.id,
                'generated_prompt': result['generated_prompt'],
                'analysis': result['analysis'],
                'score': result['score'],
                'template_used': result['template_used'],
                'ai_tool': ai_tool,
                'category': category
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/improve', methods=['POST'])
@cross_origin()
def improve_prompt():
    """Improve an existing prompt"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['existing_prompt', 'ai_tool', 'output_style', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        existing_prompt = data['existing_prompt']
        ai_tool = data['ai_tool']
        output_style = data['output_style']
        category = data['category']
        
        # Improve the prompt
        result = engine.improve_existing_prompt(
            existing_prompt=existing_prompt,
            ai_tool=ai_tool,
            output_style=output_style,
            category=category
        )
        
        # Save to database
        generated_prompt = GeneratedPrompt(
            original_input=existing_prompt,
            ai_tool=ai_tool,
            output_style=output_style,
            category=category,
            seo_keywords='',
            generated_prompt=result['generated_prompt'],
            analysis=result['analysis'],
            score=result['score']
        )
        
        db.session.add(generated_prompt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': generated_prompt.id,
                'generated_prompt': result['generated_prompt'],
                'analysis': result['analysis'],
                'score': result['score'],
                'improvements_made': result['improvements_made'],
                'ai_tool': ai_tool,
                'category': category
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_prompt():
    """Analyze a prompt without modifying it"""
    try:
        data = request.json
        
        if 'prompt' not in data:
            return jsonify({'error': 'Missing required field: prompt'}), 400
        
        prompt = data['prompt']
        ai_tool = data.get('ai_tool', 'chatgpt')
        category = data.get('category', 'content_generation')
        
        # Analyze the prompt
        analysis = engine._analyze_prompt(prompt, ai_tool, category)
        score = engine._score_prompt(prompt, ai_tool, category)
        issues = engine._identify_prompt_issues(prompt)
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis,
                'score': score,
                'issues': issues,
                'word_count': len(prompt.split()),
                'character_count': len(prompt)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/templates', methods=['GET'])
@cross_origin()
def get_templates():
    """Get available prompt templates"""
    try:
        templates = engine.templates
        return jsonify({
            'success': True,
            'data': templates
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """Get user's prompt generation history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        prompts = GeneratedPrompt.query.order_by(
            GeneratedPrompt.created_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'prompts': [prompt.to_dict() for prompt in prompts.items],
                'total': prompts.total,
                'pages': prompts.pages,
                'current_page': page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/export/<int:prompt_id>', methods=['GET'])
@cross_origin()
def export_prompt(prompt_id):
    """Export a specific prompt"""
    try:
        prompt = GeneratedPrompt.query.get_or_404(prompt_id)
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'data': prompt.to_dict()
            })
        elif format_type == 'txt':
            content = f"Generated Prompt:\n{prompt.generated_prompt}\n\nAnalysis:\n{prompt.analysis}\n\nScore: {prompt.score}/100"
            return content, 200, {'Content-Type': 'text/plain'}
        else:
            return jsonify({'error': 'Invalid format. Use json or txt'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """Get available categories"""
    try:
        categories = {
            'content_generation': 'Content Generation',
            'image_generation': 'Image Generation', 
            'code_generation': 'Code Generation',
            'data_analysis': 'Data Analysis',
            'marketing': 'Marketing'
        }
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/ai-tools', methods=['GET'])
@cross_origin()
def get_ai_tools():
    """Get available AI tools"""
    try:
        ai_tools = {
            'chatgpt': 'ChatGPT (GPT-4)',
            'claude': 'Claude 3',
            'gemini': 'Google Gemini',
            'midjourney': 'Midjourney',
            'dalle': 'DALL-E'
        }
        
        return jsonify({
            'success': True,
            'data': ai_tools
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_bp.route('/output-styles', methods=['GET'])
@cross_origin()
def get_output_styles():
    """Get available output styles"""
    try:
        styles = {
            'creative': 'Creative',
            'technical': 'Technical',
            'marketing': 'Marketing',
            'research': 'Research'
        }
        
        return jsonify({
            'success': True,
            'data': styles
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

