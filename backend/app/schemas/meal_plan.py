from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RecipeBase(BaseModel):
    """Base recipe model."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    ingredients: List[Dict[str, Any]] = Field(..., description="List of ingredients with quantities")
    instructions: List[str] = Field(..., description="Step-by-step instructions")
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: int = Field(1, ge=1)
    difficulty_level: Optional[str] = None
    tags: Optional[List[str]] = Field(None, description="Recipe tags (keto, vegan, etc.)")
    nutrition_facts: Optional[Dict[str, Any]] = Field(None, description="Nutrition information")
    is_public: bool = Field(False, description="Whether recipe is public")


class RecipeCreate(RecipeBase):
    """Recipe creation model."""
    created_by_trainer_id: int = Field(..., description="Trainer who created the recipe")


class RecipeUpdate(BaseModel):
    """Recipe update model."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    instructions: Optional[List[str]] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = None
    tags: Optional[List[str]] = None
    nutrition_facts: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class RecipeResponse(RecipeBase):
    """Recipe response model."""
    id: int
    created_by_trainer_id: int
    image_url: Optional[str]
    video_url: Optional[str]
    total_time_minutes: Optional[int]
    calories_per_serving: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Creator info
    creator_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MealPlanBase(BaseModel):
    """Base meal plan model."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    plan_type: str = Field(..., description="Meal plan type")
    duration_days: int = Field(..., ge=1, description="Plan duration in days")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    allergens_to_avoid: Optional[List[str]] = Field(None, description="Allergens to avoid")
    target_calories: Optional[float] = Field(None, ge=0)
    target_protein_grams: Optional[float] = Field(None, ge=0)
    target_carbs_grams: Optional[float] = Field(None, ge=0)
    target_fat_grams: Optional[float] = Field(None, ge=0)
    target_fiber_grams: Optional[float] = Field(None, ge=0)
    meals_per_day: int = Field(3, ge=1, le=10)
    snacks_per_day: int = Field(2, ge=0, le=10)
    preferences: Optional[List[str]] = Field(None, description="Food preferences")
    dislikes: Optional[List[str]] = Field(None, description="Foods to avoid")
    notes: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)


class MealPlanCreate(MealPlanBase):
    """Meal plan creation model."""
    client_id: int = Field(..., description="Client ID")
    weekly_meal_plan: Optional[Dict[str, Any]] = Field(None, description="Weekly meal structure")
    recipes: Optional[List[int]] = Field(None, description="List of recipe IDs")


class MealPlanUpdate(BaseModel):
    """Meal plan update model."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1)
    dietary_restrictions: Optional[List[str]] = None
    allergens_to_avoid: Optional[List[str]] = None
    target_calories: Optional[float] = Field(None, ge=0)
    target_protein_grams: Optional[float] = Field(None, ge=0)
    target_carbs_grams: Optional[float] = Field(None, ge=0)
    target_fat_grams: Optional[float] = Field(None, ge=0)
    target_fiber_grams: Optional[float] = Field(None, ge=0)
    meals_per_day: Optional[int] = Field(None, ge=1, le=10)
    snacks_per_day: Optional[int] = Field(None, ge=0, le=10)
    weekly_meal_plan: Optional[Dict[str, Any]] = None
    recipes: Optional[List[int]] = None
    preferences: Optional[List[str]] = None
    dislikes: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    adherence_percentage: Optional[float] = Field(None, ge=0, le=100)


class MealPlanResponse(MealPlanBase):
    """Meal plan response model."""
    id: int
    client_id: int
    created_by_trainer_id: Optional[int]
    weekly_meal_plan: Optional[Dict[str, Any]]
    recipes: Optional[List[int]]
    shopping_list: Optional[List[str]]
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    adherence_percentage: float
    is_template: bool
    created_from_template_id: Optional[int]
    is_paid: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    client_name: Optional[str] = None
    trainer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DailyMealPlan(BaseModel):
    """Daily meal plan structure."""
    date: datetime
    meals: List[Dict[str, Any]]  # breakfast, lunch, dinner, snacks
    total_calories: Optional[float]
    total_protein: Optional[float]
    total_carbs: Optional[float]
    total_fat: Optional[float]
    total_fiber: Optional[float]
    shopping_items: Optional[List[str]]


class MealPlanTemplate(BaseModel):
    """Meal plan template model."""
    id: int
    name: str
    description: Optional[str]
    plan_type: str
    duration_days: int
    weekly_meal_plan: Optional[Dict[str, Any]]
    recipes: Optional[List[int]]
    created_by_trainer_id: int
    
    model_config = ConfigDict(from_attributes=True)


