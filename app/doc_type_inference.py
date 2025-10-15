"""Document type inference from filename patterns."""
from pathlib import Path
from typing import Optional


def infer_doc_type(file_path: Path) -> str:
    """
    Infer document type from path and filename patterns.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Document type string
    """
    path_lower = str(file_path).lower()
    name_lower = file_path.name.lower()
    
    # Videos
    if file_path.suffix.lower() in ['.mp4', '.webm', '.avi', '.mov']:
        if "bootcamp" in path_lower:
            return "bootcamp_session"
        elif "pro training" in path_lower or "protrader" in path_lower:
            return "protrader_video"
        else:
            return "training_video"
    
    # PDFs and documents
    if "keytakeaways" in name_lower or "key takeaways" in name_lower:
        return "key_takeaways"
    
    if "drill" in name_lower and ("answer" in name_lower or "key" in name_lower):
        return "drill_answer_key"
    elif "drill" in name_lower:
        return "practice_drill"
    
    if "cheat" in name_lower or "reference" in name_lower:
        return "reference_sheet"
    
    if "battlecard" in name_lower:
        return "quick_reference"
    
    if "answer" in name_lower and "key" in name_lower:
        return "answer_key"
    
    # Office files
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        if "position" in name_lower or "sizing" in name_lower or "calculator" in name_lower:
            return "calculator"
        else:
            return "spreadsheet_data"
    
    if file_path.suffix.lower() in ['.docx', '.doc']:
        if "note" in name_lower:
            return "notes"
        else:
            return "document"
    
    # Text files
    if file_path.suffix.lower() == '.txt':
        return "text_document"
    
    # PDFs - default categorization
    if file_path.suffix.lower() == '.pdf':
        return "training_guide"
    
    return "document"


def get_doc_category(doc_type: str) -> str:
    """
    Map document type to broader category.
    
    Args:
        doc_type: Specific document type
        
    Returns:
        Category string
    """
    categories = {
        # Learning materials
        "key_takeaways": "learning_material",
        "practice_drill": "learning_material",
        "drill_answer_key": "learning_material",
        "answer_key": "learning_material",
        "training_guide": "learning_material",
        
        # Reference
        "reference_sheet": "reference",
        "quick_reference": "reference",
        "battlecard": "reference",
        
        # Video content
        "bootcamp_session": "video_instruction",
        "protrader_video": "video_instruction",
        "training_video": "video_instruction",
        
        # Tools
        "calculator": "tool",
        "spreadsheet_data": "data",
        
        # Other
        "notes": "supplementary",
        "document": "supplementary",
        "text_document": "supplementary",
    }
    
    return categories.get(doc_type, "general")


def get_difficulty_hint(file_path: Path) -> Optional[str]:
    """
    Infer difficulty level from filename if obvious.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Difficulty level or None
    """
    name_lower = file_path.name.lower()
    path_lower = str(file_path).lower()
    
    # Check for explicit markers
    if "beginner" in name_lower or "basics" in name_lower or "introduction" in name_lower:
        return "beginner"
    
    if "advanced" in name_lower:
        return "advanced"
    
    # Infer from structure
    if "part 1" in name_lower or "part1" in name_lower or "step 1" in name_lower:
        return "beginner"
    
    if "part 3" in name_lower or "part3" in name_lower or "part 4" in name_lower:
        return "intermediate"
    
    return None


# Example usage
if __name__ == "__main__":
    test_paths = [
        Path("ProTrader/Contextual_Market_Reading_Abilities_Part1_KeyTakeaways.pdf"),
        Path("ProTrader/Contextual_Market_Reading_Abilities_Part1_Drills.pdf"),
        Path("ProTrader/Contextual_Market_Reading_Abilities_Part1_AnswerKey.pdf"),
        Path("BootCamp/31st Jan/Mid.mp4"),
        Path("Tools/Position_Sizing.xlsx"),
        Path("Notes/Strategy_Notes.docx"),
        Path("Cheat_Sheets/System_Cheat_Sheets.pdf"),
    ]
    
    print("Document Type Inference Examples:")
    print("="*60)
    for path in test_paths:
        doc_type = infer_doc_type(path)
        category = get_doc_category(doc_type)
        difficulty = get_difficulty_hint(path)
        print(f"{path.name:50} → {doc_type:20} [{category}]" + (f" ({difficulty})" if difficulty else ""))
