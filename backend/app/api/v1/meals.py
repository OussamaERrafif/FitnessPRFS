from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.session import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.services.meal_plan_service import meal_plan_service
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
from app.models.meal_plan import DietType, MealType
from app.models.user import User

router = APIRouter(prefix="/meals", tags=["Meals"])


@router.post("/", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new meal plan (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can create meal plans"
        )
    
    try:
        meal_plan = meal_plan_service.create_meal_plan(db, meal_plan_data)
        return MealPlanResponse.model_validate(meal_plan)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meal plan"
        )


@router.get("/", response_model=List[MealPlanResponse])
async def get_meal_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    diet_type: Optional[DietType] = Query(None),
    target_calories_min: Optional[int] = Query(None, ge=0),
    target_calories_max: Optional[int] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get meal plans with optional filtering."""
    # Apply role-based filtering
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if client:
            client_id = client.id  # Only show client's own meal plans
        else:
            return []  # No client profile found
    # Trainers and admins can see all meal plans
    
    filters = None
    if any([client_id, diet_type, target_calories_min, target_calories_max, search]):
        filters = MealPlanFilter(
            client_id=client_id,
            diet_type=diet_type,
            target_calories_min=target_calories_min,
            target_calories_max=target_calories_max,
            search=search
        )
    
    meal_plans = meal_plan_service.get_meal_plans(db, skip, limit, filters)
    return [MealPlanResponse.model_validate(meal_plan) for meal_plan in meal_plans]


@router.get("/search", response_model=List[MealPlanResponse])
async def search_meal_plans(
    search_term: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search meal plans by name or description."""
    meal_plans = meal_plan_service.search_meal_plans(db, search_term, limit)
    return [MealPlanResponse.model_validate(meal_plan) for meal_plan in meal_plans]


@router.get("/client/{client_id}/active", response_model=List[MealPlanResponse])
async def get_client_active_meal_plans(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get active meal plans for a client."""
    # Check permissions
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or client.id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plans"
            )
    elif current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients, trainers, and admins can view meal plans"
        )
    
    meal_plans = meal_plan_service.get_client_active_meal_plans(db, client_id)
    return [MealPlanResponse.model_validate(meal_plan) for meal_plan in meal_plans]


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get meal plan by ID."""
    meal_plan = meal_plan_service.get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    # Check permissions
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or meal_plan.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plans"
            )
    # Trainers and admins can view all meal plans
    
    return MealPlanResponse.model_validate(meal_plan)


@router.put("/{meal_plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    meal_plan_id: int,
    meal_plan_data: MealPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a meal plan (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can update meal plans"
        )
    
    updated_meal_plan = meal_plan_service.update_meal_plan(db, meal_plan_id, meal_plan_data)
    if not updated_meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return MealPlanResponse.model_validate(updated_meal_plan)


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a meal plan (soft delete - trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can delete meal plans"
        )
    
    success = meal_plan_service.delete_meal_plan(db, meal_plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return None  # 204 No Content should return no body


@router.post("/{meal_plan_id}/recipes")
async def add_recipe_to_meal_plan(
    meal_plan_id: int,
    recipe_data: MealPlanRecipeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a recipe to a meal plan (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can modify meal plans"
        )
    
    try:
        meal_plan_recipe = meal_plan_service.add_recipe_to_meal_plan(db, meal_plan_id, recipe_data)
        if not meal_plan_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        return {"message": "Recipe added to meal plan successfully", "recipe_id": meal_plan_recipe.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add recipe to meal plan"
        )


@router.get("/{meal_plan_id}/recipes")
async def get_meal_plan_recipes(
    meal_plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all recipes in a meal plan."""
    # Check if meal plan exists and user has permission
    meal_plan = meal_plan_service.get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or meal_plan.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plan recipes"
            )
    
    recipes = meal_plan_service.get_meal_plan_recipes(db, meal_plan_id)
    return recipes


@router.get("/{meal_plan_id}/day/{day_number}")
async def get_daily_meal_plan(
    meal_plan_id: int,
    day_number: int = Path(..., ge=1, le=7),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get meal plan for a specific day."""
    # Check permissions (same as get_meal_plan_recipes)
    meal_plan = meal_plan_service.get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or meal_plan.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plans"
            )
    
    daily_meals = meal_plan_service.get_daily_meal_plan(db, meal_plan_id, day_number)
    return daily_meals


@router.get("/{meal_plan_id}/nutrition", response_model=NutritionalSummary)
async def get_meal_plan_nutrition(
    meal_plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get nutritional summary for a meal plan."""
    # Check permissions
    meal_plan = meal_plan_service.get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or meal_plan.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plan nutrition"
            )
    
    nutrition = meal_plan_service.calculate_nutritional_summary(db, meal_plan_id)
    return nutrition


@router.get("/{meal_plan_id}/weekly", response_model=WeeklyMealPlan)
async def get_weekly_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a weekly meal plan structure."""
    # Check permissions
    meal_plan = meal_plan_service.get_meal_plan_by_id(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    if current_user.role.value == "client":
        from app.services.client_service import client_service
        client = client_service.get_client_by_user_id(db, current_user.id)
        if not client or meal_plan.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other client's meal plans"
            )
    
    weekly_plan = meal_plan_service.generate_weekly_meal_plan(db, meal_plan_id)
    if not weekly_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate weekly meal plan"
        )
    
    return weekly_plan


@router.post("/{meal_plan_id}/duplicate")
async def duplicate_meal_plan(
    meal_plan_id: int,
    new_name: str = Query(..., min_length=1, max_length=200),
    client_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate an existing meal plan (trainers and admins only)."""
    if current_user.role.value not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can duplicate meal plans"
        )
    
    try:
        new_meal_plan = meal_plan_service.duplicate_meal_plan(db, meal_plan_id, new_name, client_id)
        if not new_meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original meal plan not found"
            )
        
        return {"message": "Meal plan duplicated successfully", "new_meal_plan_id": new_meal_plan.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate meal plan"
        )