class NutritionTracker(BaseModel):
    """Nutrition tracking model."""
    client_id: int
    date: datetime
    meals_logged: List[Dict[str, Any]]
    total_calories_consumed: Optional[float]
    total_protein_consumed: Optional[float]
    total_carbs_consumed: Optional[float]
    total_fat_consumed: Optional[float]
    adherence_to_plan: Optional[float]  # percentage
    notes: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class PublicRecipe(BaseModel):
    """Public recipe for sharing."""
    id: int
    name: str
    description: Optional[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    servings: int
    difficulty_level: Optional[str]
    tags: Optional[List[str]]
    image_url: Optional[str]
    calories_per_serving: Optional[float]
    creator_name: str
    
    model_config = ConfigDict(from_attributes=True)


class ShoppingList(BaseModel):
    """Shopping list model."""
    meal_plan_id: int
    client_id: int
    week_start_date: datetime
    items: List[Dict[str, Any]]  # ingredient, quantity, unit, category
    total_estimated_cost: Optional[float]
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MealPlanFilter(BaseModel):
    """Meal plan filter model."""
    client_id: Optional[int] = None
    diet_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_calories_min: Optional[int] = None
    target_calories_max: Optional[int] = None
    search: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MealPlanRecipeBase(BaseModel):
    """Base meal plan recipe model."""
    recipe_id: int = Field(..., description="Recipe ID")
    day_number: int = Field(..., ge=1, description="Day number in the meal plan")
    meal_type: str = Field(..., description="Type of meal (breakfast, lunch, etc.)")
    meal_order: int = Field(1, ge=1, description="Order within the same meal type")
    servings: float = Field(1.0, gt=0, description="Number of servings")
    portion_size: Optional[str] = Field(None, description="Portion size description")
    preparation_notes: Optional[str] = None
    substitutions: Optional[str] = None
    is_optional: bool = Field(False, description="Whether this meal is optional")


class MealPlanRecipeCreate(MealPlanRecipeBase):
    """Meal plan recipe creation model."""
    meal_plan_id: int = Field(..., description="Meal plan ID")


class MealPlanRecipeUpdate(BaseModel):
    """Meal plan recipe update model."""
    recipe_id: Optional[int] = None
    day_number: Optional[int] = Field(None, ge=1)
    meal_type: Optional[str] = None
    meal_order: Optional[int] = Field(None, ge=1)
    servings: Optional[float] = Field(None, gt=0)
    portion_size: Optional[str] = None
    preparation_notes: Optional[str] = None
    substitutions: Optional[str] = None
    is_optional: Optional[bool] = None
    is_active: Optional[bool] = None
    override_calories: Optional[float] = Field(None, ge=0)
    override_protein: Optional[float] = Field(None, ge=0)
    override_carbs: Optional[float] = Field(None, ge=0)
    override_fat: Optional[float] = Field(None, ge=0)


class MealPlanRecipeResponse(MealPlanRecipeBase):
    """Meal plan recipe response model."""
    id: int
    meal_plan_id: int
    override_calories: Optional[float]
    override_protein: Optional[float]
    override_carbs: Optional[float]
    override_fat: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Recipe details
    recipe_name: Optional[str] = None
    recipe_calories: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class NutritionalSummary(BaseModel):
    """Nutritional summary model."""
    total_calories: float = Field(0.0, ge=0)
    total_protein: float = Field(0.0, ge=0)
    total_carbs: float = Field(0.0, ge=0)
    total_fat: float = Field(0.0, ge=0)
    total_fiber: float = Field(0.0, ge=0)
    protein_percentage: float = Field(0.0, ge=0, le=100)
    carbs_percentage: float = Field(0.0, ge=0, le=100)
    fat_percentage: float = Field(0.0, ge=0, le=100)
    
    model_config = ConfigDict(from_attributes=True)


class WeeklyMealPlan(BaseModel):
    """Weekly meal plan structure model."""
    week_number: int = Field(..., ge=1, description="Week number in the plan")
    start_date: datetime = Field(..., description="Week start date")
    end_date: datetime = Field(..., description="Week end date")
    daily_plans: List[DailyMealPlan] = Field(..., description="Daily meal plans for the week")
    weekly_nutrition: NutritionalSummary = Field(..., description="Weekly nutritional summary")
    shopping_list: Optional[List[Dict[str, Any]]] = Field(None, description="Weekly shopping list")
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
