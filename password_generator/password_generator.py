# ---------------------------------------------------------------------
# Project: Password Generator Tool
# Description: A secure, flexible CLI tool to generate strong random passwords.
# Author: Deepanshu
# Version: 1.1.0
# ---------------------------------------------------------------------

import argparse
import secrets
import string
from typing import List


def log(message: str) -> None:
    """Simple console logger with a consistent prefix."""
    print(f"[PasswordGen] {message}")


def build_char_sets(use_uppercase: bool, use_digits: bool, use_symbols: bool) -> List[str]:
    """
    Return a list of character sets to use based on user preferences.
    Each entry in the list is a string of allowed characters for that category.
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase if use_uppercase else ""
    digits = string.digits if use_digits else ""
    symbols = string.punctuation if use_symbols else ""
    sets = [s for s in (lower, upper, digits, symbols) if s]
    return sets


def generate_password(
    length: int = 12,
    use_uppercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generate a cryptographically secure password.

    Guarantees:
    - At least one character from each selected category is present.
    - Uses the `secrets` module for randomness (secure).
    - Raises ValueError for invalid inputs.

    Args:
        length: total length of the password (must be >= number of selected categories).
        use_uppercase: include uppercase letters if True.
        use_digits: include digits if True.
        use_symbols: include punctuation symbols if True.

    Returns:
        A randomly generated password string.
    """
    if length <= 0:
        raise ValueError("Password length must be a positive integer.")

    char_sets = build_char_sets(use_uppercase, use_digits, use_symbols)

    if not char_sets:
        raise ValueError("No character categories selected. Enable at least one option.")

    # Ensure the password length can include at least one character from each selected set
    if length < len(char_sets):
        raise ValueError(f"Length too short for chosen options. Minimum length = {len(char_sets)}")

    # Start by picking one guaranteed character from each chosen category
    password_chars: List[str] = [secrets.choice(char_set) for char_set in char_sets]

    # Create a pool containing all allowed characters
    all_allowed = "".join(char_sets)

    # Fill the remaining positions randomly from the full pool
    remaining = length - len(password_chars)
    password_chars += [secrets.choice(all_allowed) for _ in range(remaining)]

    # Shuffle to avoid predictable placement of guaranteed characters
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def interactive_mode() -> None:
    """Run the interactive prompt for users who prefer to answer questions."""
    log("Interactive mode started. Press Enter to accept suggested defaults.")
    try:
        raw_length = input("Enter password length (default 12): ").strip()
        length = int(raw_length) if raw_length else 12

        uc = input("Include uppercase letters? (y/N): ").strip().lower() == "y"
        dg = input("Include digits? (Y/n): ").strip().lower() != "n"  # default True
        sy = input("Include symbols? (y/N): ").strip().lower() == "y"

        pwd = generate_password(length=length, use_uppercase=uc, use_digits=dg, use_symbols=sy)
        print("\n✅ Generated Password:\n")
        print(pwd)
        print()
        log("Password generation completed.")
    except ValueError as ve:
        log(f"Input error: {ve}")
    except KeyboardInterrupt:
        log("Operation cancelled by user.")


def cli_mode() -> None:
    """Parse command line arguments and produce a password accordingly."""
    parser = argparse.ArgumentParser(
        prog="password_generator",
        description="Generate a strong random password (secure, configurable)."
    )
    parser.add_argument("-l", "--length", type=int, default=12, help="Password length (default: 12)")
    parser.add_argument("--no-uppercase", action="store_true", help="Exclude uppercase letters from the password")
    parser.add_argument("--no-digits", action="store_true", help="Exclude digits from the password")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude symbols from the password")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive prompt mode")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    use_uppercase = not args.no_uppercase
    use_digits = not args.no_digits
    use_symbols = not args.no_symbols

    try:
        password = generate_password(length=args.length, use_uppercase=use_uppercase, use_digits=use_digits, use_symbols=use_symbols)
        print(password)
        log("Password generated successfully (CLI mode).")
    except ValueError as ve:
        log(f"Error: {ve}")


if __name__ == "__main__":
    """
    Script entry point.
    Examples:
      - Interactive: python password_generator.py --interactive
      - CLI:         python password_generator.py --length 16
      - CLI (no symbols): python password_generator.py --length 14 --no-symbols
    """
    cli_mode()
