#!/usr/bin/env python
from social_media_manager.crew import SocialMediaManager
import sys
from datetime import datetime

def run():
    """Main entry point for the crew"""
    print("\n" + "="*70)
    print("Personalized Interview DM Generator")
    print("="*70 + "\n")

    # Collect all dynamic inputs from the user
    person_name = input("Enter the name of the person/expert you want to contact: ").strip()
    if not person_name:
        print("No name provided. Exiting.")
        sys.exit(0)

    niche = input("Enter the niche/field (e.g. AI, Cooking, Gaming): ").strip()
    if not niche:
        print("No niche provided. Exiting.")
        sys.exit(0)

    youtube_channel = input("Enter your YouTube channel handle (e.g. @MrBeast: ").strip()
    if not youtube_channel:
        print("No YouTube channel provided. Exiting.")
        sys.exit(0)

    your_name = input("Enter your first name for the DM signature: ").strip()
    if not your_name:
        print("No name provided. Exiting.")
        sys.exit(0)

    print(f"\nStarting outreach process for: {person_name}")
    print(f"Niche: {niche}")
    print("Researching recent highlights...")

    # Pass all dynamic values to the crew
    inputs = {
        "person_name": person_name,
        "niche": niche,
        "youtube_channel": youtube_channel,
        "name": your_name,
        "current_year": str(datetime.now().year)  # Automatically use current year
    }

    try:
        result = SocialMediaManager().crew().kickoff(inputs=inputs)
        print("\n" + "="*80)
        print("Final Personalized DM:")
        print("-"*80)
        print(result)
        print("="*80 + "\n")
    except Exception as e:
        print(f"Error running crew: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
