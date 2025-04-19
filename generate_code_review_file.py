import os
import argparse

def generate_code_review_file(root_dir, output_file, extensions=None, exclude_dirs=None, exclude_files=None):
    """
    Generate a file containing concatenated code from the project with proper markers.
    
    Args:
        root_dir (str): Root directory of the project
        output_file (str): Path to the output file
        extensions (list): List of file extensions to include (e.g., ['.py', '.js'])
        exclude_dirs (list): List of directories to exclude
        exclude_files (list): List of files to exclude
    """
    if extensions is None:
        extensions = ['.py']
    
    if exclude_dirs is None:
        exclude_dirs = ['venv', '.git', '__pycache__', '.pytest_cache']
    
    if exclude_files is None:
        exclude_files = []
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip excluded directories
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir)
                
                # Skip if file extension not in extensions or file is in exclude_files
                if not any(filename.endswith(ext) for ext in extensions) or rel_path in exclude_files:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                    
                    # Write file markers and content
                    f.write(f"--- START FILE: {rel_path} ---\n")
                    f.write(content)
                    if not content.endswith('\n'):
                        f.write('\n')
                    f.write(f"--- END FILE: {rel_path} ---\n\n")
                    
                    print(f"Added: {rel_path}")
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a code review file from project files')
    parser.add_argument('--root', default='.', help='Root directory of the project')
    parser.add_argument('--output', default='codebase_for_review.txt', help='Output file path')
    parser.add_argument('--extensions', nargs='+', default=['.py'], help='File extensions to include')
    parser.add_argument('--exclude-dirs', nargs='+', default=['venv', '.git', '__pycache__', '.pytest_cache'], 
                        help='Directories to exclude')
    parser.add_argument('--exclude-files', nargs='+', default=[], help='Files to exclude')
    
    args = parser.parse_args()
    
    generate_code_review_file(
        args.root, 
        args.output, 
        args.extensions, 
        args.exclude_dirs, 
        args.exclude_files
    )
    
    print(f"\nCode review file generated at: {args.output}")
    print(f"Total files processed: {sum(1 for line in open(args.output) if line.startswith('--- START FILE:'))}")
