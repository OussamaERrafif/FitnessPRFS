from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from app.models.meal_plan import MealPlan, MealPlanRecipe, MealType, DietType
from app.models.recipe import Recipe
from app.models.client import Client
from app.schemas.meal_plan import (
    MealPlanCreate,
    MealPlanUpdate,
    MealPlanResponse,
    MealPlanRecipeCreate,
    MealPlanRecipeUpdate,
    MealPlanFilter,
    NutritionalSummary,
    WeeklyMealPlan
)


class MealPlanService:
    """Service for meal plan management."""
    
    @staticmethod
    def create_meal_plan(db: Session, meal_plan_data: MealPlanCreate) -> MealPlan:
        """Create a new meal plan."""
        # Validate client exists if client_id provided
        if meal_plan_data.client_id:
            client = db.query(Client).filter(Client.id == meal_plan_data.client_id).first()
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client not found"
                )
        
        meal_plan_dict = meal_plan_data.model_dump()
        
        # Convert lists to JSON strings if needed
        if meal_plan_dict.get('dietary_restrictions'):
            meal_plan_dict['dietary_restrictions'] = str(meal_plan_dict['dietary_restrictions'])
        
        meal_plan = MealPlan(**meal_plan_dict)
        
        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)
        return meal_plan
    
    @staticmethod
    def get_meal_plan_by_id(db: Session, meal_plan_id: int) -> Optional[MealPlan]:
        """Get meal plan by ID."""
        return db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    
    @staticmethod
    def get_meal_plans(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[MealPlanFilter] = None
    ) -> List[MealPlan]:
        """Get meal plans with optional filtering."""
        query = db.query(MealPlan).filter(MealPlan.is_active == True)
        
        if filters:
            if filters.client_id:
                query = query.filter(MealPlan.client_id == filters.client_id)
            
            if filters.diet_type:
                query = query.filter(MealPlan.diet_type == filters.diet_type)
            
            if filters.start_date:
                query = query.filter(MealPlan.start_date >= filters.start_date)
            
            if filters.end_date:
                query = query.filter(MealPlan.end_date <= filters.end_date)
            
            if filters.target_calories_min:
                query = query.filter(MealPlan.target_calories >= filters.target_calories_min)
            
            if filters.target_calories_max:
                query = query.filter(MealPlan.target_calories <= filters.target_calories_max)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        MealPlan.name.ilike(search_term),
                        MealPlan.description.ilike(search_term)
                    )
                )
        
        return query.order_by(MealPlan.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_meal_plan(
        db: Session,
        meal_plan_id: int,
        meal_plan_data: MealPlanUpdate
    ) -> Optional[MealPlan]:
        """Update a meal plan."""
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            return None
        
        update_dict = meal_plan_data.model_dump(exclude_unset=True)
        
        # Convert lists to JSON strings if needed
        if 'dietary_restrictions' in update_dict and update_dict['dietary_restrictions']:
            update_dict['dietary_restrictions'] = str(update_dict['dietary_restrictions'])
        
        for field, value in update_dict.items():
            setattr(meal_plan, field, value)
        
        meal_plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(meal_plan)
        return meal_plan
    
    @staticmethod
    def delete_meal_plan(db: Session, meal_plan_id: int) -> bool:
        """Soft delete a meal plan."""
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            return False
        
        meal_plan.is_active = False
        meal_plan.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def add_recipe_to_meal_plan(
        db: Session,
        meal_plan_id: int,
        recipe_data: MealPlanRecipeCreate
    ) -> Optional[MealPlanRecipe]:
        """Add a recipe to a meal plan."""
        # Validate meal plan exists
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            return None
        
        # Validate recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_data.recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )
        
        meal_plan_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan_id,
            **recipe_data.model_dump()
        )
        
        db.add(meal_plan_recipe)
        db.commit()
        db.refresh(meal_plan_recipe)
        return meal_plan_recipe
    
    @staticmethod
    def update_meal_plan_recipe(
        db: Session,
        meal_plan_recipe_id: int,
        recipe_data: MealPlanRecipeUpdate
    ) -> Optional[MealPlanRecipe]:
        """Update a meal plan recipe."""
        meal_plan_recipe = db.query(MealPlanRecipe).filter(
            MealPlanRecipe.id == meal_plan_recipe_id
        ).first()
        
        if not meal_plan_recipe:
            return None
        
        update_dict = recipe_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(meal_plan_recipe, field, value)
        
        db.commit()
        db.refresh(meal_plan_recipe)
        return meal_plan_recipe
    
    @staticmethod
    def remove_recipe_from_meal_plan(db: Session, meal_plan_recipe_id: int) -> bool:
        """Remove a recipe from a meal plan."""
        meal_plan_recipe = db.query(MealPlanRecipe).filter(
            MealPlanRecipe.id == meal_plan_recipe_id
        ).first()
        
        if not meal_plan_recipe:
            return False
        
        db.delete(meal_plan_recipe)
        db.commit()
        return True
    
    @staticmethod
    def get_meal_plan_recipes(db: Session, meal_plan_id: int) -> List[MealPlanRecipe]:
        """Get all recipes in a meal plan."""
        return db.query(MealPlanRecipe).filter(
            MealPlanRecipe.meal_plan_id == meal_plan_id
        ).order_by(MealPlanRecipe.day_number, MealPlanRecipe.meal_type).all()
    
    @staticmethod
    def get_daily_meal_plan(
        db: Session,
        meal_plan_id: int,
        day_number: int
    ) -> List[MealPlanRecipe]:
        """Get meal plan for a specific day."""
        return db.query(MealPlanRecipe).filter(
            and_(
                MealPlanRecipe.meal_plan_id == meal_plan_id,
                MealPlanRecipe.day_number == day_number
            )
        ).order_by(MealPlanRecipe.meal_type).all()
    
    @staticmethod
    def get_meal_plan_by_meal_type(
        db: Session,
        meal_plan_id: int,
        meal_type: MealType
    ) -> List[MealPlanRecipe]:
        """Get all meals of a specific type from a meal plan."""
        return db.query(MealPlanRecipe).filter(
            and_(
                MealPlanRecipe.meal_plan_id == meal_plan_id,
                MealPlanRecipe.meal_type == meal_type
            )
        ).order_by(MealPlanRecipe.day_number).all()
    
    @staticmethod
    def calculate_nutritional_summary(
        db: Session,
        meal_plan_id: int
    ) -> NutritionalSummary:
        """Calculate nutritional summary for a meal plan."""
        meal_plan_recipes = MealPlanService.get_meal_plan_recipes(db, meal_plan_id)
        
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_fiber = 0.0
        
        for mp_recipe in meal_plan_recipes:
            recipe = db.query(Recipe).filter(Recipe.id == mp_recipe.recipe_id).first()
            if recipe:
                # Scale nutrition based on serving size
                serving_multiplier = mp_recipe.serving_size / (recipe.servings or 1)
                
                total_calories += (recipe.calories_per_serving or 0) * serving_multiplier
                total_protein += (recipe.protein_grams or 0) * serving_multiplier
                total_carbs += (recipe.carbs_grams or 0) * serving_multiplier
                total_fat += (recipe.fat_grams or 0) * serving_multiplier
                total_fiber += (recipe.fiber_grams or 0) * serving_multiplier
        
        # Get meal plan duration
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        duration_days = 7  # Default to 7 days if not specified
        if meal_plan and meal_plan.start_date and meal_plan.end_date:
            duration_days = (meal_plan.end_date - meal_plan.start_date).days + 1
        
        return NutritionalSummary(
            total_calories=total_calories,
            calories_per_day=total_calories / duration_days if duration_days > 0 else 0,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            total_fiber=total_fiber,
            protein_percentage=(total_protein * 4 / total_calories * 100) if total_calories > 0 else 0,
            carbs_percentage=(total_carbs * 4 / total_calories * 100) if total_calories > 0 else 0,
            fat_percentage=(total_fat * 9 / total_calories * 100) if total_calories > 0 else 0
        )
    
    @staticmethod
    def get_client_active_meal_plans(db: Session, client_id: int) -> List[MealPlan]:
        """Get active meal plans for a client."""
        today = datetime.utcnow().date()
        
        return db.query(MealPlan).filter(
            and_(
                MealPlan.client_id == client_id,
                MealPlan.is_active == True,
                or_(
                    MealPlan.end_date.is_(None),
                    MealPlan.end_date >= today
                ),
                MealPlan.start_date <= today
            )
        ).order_by(MealPlan.start_date.desc()).all()
    
    @staticmethod
    def generate_weekly_meal_plan(
        db: Session,
        meal_plan_id: int
    ) -> Optional[WeeklyMealPlan]:
        """Generate a weekly meal plan structure."""
        meal_plan = MealPlanService.get_meal_plan_by_id(db, meal_plan_id)
        if not meal_plan:
            return None
        
        weekly_plan = WeeklyMealPlan(
            meal_plan_id=meal_plan_id,
            week_start_date=meal_plan.start_date or datetime.utcnow().date(),
            daily_meals={}
        )
        
        # Get all recipes for the meal plan
        meal_plan_recipes = MealPlanService.get_meal_plan_recipes(db, meal_plan_id)
        
        # Organize by day
        for day in range(1, 8):  # 7 days
            day_meals = {
                "breakfast": [],
                "lunch": [],
                "dinner": [],
                "snack": []
            }
            
            day_recipes = [r for r in meal_plan_recipes if r.day_number == day]
            
            for recipe_item in day_recipes:
                recipe = db.query(Recipe).filter(Recipe.id == recipe_item.recipe_id).first()
                if recipe:
                    meal_info = {
                        "recipe_id": recipe.id,
                        "recipe_name": recipe.name,
                        "serving_size": recipe_item.serving_size,
                        "calories": (recipe.calories_per_serving or 0) * (recipe_item.serving_size / (recipe.servings or 1)),
                        "prep_time": recipe.prep_time_minutes,
                        "notes": recipe_item.notes
                    }
                    
                    if recipe_item.meal_type == MealType.BREAKFAST:
                        day_meals["breakfast"].append(meal_info)
                    elif recipe_item.meal_type == MealType.LUNCH:
                        day_meals["lunch"].append(meal_info)
                    elif recipe_item.meal_type == MealType.DINNER:
                        day_meals["dinner"].append(meal_info)
                    elif recipe_item.meal_type == MealType.SNACK:
                        day_meals["snack"].append(meal_info)
            
            weekly_plan.daily_meals[f"day_{day}"] = day_meals
        
        return weekly_plan
    
    @staticmethod
    def duplicate_meal_plan(
        db: Session,
        meal_plan_id: int,
        new_name: str,
        client_id: Optional[int] = None
    ) -> Optional[MealPlan]:
        """Duplicate an existing meal plan."""
        original_meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not original_meal_plan:
            return None
        
        # Create new meal plan
        new_meal_plan_data = {
            "name": new_name,
            "description": f"Copy of {original_meal_plan.name}",
            "client_id": client_id or original_meal_plan.client_id,
            "diet_type": original_meal_plan.diet_type,
            "target_calories": original_meal_plan.target_calories,
            "start_date": datetime.utcnow().date(),
            "end_date": datetime.utcnow().date() + timedelta(days=7),
            "dietary_restrictions": original_meal_plan.dietary_restrictions
        }
        
        new_meal_plan = MealPlan(**new_meal_plan_data)
        db.add(new_meal_plan)
        db.commit()
        db.refresh(new_meal_plan)
        
        # Copy all recipes
        original_recipes = MealPlanService.get_meal_plan_recipes(db, meal_plan_id)
        for orig_recipe in original_recipes:
            new_recipe = MealPlanRecipe(
                meal_plan_id=new_meal_plan.id,
                recipe_id=orig_recipe.recipe_id,
                day_number=orig_recipe.day_number,
                meal_type=orig_recipe.meal_type,
                serving_size=orig_recipe.serving_size,
                notes=orig_recipe.notes
            )
            db.add(new_recipe)
        
        db.commit()
        return new_meal_plan
    
    @staticmethod
    def search_meal_plans(db: Session, search_term: str, limit: int = 20) -> List[MealPlan]:
        """Search meal plans by name or description."""
        search_pattern = f"%{search_term}%"
        return db.query(MealPlan).filter(
            and_(
                MealPlan.is_active == True,
                or_(
                    MealPlan.name.ilike(search_pattern),
                    MealPlan.description.ilike(search_pattern)
                )
            )
        ).limit(limit).all()


# Global meal plan service instance
meal_plan_service = MealPlanService()
