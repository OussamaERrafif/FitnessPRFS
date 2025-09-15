from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from app.models.program import Program, ProgramExercise, ProgramStatus, ProgramDifficulty
from app.models.client import Client
from app.models.trainer import Trainer
from app.models.exercise import Exercise, DifficultyLevel
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramExerciseCreate,
    ProgramExerciseUpdate,
    ProgramFilter,
    ProgramAssignment
)


class ProgramService:
    """Service for program management and assignment."""
    
    @staticmethod
    def create_program(db: Session, program_data: ProgramCreate, trainer_id: int) -> Program:
        """Create a new fitness program."""
        # Validate trainer exists
        from app.services.trainer_service import trainer_service
        trainer = trainer_service.get_trainer_by_id(db, trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        
        # Validate client exists
        from app.services.client_service import client_service
        client = client_service.get_client_by_id(db, program_data.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        program_dict = program_data.model_dump()
        
        # Add trainer_id to the program
        program_dict['trainer_id'] = trainer_id
        
        # Set start date if not provided
        if 'start_date' not in program_dict or not program_dict['start_date']:
            program_dict['start_date'] = datetime.utcnow()
        
        # Convert lists to JSON strings if needed
        import json
        if 'goals' in program_dict and program_dict['goals'] is not None:
            program_dict['goals'] = json.dumps(program_dict['goals'])
        if 'exercise_list' in program_dict and program_dict['exercise_list'] is not None:
            program_dict['exercise_list'] = json.dumps(program_dict['exercise_list'])
        
        program = Program(**program_dict)
        
        db.add(program)
        db.commit()
        db.refresh(program)
        
        # Send program assignment notification
        if program.client_id:
            try:
                from app.services.notification_service import notification_service
                notification_service.send_program_assigned_notification(
                    db, program.client.user_id, program.name
                )
            except Exception as e:
                # Log error but don't fail program creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send program assignment notification: {str(e)}")
        
        # Refresh program from database to get fresh state
        db.refresh(program)
        
        # Convert JSON strings back to lists for response
        program = ProgramService._convert_json_fields_to_lists(program)
        
        return program
    
    @staticmethod
    def get_program_by_id(db: Session, program_id: int) -> Optional[Program]:
        """Get program by ID."""
        return db.query(Program).filter(Program.id == program_id).first()
    
    @staticmethod
    def get_programs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[ProgramFilter] = None
    ) -> List[Program]:
        """Get programs with optional filtering."""
        query = db.query(Program).filter(Program.is_active == True)
        
        if filters:
            if filters.status:
                query = query.filter(Program.status == filters.status)
            
            if filters.difficulty_level:
                query = query.filter(Program.difficulty_level == filters.difficulty_level)
            
            if filters.trainer_id:
                query = query.filter(Program.trainer_id == filters.trainer_id)
            
            if filters.duration_weeks_min:
                query = query.filter(Program.duration_weeks >= filters.duration_weeks_min)
            
            if filters.duration_weeks_max:
                query = query.filter(Program.duration_weeks <= filters.duration_weeks_max)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Program.name.ilike(search_term),
                        Program.description.ilike(search_term)
                    )
                )
        
        return query.order_by(Program.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_program(db: Session, program_id: int, program_data: ProgramUpdate) -> Optional[Program]:
        """Update a program."""
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return None
        
        update_dict = program_data.model_dump(exclude_unset=True)
        
        # Convert lists to JSON strings if needed
        if 'goals' in update_dict and update_dict['goals']:
            update_dict['goals'] = str(update_dict['goals'])
        if 'equipment_required' in update_dict and update_dict['equipment_required']:
            update_dict['equipment_required'] = str(update_dict['equipment_required'])
        
        for field, value in update_dict.items():
            setattr(program, field, value)
        
        program.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(program)
        return program
    
    @staticmethod
    def delete_program(db: Session, program_id: int) -> bool:
        """Soft delete a program."""
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return False
        
        program.is_active = False
        program.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def add_exercise_to_program(
        db: Session,
        program_id: int,
        exercise_data: ProgramExerciseCreate
    ) -> Optional[ProgramExercise]:
        """Add an exercise to a program."""
        # Validate program exists
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return None
        
        # Validate exercise exists
        exercise = db.query(Exercise).filter(Exercise.id == exercise_data.exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        
        program_exercise = ProgramExercise(
            program_id=program_id,
            **exercise_data.model_dump()
        )
        
        db.add(program_exercise)
        db.commit()
        db.refresh(program_exercise)
        return program_exercise
    
    @staticmethod
    def update_program_exercise(
        db: Session,
        program_exercise_id: int,
        exercise_data: ProgramExerciseUpdate
    ) -> Optional[ProgramExercise]:
        """Update a program exercise."""
        program_exercise = db.query(ProgramExercise).filter(
            ProgramExercise.id == program_exercise_id
        ).first()
        
        if not program_exercise:
            return None
        
        update_dict = exercise_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(program_exercise, field, value)
        
        db.commit()
        db.refresh(program_exercise)
        return program_exercise
    
    @staticmethod
    def remove_exercise_from_program(db: Session, program_exercise_id: int) -> bool:
        """Remove an exercise from a program."""
        program_exercise = db.query(ProgramExercise).filter(
            ProgramExercise.id == program_exercise_id
        ).first()
        
        if not program_exercise:
            return False
        
        db.delete(program_exercise)
        db.commit()
        return True
    
    @staticmethod
    def get_program_exercises(db: Session, program_id: int) -> List[ProgramExercise]:
        """Get all exercises in a program."""
        return db.query(ProgramExercise).filter(
            ProgramExercise.program_id == program_id
        ).order_by(ProgramExercise.week_number, ProgramExercise.day_number, ProgramExercise.order_in_workout).all()
    
    @staticmethod
    def assign_program_to_client(
        db: Session,
        program_id: int,
        client_id: int,
        assignment_data: Optional[ProgramAssignment] = None
    ) -> Optional[Dict[str, Any]]:
        """Assign a program to a client."""
        # Validate program and client exist
        program = db.query(Program).filter(Program.id == program_id).first()
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not program or not client:
            return None
        
        # Check if client already has this program assigned
        # In a real implementation, you'd have a client_programs table
        # For now, we'll return assignment info
        
        start_date = assignment_data.start_date if assignment_data else datetime.utcnow().date()
        end_date = start_date + timedelta(weeks=program.duration_weeks)
        
        # In a real implementation, you'd create a ClientProgram record
        # For now, we'll return the assignment details
        
        return {
            "program_id": program_id,
            "client_id": client_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "assigned",
            "progress_percentage": 0.0,
            "assigned_at": datetime.utcnow()
        }
    
    @staticmethod
    def get_client_programs(db: Session, client_id: int) -> List[Dict[str, Any]]:
        """Get all programs assigned to a client."""
        # In a real implementation, you'd query a client_programs table
        # For now, return empty list as placeholder
        return []
    
    @staticmethod
    def get_trainer_programs(db: Session, trainer_id: int) -> List[Program]:
        """Get all programs created by a trainer."""
        return db.query(Program).filter(
            Program.trainer_id == trainer_id,
            Program.is_active == True
        ).order_by(Program.created_at.desc()).all()
    
    @staticmethod
    def get_program_by_week_day(
        db: Session,
        program_id: int,
        week_number: int,
        day_number: int
    ) -> List[ProgramExercise]:
        """Get exercises for a specific week and day of a program."""
        return db.query(ProgramExercise).filter(
            and_(
                ProgramExercise.program_id == program_id,
                ProgramExercise.week_number == week_number,
                ProgramExercise.day_number == day_number
            )
        ).order_by(ProgramExercise.order_in_workout).all()
    
    @staticmethod
    def duplicate_program(
        db: Session,
        program_id: int,
        new_name: str,
        trainer_id: Optional[int] = None
    ) -> Optional[Program]:
        """Duplicate an existing program."""
        original_program = db.query(Program).filter(Program.id == program_id).first()
        if not original_program:
            return None
        
        # Create new program with modified details
        new_program_data = {
            "name": new_name,
            "description": f"Copy of {original_program.name}",
            "difficulty_level": original_program.difficulty_level,
            "duration_weeks": original_program.duration_weeks,
            "sessions_per_week": original_program.sessions_per_week,
            "goals": original_program.goals,
            "equipment_required": original_program.equipment_required,
            "trainer_id": trainer_id or original_program.trainer_id
        }
        
        new_program = Program(**new_program_data)
        db.add(new_program)
        db.commit()
        db.refresh(new_program)
        
        # Copy all exercises
        original_exercises = ProgramService.get_program_exercises(db, program_id)
        for orig_exercise in original_exercises:
            new_exercise = ProgramExercise(
                program_id=new_program.id,
                exercise_id=orig_exercise.exercise_id,
                week_number=orig_exercise.week_number,
                day_number=orig_exercise.day_number,
                order_in_workout=orig_exercise.order_in_workout,
                target_sets=orig_exercise.target_sets,
                target_reps=orig_exercise.target_reps,
                target_weight=orig_exercise.target_weight,
                target_duration_minutes=orig_exercise.target_duration_minutes,
                rest_seconds=orig_exercise.rest_seconds,
                notes=orig_exercise.notes
            )
            db.add(new_exercise)
        
        db.commit()
        return new_program
    
    @staticmethod
    def get_popular_programs(db: Session, limit: int = 10) -> List[Program]:
        """Get popular programs (mock implementation)."""
        # In a real implementation, you'd track usage statistics
        return db.query(Program).filter(
            Program.is_active == True,
            Program.status == ProgramStatus.ACTIVE.value
        ).order_by(Program.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def search_programs(db: Session, search_term: str, limit: int = 20) -> List[Program]:
        """Search programs by name or description."""
        search_pattern = f"%{search_term}%"
        return db.query(Program).filter(
            and_(
                Program.is_active == True,
                or_(
                    Program.name.ilike(search_pattern),
                    Program.description.ilike(search_pattern)
                )
            )
        ).limit(limit).all()
    
    @staticmethod
    @staticmethod
    def _convert_json_fields_to_lists(program: Program) -> Program:
        """Convert JSON string fields back to lists for API response."""
        import json
        
        # Convert goals from JSON string to list
        if program.goals is not None:
            try:
                if isinstance(program.goals, str):
                    program.goals = json.loads(program.goals)
            except (json.JSONDecodeError, TypeError):
                program.goals = []
        
        # Convert exercise_list from JSON string to list
        if program.exercise_list is not None:
            try:
                if isinstance(program.exercise_list, str):
                    program.exercise_list = json.loads(program.exercise_list)
            except (json.JSONDecodeError, TypeError):
                program.exercise_list = []
        
        return program


# Global program service instance
program_service = ProgramService()
