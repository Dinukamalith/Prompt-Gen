from src.models.user import db
from datetime import datetime
import json

class PromptTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    ai_tool = db.Column(db.String(50), nullable=False)
    template_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'ai_tool': self.ai_tool,
            'template_content': self.template_content,
            'created_at': self.created_at.isoformat()
        }

class GeneratedPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_input = db.Column(db.Text, nullable=False)
    ai_tool = db.Column(db.String(50), nullable=False)
    output_style = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    seo_keywords = db.Column(db.Text)
    generated_prompt = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.Text)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_input': self.original_input,
            'ai_tool': self.ai_tool,
            'output_style': self.output_style,
            'category': self.category,
            'seo_keywords': self.seo_keywords,
            'generated_prompt': self.generated_prompt,
            'analysis': self.analysis,
            'score': self.score,
            'created_at': self.created_at.isoformat()
        }

