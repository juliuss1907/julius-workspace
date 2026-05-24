# save_markdown.py
import os
from datetime import datetime, timedelta
from pathlib import Path
from config import OUTPUT_SETTINGS


def format_filename(scraped_at):
    """
    Format filename based on config template

    Args:
        scraped_at: datetime or ISO string

    Returns:
        str: Formatted filename
    """
    if isinstance(scraped_at, str):
        dt = datetime.fromisoformat(scraped_at)
    else:
        dt = scraped_at

    # Available variables
    variables = {
        'date': dt.strftime('%Y-%m-%d'),
        'time': dt.strftime('%H%M'),
        'timestamp': dt.strftime('%Y%m%d_%H%M'),
        'datetime': dt.strftime('%Y-%m-%d_%H%M'),
        'year': dt.strftime('%Y'),
        'month': dt.strftime('%m'),
        'day': dt.strftime('%d'),
        'hour': dt.strftime('%H'),
        'minute': dt.strftime('%M'),
    }

    template = OUTPUT_SETTINGS['markdown']['filename_format']
    filename = template.format(**variables)

    return filename


def save_markdown(brief, scraped_at):
    """
    Save brief to markdown file

    Args:
        brief: Formatted brief text
        scraped_at: datetime or ISO string

    Returns:
        tuple: (success: bool, filepath: str)
    """
    if not OUTPUT_SETTINGS['markdown']['enabled']:
        print("📝 Markdown output disabled")
        return False, None

    try:
        # Get output path
        output_dir = OUTPUT_SETTINGS['markdown']['path']

        # Expand ~ to home directory
        output_dir = os.path.expanduser(output_dir)

        # Format filename
        filename = format_filename(scraped_at)

        # Full path (handle subdirectories in filename)
        filepath = os.path.join(output_dir, filename)

        # Create directories if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(brief)

        print(f"📝 Markdown saved: {filepath}")

        # Update index if enabled
        if OUTPUT_SETTINGS['markdown']['create_index']:
            update_index(output_dir, filepath, scraped_at)

        # Cleanup old files if configured
        keep_days = OUTPUT_SETTINGS['markdown']['keep_days']
        if keep_days > 0:
            cleanup_old_files(output_dir, keep_days)

        return True, filepath

    except Exception as e:
        print(f"❌ Error saving markdown: {e}")
        return False, None


def update_index(output_dir, new_filepath, scraped_at):
    """
    Update index.md with list of all briefs

    Args:
        output_dir: Base output directory
        new_filepath: Path to newly created brief
        scraped_at: datetime or ISO string
    """
    try:
        index_path = os.path.join(output_dir, 'index.md')

        if isinstance(scraped_at, str):
            dt = datetime.fromisoformat(scraped_at)
        else:
            dt = scraped_at

        icon = OUTPUT_SETTINGS['brief']['icon']

        # Relative path from index to brief
        rel_path = os.path.relpath(new_filepath, output_dir)

        # Entry line with full timestamp
        entry = f"- {dt.strftime('%Y-%m-%d %H:%M')} {icon} [Brief]({rel_path})\n"

        # Read existing index
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# News Brief Archive\n\n"

        # Check if entry already exists
        if rel_path not in content:
            # Insert after header
            lines = content.split('\n')
            header_end = 2  # After "# Title\n\n"
            lines.insert(header_end, entry.rstrip())
            content = '\n'.join(lines)

            # Write back
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"📑 Index updated: {index_path}")

    except Exception as e:
        print(f"⚠️  Could not update index: {e}")


def cleanup_old_files(output_dir, keep_days):
    """
    Delete markdown files older than keep_days

    Args:
        output_dir: Base output directory
        keep_days: Number of days to keep
    """
    try:
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0

        # Find all .md files (except index.md)
        for root, dirs, files in os.walk(output_dir):
            for filename in files:
                if filename == 'index.md':
                    continue

                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)

                    # Check file age
                    mtime = os.path.getmtime(filepath)
                    file_date = datetime.fromtimestamp(mtime)

                    if file_date < cutoff:
                        os.remove(filepath)
                        deleted_count += 1

        if deleted_count > 0:
            print(f"🗑️  Cleaned up {deleted_count} old markdown files")

    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")


def get_markdown_stats(output_dir=None):
    """
    Get statistics about saved markdown files

    Args:
        output_dir: Directory to analyze (default: from config)

    Returns:
        dict: Statistics
    """
    if output_dir is None:
        output_dir = OUTPUT_SETTINGS['markdown']['path']

    try:
        output_dir = os.path.expanduser(output_dir)

        if not os.path.exists(output_dir):
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'oldest_date': None,
                'newest_date': None
            }

        files = []
        total_size = 0

        for root, dirs, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename.endswith('.md') and filename != 'index.md':
                    filepath = os.path.join(root, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)

                    files.append({
                        'path': filepath,
                        'mtime': mtime,
                        'size': size
                    })
                    total_size += size

        if not files:
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'oldest_date': None,
                'newest_date': None
            }

        files.sort(key=lambda x: x['mtime'])

        return {
            'total_files': len(files),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'oldest_date': datetime.fromtimestamp(files[0]['mtime']).strftime('%Y-%m-%d'),
            'newest_date': datetime.fromtimestamp(files[-1]['mtime']).strftime('%Y-%m-%d')
        }

    except Exception as e:
        print(f"⚠️  Could not get stats: {e}")
        return None
