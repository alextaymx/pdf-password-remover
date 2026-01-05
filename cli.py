#!/usr/bin/env python3
"""
CLI tool for batch removing passwords from PDF files.
"""

import argparse
import sys
from pathlib import Path
import pikepdf


def remove_password(input_path: Path, output_path: Path, password: str) -> bool:
    """
    Remove password from a PDF file.
    
    Args:
        input_path: Path to the encrypted PDF
        output_path: Path for the unlocked PDF
        password: The password to unlock the PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)
        return True
    except pikepdf.PasswordError:
        print(f"  ✗ Wrong password for: {input_path.name}")
        return False
    except Exception as e:
        print(f"  ✗ Error processing {input_path.name}: {e}")
        return False


def process_files(files: list[Path], output_dir: Path, password: str) -> tuple[int, int]:
    """
    Process multiple PDF files.
    
    Returns:
        Tuple of (success_count, failure_count)
    """
    success = 0
    failed = 0
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files:
        if not file_path.exists():
            print(f"  ✗ File not found: {file_path}")
            failed += 1
            continue
            
        if file_path.suffix.lower() != '.pdf':
            print(f"  ✗ Not a PDF file: {file_path}")
            failed += 1
            continue
        
        output_name = f"{file_path.stem}_unlocked.pdf"
        output_path = output_dir / output_name
        
        print(f"  Processing: {file_path.name}")
        
        if remove_password(file_path, output_path, password):
            print(f"  ✓ Saved: {output_path}")
            success += 1
        else:
            failed += 1
    
    return success, failed


def main():
    parser = argparse.ArgumentParser(
        description="Batch remove passwords from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --password "secret" file.pdf
  python cli.py --password "secret" file1.pdf file2.pdf
  python cli.py --password "secret" --input-dir ./pdfs
  python cli.py --password "secret" --output-dir ./unlocked file.pdf
        """
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="PDF files to process"
    )
    
    parser.add_argument(
        "-p", "--password",
        required=True,
        help="Password to unlock the PDFs"
    )
    
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        help="Process all PDFs in this directory"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("./unlocked"),
        help="Output directory for unlocked PDFs (default: ./unlocked)"
    )
    
    args = parser.parse_args()
    
    # Collect files to process
    files_to_process = list(args.files)
    
    if args.input_dir:
        if args.input_dir.is_dir():
            files_to_process.extend(args.input_dir.glob("*.pdf"))
            files_to_process.extend(args.input_dir.glob("*.PDF"))
        else:
            print(f"Error: Input directory not found: {args.input_dir}")
            sys.exit(1)
    
    if not files_to_process:
        print("Error: No PDF files specified. Use --help for usage.")
        sys.exit(1)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in files_to_process:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    print(f"\n{'='*50}")
    print(f"PDF Password Remover")
    print(f"{'='*50}")
    print(f"Files to process: {len(unique_files)}")
    print(f"Output directory: {args.output_dir.absolute()}")
    print(f"{'='*50}\n")
    
    success, failed = process_files(unique_files, args.output_dir, args.password)
    
    print(f"\n{'='*50}")
    print(f"Results: {success} succeeded, {failed} failed")
    print(f"{'='*50}\n")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

