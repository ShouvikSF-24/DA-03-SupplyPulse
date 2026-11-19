from src.database import engine, test_connection


def main():
    print("=" * 60)
    print("SUPPLYPULSE - PYTHON DATABASE CONNECTION TEST")
    print("=" * 60)

    try:
        result = test_connection()

        print("\nConnection successful!")
        print(f"Database: {result[0]}")
        print(f"User: {result[1]}")
        print(f"Version: {result[2]}")

    except Exception as error:
        print("\nDatabase connection failed!")
        print(f"Error: {error}")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()