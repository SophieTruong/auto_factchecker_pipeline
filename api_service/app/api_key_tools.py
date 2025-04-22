import argparse
import sys
from utils.password_hashing import hash_password
from database import crud, postgres
from sqlalchemy.orm import Session


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Manage API keys in the database.")
    parser.add_argument(
        "command",
        choices=["ADD", "DELETE"],
        help="The command to execute: ADD to add a new API key, DELETE to remove an API key.",
    )
    parser.add_argument(
        "key",
        type=str,
        help="The key for the command: a raw API key string or ALL (if ALL keys are to be deleted).",
    )

    args = parser.parse_args()

    # Initialize database session
    db: Session = next(postgres.get_db())

    try:
        if args.command == "ADD":
            if args.key == "ALL":
                print("Cannot use ALL as key, restricted")
                sys.exit(-1)
            new_api_key = crud.add_api_key(db, args.key)
            print(f"API key added successfully: {new_api_key.hashed_api_key}")
        elif args.command == "DELETE":
            if args.key == "ALL":
                crud.reset_api_keys(db)
                print("All keys removed")
                sys.exit(0)
            else:
                crud.remove_api_key(db, hash_password(args.key))
                print("API key deleted successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
