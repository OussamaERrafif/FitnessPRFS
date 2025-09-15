from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.session import Base


class MealPlanType(PyEnum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    CUTTING = "cutting"
    BULKING = "bulking"
    PERFORMANCE = "performance"
    GENERAL_HEALTH = "general_health"


class DietaryRestriction(PyEnum):
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low_carb"
    LOW_FAT = "low_fat"
    HALAL = "halal"
    KOSHER = "kosher"


class MealType(PyEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"


class DietType(PyEnum):
    STANDARD = "standard"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low_carb"
    MEDITERRANEAN = "mediterranean"
    DASH = "dash"
    INTERMITTENT_FASTING = "intermittent_fasting"


class MealPlan(Base):
    """Meal plan model for nutrition tracking."""
    
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Assignment
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by_trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    
    # Plan details
    plan_type = Column(String(50), nullable=False)  # MealPlanType enum as string
    duration_days = Column(Integer, nullable=False)  # Plan duration in days
    
    # Dietary information
    dietary_restrictions = Column(Text, nullable=True)  # JSON string of restrictions
    allergens_to_avoid = Column(Text, nullable=True)  # JSON string of allergens
    
    # Nutritional targets
    target_calories = Column(Float, nullable=True)
    target_protein_grams = Column(Float, nullable=True)
    target_carbs_grams = Column(Float, nullable=True)
    target_fat_grams = Column(Float, nullable=True)
    target_fiber_grams = Column(Float, nullable=True)
    
    # Macro ratios (percentages)
    protein_percentage = Column(Float, nullable=True)
    carbs_percentage = Column(Float, nullable=True)
    fat_percentage = Column(Float, nullable=True)
    
    # Meal structure
    meals_per_day = Column(Integer, default=3)
    snacks_per_day = Column(Integer, default=2)
    
    # Plan structure (JSON)
    weekly_meal_plan = Column(Text, nullable=True)  # JSON structure of weekly meals
    recipes = Column(Text, nullable=True)  # JSON list of recipes used
    shopping_list = Column(Text, nullable=True)  # JSON shopping list
    
    # Status and dates
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Progress tracking
    adherence_percentage = Column(Float, default=0.0)  # How well client follows the plan
    
    # Customization
    preferences = Column(Text, nullable=True)  # JSON string of food preferences
    dislikes = Column(Text, nullable=True)  # JSON string of foods to avoid
    notes = Column(Text, nullable=True)
    
    # Template information
    is_template = Column(Boolean, default=False)
    created_from_template_id = Column(Integer, nullable=True)
    
    # Pricing (if applicable)
    price = Column(Float, nullable=True)
    is_paid = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="meal_plans")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MealPlan(id={self.id}, name='{self.name}', client_id={self.client_id})>"


class MealPlanRecipe(Base):
    """Junction table connecting meal plans to recipes with scheduling information."""
    
    __tablename__ = "meal_plan_recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    # Meal scheduling
    day_number = Column(Integer, nullable=False)  # Day 1, 2, 3, etc. in the meal plan
    meal_type = Column(String(50), nullable=False)  # MealType enum as string
    meal_order = Column(Integer, default=1)  # Order within the same meal type (for multiple items)
    
    # Serving information
    servings = Column(Float, default=1.0)  # How many servings of this recipe
    portion_size = Column(String(100), nullable=True)  # e.g., "1 cup", "200g"
    
    # Customization
    preparation_notes = Column(Text, nullable=True)  # Special preparation instructions
    substitutions = Column(Text, nullable=True)  # Alternative ingredients or recipes
    
    # Nutritional overrides (if different from base recipe)
    override_calories = Column(Float, nullable=True)
    override_protein = Column(Float, nullable=True)
    override_carbs = Column(Float, nullable=True)
    override_fat = Column(Float, nullable=True)
    
    # Status
    is_optional = Column(Boolean, default=False)  # Optional meal/snack
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="meal_plan_recipes")
    recipe = relationship("Recipe", back_populates="meal_plan_recipes")
    
    def __repr__(self):
        return f"<MealPlanRecipe(id={self.id}, meal_plan_id={self.meal_plan_id}, recipe_id={self.recipe_id}, day={self.day_number}, meal_type='{self.meal_type}')>"
