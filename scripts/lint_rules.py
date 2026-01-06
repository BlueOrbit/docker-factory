#!/usr/bin/env python3
import os
import sys

IMAGES_DIR = "images"

def check_pre_build_rules():
    if not os.path.exists(IMAGES_DIR):
        print(f"Directory {IMAGES_DIR} not found.")
        return True

    violations = []

    for image_name in os.listdir(IMAGES_DIR):
        image_path = os.path.join(IMAGES_DIR, image_name)
        if not os.path.isdir(image_path):
            continue

        pre_build_path = os.path.join(image_path, "pre-build.sh")
        requires_path = os.path.join(image_path, "pre-build.requires")

        if os.path.exists(pre_build_path):
            if not os.path.exists(requires_path):
                violations.append(f"[RULE VIOLATION] {image_name}: 'pre-build.sh' exists but 'pre-build.requires' is missing.")
            else:
                # Basic check: requires file should not be empty
                with open(requires_path, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        violations.append(f"[RULE VIOLATION] {image_name}: 'pre-build.requires' is empty.")

    if violations:
        print("\n".join(violations))
        return False
    
    print("All pre-build rules passed.")
    return True

if __name__ == "__main__":
    if not check_pre_build_rules():
        sys.exit(1)
