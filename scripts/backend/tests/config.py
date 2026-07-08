BASE_URL = "http://localhost:8001"

TIMEOUT = 30

TEST_ACCOUNTS = {}

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}

P0_SCENES = [
    "scene_s1_health_check.py",
    "scene_s2_config.py",
    "scene_s3_question.py",
]

ALL_SCENES = [
    "scene_s1_health_check.py",
    "scene_s2_config.py",
    "scene_s3_question.py",
    "scene_s4_search.py",
    "scene_s5_generate.py",
    "scene_s6_transcript.py",
    "scene_s7_dialogue.py",
]
