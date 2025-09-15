from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from app.models.progress_log import ProgressLog, LogType, ProgressType
from app.models.exercise import Exercise
from app.schemas.progress_log import (
    ProgressLogCreate,
    ProgressLogUpdate,
    ProgressLogResponse,
    ProgressLogFilter,
    ProgressStats,
    WorkoutSummary
)


class ProgressLogService:
    """Service for progress logging and tracking."""
    
    @staticmethod
    def create_progress_log(db: Session, log_data: ProgressLogCreate, trainer_id: Optional[int] = None) -> ProgressLog:
        """Create a new progress log entry."""
        # Validate user exists
        from app.models.user import User
        user = db.query(User).filter(User.id == log_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate exercise exists if exercise_id provided
        if log_data.exercise_id:
            exercise = db.query(Exercise).filter(Exercise.id == log_data.exercise_id).first()
            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exercise not found"
                )
        
        log_dict = log_data.model_dump()
        
        # Convert lists/dicts to JSON strings if needed
        if log_dict.get('exercise_data'):
            log_dict['exercise_data'] = str(log_dict['exercise_data'])
        if log_dict.get('notes'):
            log_dict['notes'] = log_dict['notes']
        
        progress_log = ProgressLog(**log_dict)
        
        db.add(progress_log)
        db.commit()
        db.refresh(progress_log)
        return progress_log
    
    @staticmethod
    def get_progress_log_by_id(db: Session, progress_log_id: int) -> Optional[ProgressLog]:
        """Get progress log by ID."""
        progress_log = db.query(ProgressLog).filter(ProgressLog.id == progress_log_id).first()
        if not progress_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress log not found"
            )
        return progress_log
    
    @staticmethod
    def get_client_progress_logs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[ProgressLogFilter] = None
    ) -> List[ProgressLog]:
        """Get progress logs for a specific user with optional filtering."""
        query = db.query(ProgressLog).filter(ProgressLog.user_id == user_id)
        
        if filters:
            if filters.log_type:
                query = query.filter(ProgressLog.log_type == filters.log_type)
            
            if filters.exercise_id:
                query = query.filter(ProgressLog.exercise_id == filters.exercise_id)
            
            if filters.start_date:
                query = query.filter(ProgressLog.workout_date >= filters.start_date)

            if filters.end_date:
                query = query.filter(ProgressLog.workout_date <= filters.end_date)

        return query.order_by(desc(ProgressLog.workout_date)).offset(skip).limit(limit).all()

    @staticmethod
    def update_progress_log(
        db: Session, 
        progress_log_id: int, 
        progress_update: ProgressLogUpdate,
        trainer_id: Optional[int] = None
    ) -> Optional[ProgressLog]:
        """Update a progress log entry."""
        progress_log = db.query(ProgressLog).filter(ProgressLog.id == progress_log_id).first()
        if not progress_log:
            return None
        
        # Check authorization if trainer_id is provided
        if trainer_id and hasattr(progress_log, 'trainer_id') and progress_log.trainer_id != trainer_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this progress log")
        
        update_dict = progress_update.model_dump(exclude_unset=True)
        
        # Convert lists/dicts to JSON strings if needed
        if 'exercise_data' in update_dict and update_dict['exercise_data']:
            update_dict['exercise_data'] = str(update_dict['exercise_data'])
        
        for field, value in update_dict.items():
            setattr(progress_log, field, value)
        
        progress_log.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(progress_log)
        return progress_log
    
    @staticmethod
    def delete_progress_log(
        db: Session, 
        progress_log_id: int, 
        trainer_id: Optional[int] = None
    ) -> bool:
        """Delete a progress log entry."""
        progress_log = db.query(ProgressLog).filter(ProgressLog.id == progress_log_id).first()
        if not progress_log:
            return False
        
        # Check authorization if trainer_id is provided
        if trainer_id and hasattr(progress_log, 'trainer_id') and progress_log.trainer_id != trainer_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this progress log")
        
        db.delete(progress_log)
        db.commit()
        return True
    
    @staticmethod
    def get_workout_history(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[ProgressLog]:
        """Get workout history for a client."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.created_at >= start_date
            )
        ).order_by(desc(ProgressLog.created_at)).all()
    
    @staticmethod
    def get_body_measurements_history(
        db: Session,
        user_id: int,
        days: int = 90
    ) -> List[ProgressLog]:
        """Get body measurements history for a client."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "measurement",
                ProgressLog.created_at >= start_date
            )
        ).order_by(ProgressLog.created_at).all()
    
    @staticmethod
    def get_weight_progress(
        db: Session,
        user_id: int,
        days: int = 90
    ) -> List[ProgressLog]:
        """Get weight progress for a client."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "weight",
                ProgressLog.created_at >= start_date
            )
        ).order_by(ProgressLog.created_at).all()
    
    @staticmethod
    def get_exercise_progress(
        db: Session,
        user_id: int,
        exercise_id: int,
        limit: int = 20
    ) -> List[ProgressLog]:
        """Get progress for a specific exercise."""
        return db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.exercise_id == exercise_id,
                ProgressLog.log_type == "workout"
            )
        ).order_by(desc(ProgressLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_progress_stats(db: Session, user_id: int) -> ProgressStats:
        """Get progress statistics for a client."""
        # Total workouts logged
        total_workouts = db.query(func.count(ProgressLog.id)).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout"
            )
        ).scalar() or 0
        
        # Workouts this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        workouts_this_month = db.query(func.count(ProgressLog.id)).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.created_at >= start_of_month
            )
        ).scalar() or 0
        
        # Current streak (consecutive days with workouts)
        current_streak = ProgressLogService._calculate_current_streak(db, user_id)
        
        # Latest weight
        latest_weight_log = db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "weight"
            )
        ).order_by(desc(ProgressLog.created_at)).first()
        
        current_weight = latest_weight_log.value if latest_weight_log else None
        
        # Weight change (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        old_weight_log = db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "weight",
                ProgressLog.created_at <= thirty_days_ago
            )
        ).order_by(desc(ProgressLog.created_at)).first()
        
        weight_change = 0.0
        if current_weight and old_weight_log:
            weight_change = current_weight - old_weight_log.value
        
        # Most active exercise
        most_active_exercise_query = db.query(
            ProgressLog.exercise_id,
            func.count(ProgressLog.id).label('count')
        ).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.exercise_id.isnot(None)
            )
        ).group_by(ProgressLog.exercise_id).order_by(desc('count')).first()
        
        most_active_exercise_id = None
        if most_active_exercise_query:
            most_active_exercise_id = most_active_exercise_query[0]
        
        # Calculate missing fields to match ProgressStats schema
        
        # Total exercises performed (unique exercises)
        total_exercises = db.query(func.count(func.distinct(ProgressLog.exercise_id))).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.exercise_id.isnot(None)
            )
        ).scalar() or 0
        
        # Total duration in hours
        total_duration_seconds = db.query(func.sum(ProgressLog.duration)).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.duration.isnot(None)
            )
        ).scalar() or 0
        total_duration_hours = total_duration_seconds / 3600.0 if total_duration_seconds else 0.0
        
        # Total calories burned
        total_calories = db.query(func.sum(ProgressLog.calories_burned)).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.calories_burned.isnot(None)
            )
        ).scalar() or 0.0
        
        # Personal records count
        pr_count = db.query(func.count(ProgressLog.id)).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.is_personal_record == True
            )
        ).scalar() or 0
        
        # Average workouts per week (simplified calculation)
        days_since_first_workout = 7  # Default to 1 week if no workouts
        first_workout = db.query(ProgressLog.created_at).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout"
            )
        ).order_by(ProgressLog.created_at).first()
        
        if first_workout:
            days_since_first_workout = max(1, (datetime.utcnow() - first_workout[0]).days)
        
        weeks_since_first = days_since_first_workout / 7.0
        avg_workouts_per_week = total_workouts / weeks_since_first if weeks_since_first > 0 else 0.0
        
        # Most performed exercise name
        most_performed_exercise = None
        if most_active_exercise_id:
            from app.models.exercise import Exercise
            exercise = db.query(Exercise.name).filter(Exercise.id == most_active_exercise_id).first()
            if exercise:
                most_performed_exercise = exercise[0]
        
        return ProgressStats(
            total_workouts=total_workouts,
            total_exercises_performed=total_exercises,
            total_duration_hours=total_duration_hours,
            total_calories_burned=total_calories,
            personal_records_count=pr_count,
            current_streak_days=current_streak,
            average_workouts_per_week=avg_workouts_per_week,
            most_performed_exercise=most_performed_exercise
        )
    
    @staticmethod
    def _calculate_current_streak(db: Session, user_id: int) -> int:
        """Calculate current workout streak in days."""
        # This is a simplified calculation
        # In a real implementation, you'd check consecutive days
        
        # Get recent workouts
        recent_workouts = db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.created_at >= (datetime.utcnow() - timedelta(days=30))
            )
        ).order_by(desc(ProgressLog.created_at)).all()
        
        if not recent_workouts:
            return 0
        
        # Simple streak calculation - count unique days with workouts
        workout_dates = set()
        for workout in recent_workouts:
            workout_dates.add(workout.created_at.date())
        
        # Check for consecutive days from today backwards
        streak = 0
        current_date = datetime.utcnow().date()
        
        while current_date in workout_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    @staticmethod
    def get_workout_summary(
        db: Session,
        user_id: int,
        date: datetime
    ) -> Optional[WorkoutSummary]:
        """Get workout summary for a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        workouts = db.query(ProgressLog).filter(
            and_(
                ProgressLog.user_id == user_id,
                ProgressLog.log_type == "workout",
                ProgressLog.created_at >= start_of_day,
                ProgressLog.created_at < end_of_day
            )
        ).all()
        
        if not workouts:
            return None
        
        # Calculate summary statistics
        total_exercises = len(workouts)
        total_sets = sum(int(w.sets or 0) for w in workouts)
        total_reps = sum(int(w.reps or 0) for w in workouts)
        
        # Estimated duration (sum of individual exercise durations)
        total_duration = 0
        for workout in workouts:
            if workout.exercise_id:
                exercise = db.query(Exercise).filter(Exercise.id == workout.exercise_id).first()
                if exercise:
                    total_duration += exercise.estimated_duration_minutes or 1
        
        return WorkoutSummary(
            date=date.date(),
            total_exercises=total_exercises,
            total_sets=total_sets,
            total_reps=total_reps,
            estimated_duration_minutes=total_duration,
            exercises_completed=[w.exercise_id for w in workouts if w.exercise_id]
        )
    
    @staticmethod
    def log_workout_session(
        db: Session,
        user_id: int,
        exercises_data: List[Dict[str, Any]]
    ) -> List[ProgressLog]:
        """Log multiple exercises as a workout session."""
        logged_exercises = []
        
        for exercise_data in exercises_data:
            log_data = ProgressLogCreate(
                user_id=user_id,
                log_type="workout",
                exercise_id=exercise_data.get('exercise_id'),
                sets=exercise_data.get('sets'),
                reps=exercise_data.get('reps'),
                weight=exercise_data.get('weight'),
                duration=exercise_data.get('duration'),
                distance=exercise_data.get('distance'),
                exercise_data=exercise_data.get('additional_data', {}),
                notes=exercise_data.get('notes')
            )
            
            progress_log = ProgressLogService.create_progress_log(db, log_data)
            logged_exercises.append(progress_log)
        
        return logged_exercises

    @staticmethod
    def get_progress_logs_by_type(
        db: Session,
        user_id: int,
        progress_type: ProgressType
    ) -> List[ProgressLog]:
        """Get progress logs filtered by type."""
        return db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id,
            ProgressLog.workout_type == progress_type.value
        ).order_by(desc(ProgressLog.workout_date)).all()

    @staticmethod
    def get_progress_logs_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[ProgressLog]:
        """Get progress logs within a date range."""
        return db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id,
            ProgressLog.workout_date >= start_date,
            ProgressLog.workout_date <= end_date
        ).order_by(desc(ProgressLog.workout_date)).all()

    @staticmethod
    def get_latest_progress_by_type(
        db: Session,
        user_id: int,
        progress_type: ProgressType
    ) -> Optional[ProgressLog]:
        """Get the latest progress log for a specific type."""
        return db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id,
            ProgressLog.workout_type == progress_type.value
        ).order_by(desc(ProgressLog.workout_date)).first()

    @staticmethod
    def get_progress_summary(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """Get progress summary for a user."""
        from app.models.progress_log import ProgressType
        
        summary = {}
        for progress_type in ProgressType:
            latest = ProgressLogService.get_latest_progress_by_type(db, user_id, progress_type)
            if latest:
                summary[progress_type.value] = {
                    "value": latest.weight or latest.body_weight or 0,
                    "recorded_date": latest.workout_date.date() if latest.workout_date else None
                }
        return summary

    @staticmethod
    def calculate_progress_trend(
        db: Session,
        user_id: int,
        progress_type: ProgressType
    ) -> Dict[str, Any]:
        """Calculate progress trend for a specific type."""
        logs = ProgressLogService.get_progress_logs_by_type(db, user_id, progress_type)
        if len(logs) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0}
        
        latest = logs[0]
        previous = logs[-1]
        
        latest_value = latest.weight or latest.body_weight or 0
        previous_value = previous.weight or previous.body_weight or 0
        
        if previous_value == 0:
            return {"trend": "no_baseline", "change_percentage": 0}
        
        change_percentage = ((latest_value - previous_value) / previous_value) * 100
        
        if change_percentage > 5:
            trend = "increasing"
        elif change_percentage < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 2),
            "latest_value": latest_value,
            "previous_value": previous_value
        }

    @staticmethod
    def get_progress_statistics(
        db: Session,
        user_id: int,
        progress_type: ProgressType
    ) -> Dict[str, Any]:
        """Get progress statistics for a specific type."""
        logs = ProgressLogService.get_progress_logs_by_type(db, user_id, progress_type)
        
        if not logs:
            return {
                "avg_value": 0,
                "min_value": 0,
                "max_value": 0,
                "count": 0
            }
        
        values = [log.weight or log.body_weight or 0 for log in logs]
        
        return {
            "avg_value": sum(values) / len(values),
            "min_value": min(values),
            "max_value": max(values),
            "count": len(logs)
        }

    @staticmethod
    def bulk_create_progress_logs(
        db: Session,
        progress_logs_data: List[ProgressLogCreate]
    ) -> List[ProgressLog]:
        """Create multiple progress logs in bulk."""
        progress_logs = []
        for log_data in progress_logs_data:
            progress_log = ProgressLog(**log_data.model_dump())
            progress_logs.append(progress_log)
        
        db.add_all(progress_logs)
        db.commit()
        
        for progress_log in progress_logs:
            db.refresh(progress_log)
        
        return progress_logs

    @staticmethod
    def export_progress_data(
        db: Session,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Export progress data for a user."""
        logs = db.query(ProgressLog).filter(
            ProgressLog.user_id == user_id
        ).order_by(desc(ProgressLog.workout_date)).all()
        
        return [
            {
                "date": log.workout_date.isoformat() if log.workout_date else None,
                "exercise_id": log.exercise_id,
                "workout_type": log.workout_type,
                "weight": log.weight,
                "sets": log.sets,
                "reps": log.reps,
                "notes": log.notes
            }
            for log in logs
        ]

    @staticmethod
    def get_progress_goals_comparison(
        db: Session,
        user_id: int,
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare current progress with goals."""
        from app.models.progress_log import ProgressType
        
        comparison = {}
        for goal_type, goal_data in goals.items():
            # Map goal type to ProgressType
            progress_type = None
            if goal_type == "weight":
                progress_type = ProgressType.WEIGHT
            elif goal_type == "body_fat":
                progress_type = ProgressType.BODY_FAT
            
            if progress_type:
                latest = ProgressLogService.get_latest_progress_by_type(db, user_id, progress_type)
                if latest:
                    current_value = latest.weight or latest.body_fat_percentage or 0
                    target_value = goal_data.get("target", 0)
                    
                    if target_value > 0:
                        progress_percentage = (current_value / target_value) * 100
                        comparison[goal_type] = {
                            "current_value": current_value,
                            "target_value": target_value,
                            "progress_percentage": round(progress_percentage, 2),
                            "unit": goal_data.get("unit", "")
                        }
        
        return comparison


# Global progress log service instance
progress_log_service = ProgressLogService()


