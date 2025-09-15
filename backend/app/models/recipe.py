from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class Recipe(Base):
    """Recipe model for meal planning."""
    
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Recipe details
    ingredients = Column(Text, nullable=False)  # JSON string of ingredients
    instructions = Column(Text, nullable=False)  # JSON string of instructions
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, default=1)
    difficulty_level = Column(String(50), nullable=True)
    
    # Categorization and tags
    tags = Column(Text, nullable=True)  # JSON string of tags
    cuisine_type = Column(String(100), nullable=True)
    meal_type = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack
    
    # Nutrition information
    nutrition_facts = Column(Text, nullable=True)  # JSON string
    calories_per_serving = Column(Float, nullable=True)
    protein_grams = Column(Float, nullable=True)
    carbs_grams = Column(Float, nullable=True)
    fat_grams = Column(Float, nullable=True)
    fiber_grams = Column(Float, nullable=True)
    
    # Media
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    
    # Creator and visibility
    created_by_trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Ratings and usage
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("Trainer", backref="created_recipes")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="recipe")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', creator_id={self.created_by_trainer_id})>"
