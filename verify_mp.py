import warnings
warnings.filterwarnings("ignore")
try:
    import mediapipe as mp
    try:
        from mediapipe import solutions
    except ImportError:
        try:
            import mediapipe.python.solutions as solutions
        except ImportError:
            solutions = None
            
    if solutions:
        mp.solutions = solutions
        
    print(f"Has solutions: {hasattr(mp, 'solutions')}")
    if hasattr(mp, 'solutions'):
        print(f"Face detection available: {hasattr(mp.solutions, 'face_detection')}")
except Exception as e:
    print(f"Error: {e}")
