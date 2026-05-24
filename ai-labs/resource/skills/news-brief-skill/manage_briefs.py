# manage_briefs.py
import sys
from save_markdown import get_markdown_stats, cleanup_old_files
from config import OUTPUT_SETTINGS


def show_stats():
    """Show statistics about saved briefs"""
    output_dir = OUTPUT_SETTINGS['markdown']['path']
    stats = get_markdown_stats(output_dir)

    if not stats:
        print("No statistics available")
        return

    print("=" * 60)
    print("News Brief Archive Statistics")
    print("=" * 60)
    print(f"Total files: {stats['total_files']}")
    print(f"Total size: {stats['total_size_mb']} MB")
    print(f"Oldest brief: {stats['oldest_date']}")
    print(f"Newest brief: {stats['newest_date']}")
    print("=" * 60)


def cleanup(days):
    """Cleanup old briefs"""
    output_dir = OUTPUT_SETTINGS['markdown']['path']
    print(f"Cleaning up briefs older than {days} days...")
    cleanup_old_files(output_dir, days)
    print("Done")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 manage_briefs.py stats")
        print("  python3 manage_briefs.py cleanup <days>")
        return

    command = sys.argv[1]

    if command == 'stats':
        show_stats()
    elif command == 'cleanup':
        if len(sys.argv) < 3:
            print("Error: cleanup requires <days> argument")
            return
        days = int(sys.argv[2])
        cleanup(days)
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
