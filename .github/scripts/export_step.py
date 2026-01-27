#!/usr/bin/env python3
"""
export_step.py - Export FreeCAD documents to STEP format

Usage: freecadcmd export_step.py <file1.FCStd> [file2.FCStd] ...

Exports all solid bodies from each FreeCAD file to STEP format.
Output goes to CAD_INTERNAL/STEP_FILES/<original_filename>.step
"""

from __future__ import print_function
import sys
import os

# Force unbuffered output for CI environments
sys.stdout.flush()

print("STEP Export Script")
print("=" * 50)

try:
    import FreeCAD
    import Part
    import Import
except ImportError as e:
    print(f"ERROR: Could not import FreeCAD modules: {e}")
    sys.exit(1)


def get_all_shapes(doc):
    """Find all exportable shapes in the document."""
    shapes = []
    
    # Types to skip (helper objects, not geometry)
    skip_types = [
        'Sketcher::SketchObject', 
        'PartDesign::Plane', 
        'PartDesign::Line', 
        'PartDesign::Point',
        'App::Origin', 
        'App::Plane', 
        'App::Line'
    ]
    
    for obj in doc.Objects:
        # Skip if object has no Shape attribute
        if not hasattr(obj, 'Shape'):
            continue
        
        # Skip if shape is null
        try:
            if obj.Shape.isNull():
                continue
        except Exception:
            continue
        
        # Check for solids
        try:
            if len(obj.Shape.Solids) == 0:
                continue
        except Exception:
            continue
        
        # Skip helper objects
        if obj.TypeId in skip_types:
            continue
        
        # This object is exportable
        print(f"  Found: {obj.Name} ({obj.TypeId}) - {len(obj.Shape.Solids)} solid(s)")
        shapes.append(obj)
    
    return shapes


def export_to_step(input_path):
    """Export a FreeCAD file to STEP format."""
    
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        return None
    
    # Determine output path
    # Input:  */CAD_INTERNAL/FREECAD_FILES/Design.FCStd
    # Output: */CAD_INTERNAL/STEP_FILES/Design.step
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Find the CAD_INTERNAL directory
    input_dir = os.path.dirname(os.path.abspath(input_path))
    if 'CAD_INTERNAL' in input_dir:
        cad_internal = input_dir.split('CAD_INTERNAL')[0] + 'CAD_INTERNAL'
    else:
        cad_internal = os.path.dirname(input_dir)
    
    output_dir = os.path.join(cad_internal, 'STEP_FILES')
    output_path = os.path.join(output_dir, f"{base_name}.step")
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nProcessing: {input_path}")
    print(f"Output to:  {output_path}")
    
    # Open the document
    try:
        doc = FreeCAD.openDocument(input_path)
    except Exception as e:
        print(f"ERROR: Could not open document: {e}")
        return None
    
    # Find all exportable shapes
    print("Scanning for exportable bodies...")
    shapes = get_all_shapes(doc)
    
    if not shapes:
        print("WARNING: No exportable solid bodies found in document")
        FreeCAD.closeDocument(doc.Name)
        return None
    
    print(f"Exporting {len(shapes)} object(s)...")
    
    # Export to STEP
    try:
        Import.export(shapes, output_path)
        
        # Verify export
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"SUCCESS: Exported to {output_path} ({size_mb:.1f} MB)")
            FreeCAD.closeDocument(doc.Name)
            return output_path
        else:
            print("ERROR: Export completed but file not created")
            FreeCAD.closeDocument(doc.Name)
            return None
            
    except Exception as e:
        print(f"ERROR: Export failed: {e}")
        FreeCAD.closeDocument(doc.Name)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: freecadcmd export_step.py <file1.FCStd> [file2.FCStd] ...")
        sys.exit(1)
    
    input_files = sys.argv[1:]
    results = []
    
    print(f"Processing {len(input_files)} file(s)")
    
    for input_file in input_files:
        result = export_to_step(input_file)
        results.append((input_file, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("Export Summary")
    print("="*50)
    
    success_count = sum(1 for _, r in results if r)
    print(f"Successful: {success_count}/{len(results)}")
    
    for input_file, output_file in results:
        status = "✓" if output_file else "✗"
        print(f"  {status} {os.path.basename(input_file)}")
    
    if success_count == 0:
        print("\nNo files were exported.")
        sys.exit(0)  # Don't fail - workflow handles empty case


# Run main directly (required for freecadcmd)
main()
