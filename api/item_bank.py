"""
Item bank mapping question IDs to psychometric scales.
Compatible with paper tests, online forms, and Excel uploads.
"""

ITEM_BANK = {
    # RIASEC Career Interests
    "RIA_R01": {"text": "I like building, repairing, or assembling mechanical items.", "scale": "Realistic", "reverse": False},
    "RIA_I01": {"text": "I enjoy solving science experiments, logic puzzles, or coding.", "scale": "Investigative", "reverse": False},
    "RIA_A01": {"text": "I like writing creative stories, designing graphics, or music.", "scale": "Artistic", "reverse": False},
    "RIA_S01": {"text": "I enjoy mentoring, teaching, and helping people resolve problems.", "scale": "Social", "reverse": False},
    "RIA_E01": {"text": "I like leading teams, debating ideas, and pitching business plans.", "scale": "Enterprising", "reverse": False},
    "RIA_C01": {"text": "I prefer structured routines, organizing data, and following rules.", "scale": "Conventional", "reverse": False},
    
    # Self-Assessed Aptitude Dimensions
    "APT_NUM01": {"text": "I solve math equations and numerical puzzles quickly and accurately.", "scale": "Numerical Aptitude", "reverse": False},
    "APT_VER01": {"text": "I comprehend long reading passages easily and express ideas fluently.", "scale": "Verbal Aptitude", "reverse": False},
    "APT_SPA01": {"text": "I can visualize 3D shapes, diagrams, and patterns easily.", "scale": "Spatial Reasoning", "reverse": False},
    
    # Big Five Personality (IPIP Public Domain subset)
    "IPIP_O01": {"text": "I have a vivid imagination and love exploring new theories.", "scale": "Openness", "reverse": False},
    "IPIP_C01": {"text": "I complete tasks right away and pay attention to details.", "scale": "Conscientiousness", "reverse": False},
    "IPIP_E01": {"text": "I feel comfortable in large groups and initiate conversations.", "scale": "Extraversion", "reverse": False},
    "IPIP_A01": {"text": "I sympathize with others' feelings and cooperate easily.", "scale": "Agreeableness", "reverse": False},
    "IPIP_N01": {"text": "I frequently feel anxious or stressed before major exams.", "scale": "Neuroticism", "reverse": False},
}
