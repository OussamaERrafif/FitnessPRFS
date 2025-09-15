import os

# Define the full structure: directories and files
structure = {
    "app": {
        "__init__.py": None,
        "main.py": None,
        "config": {
            "dev": {
                "config.py": None,
                "logging.yaml": None,
                "celeryconfig.py": None,
            },
            "prod": {
                "config.py": None,
                "logging.yaml": None,
                "celeryconfig.py": None,
            },
            "test": {
                "config.py": None,
                "logging.yaml": None,
                "celeryconfig.py": None,
            },
            "config.py": None,
            "logging.yaml": None,
            "celeryconfig.py": None,
        },
        "session.py": None,
        "models": {
            "__init__.py": None,
            "user.py": None,
            "client.py": None,
            "trainer.py": None,
            "program.py": None,
            "exercise.py": None,
            "recipe.py": None,
            "meal_plan.py": None,
            "session_booking.py": None,
            "progress_log.py": None,
            "payment.py": None,
            "refresh_token.py": None,
            "attachment.py": None,
        },
        "migrations": {},
        "api": {
            "routes.py": None,
            "deps.py": None,
            "v1": {
                "api.py": None,
                "endpoints": {
                    "auth.py": None,
                    "trainers.py": None,
                    "clients.py": None,
                    "programs.py": None,
                    "meals.py": None,
                    "schedules.py": None,
                    "payments.py": None,
                    "reports.py": None,
                    "ai.py": None,
                    "attachments.py": None,
                },
            },
        },
        "schemas": {
            "user.py": None,
            "client.py": None,
            "trainer.py": None,
            "auth.py": None,
            "program.py": None,
            "exercise.py": None,
            "recipe.py": None,
            "meal_plan.py": None,
            "session_booking.py": None,
            "progress_log.py": None,
            "payment.py": None,
            "attachment.py": None,
            "ai.py": None,
        },
        "services": {
            "auth_service.py": None,
            "ai_client.py": None,
            "pdf_service.py": None,
            "payment_service.py": None,
            "notification_service.py": None,
            "storage_service.py": None,
            "user_service.py": None,
            "client_service.py": None,
            "trainer_service.py": None,
            "program_service.py": None,
            "exercise_service.py": None,
            "recipe_service.py": None,
            "meal_plan_service.py": None,
            "session_booking_service.py": None,
            "progress_log_service.py": None,
            "payment_service.py": None,
            "attachment_service.py": None,
            "ai_service.py": None,
        },
        "tasks": {
            "celery_app.py": None,
            "tasks.py": None,
            "email_tasks.py": None,
            "report_tasks.py": None,
            "payment_tasks.py": None,
            "storage_tasks.py": None,
            "ai_tasks.py": None,
        },
        "utils": {
            "pagination.py": None,
            "csv_helpers.py": None,
            "export_helpers.py": None,
            "validators.py": None,
            "security.py": None,
            "email.py": None,
        },
        "logs": {},
    },
    "scripts": {
        "create_local_db.sh": None,
        "seed_demo_data.py": None,
    },
    "tests": {
        "services": {
            "test_auth_service.py": None,
            "test_ai_client.py": None,
            "test_pdf_service.py": None,
            "test_payment_service.py": None,
            "test_notification_service.py": None,
            "test_storage_service.py": None,
            "test_user_service.py": None,
            "test_client_service.py": None,
            "test_trainer_service.py": None,
            "test_program_service.py": None,
            "test_exercise_service.py": None,
            "test_recipe_service.py": None,
            "test_meal_plan_service.py": None,
            "test_session_booking_service.py": None,
            "test_progress_log_service.py": None,
            "test_payment_service.py": None,
            "test_attachment_service.py": None,
            "test_ai_service.py": None,
        },
        "api": {
            "test_auth.py": None,
            "test_trainers.py": None,
            "test_clients.py": None,
            "test_programs.py": None,
            "test_meals.py": None,
            "test_schedules.py": None,
            "test_payments.py": None,
            "test_reports.py": None,
            "test_ai.py": None,
            "test_attachments.py": None,
        },
        "core": {
            "test_config.py": None,
            "test_security.py": None,
            "test_logging.py": None,
            "test_celery_app.py": None,
            "test_tasks.py": None,
            "test_ai_integration.py": None,
        },
        "utils": {
            "test_pagination.py": None,
            "test_csv_helpers.py": None,
            "test_export_helpers.py": None,
            "test_validators.py": None,
            "test_security.py": None,
            "test_email.py": None,
        },
    },
    "docker": {
        "Dockerfile": None,
        "docker-compose.yml": None,
    },
    ".env.example": None,
    "README.md": None,
    "pyproject.toml": None,  # or requirements.txt
    "LICENSE": None,
}


def create_structure(base_path, tree):
    for name, content in tree.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # It's a folder
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:  # It's a file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write("")  # Create empty file


if __name__ == "__main__":
    create_structure(".", structure)
    print("✅ Project structure created successfully!")
