#!/usr/bin/env python3
import os
import json
import yaml
import argparse
import sys
from collections import deque

IMAGES_DIR = "images"

def load_image_config(image_name):
    config_path = os.path.join(IMAGES_DIR, image_name, "image.yml")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_all_images():
    if not os.path.exists(IMAGES_DIR):
        return []
    return [d for d in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, d))]

def build_dependency_graph(images):
    graph = {img: [] for img in images}
    reverse_graph = {img: [] for img in images}
    
    for img in images:
        config = load_image_config(img)
        if not config:
            continue
        deps = config.get("depends_on", [])
        for dep in deps:
            if dep in graph:
                graph[img].append(dep)
                reverse_graph[dep].append(img)
    return graph, reverse_graph

def get_affected_images(changed_images, reverse_graph):
    affected = set(changed_images)
    queue = deque(changed_images)
    
    while queue:
        current = queue.popleft()
        for dependent in reverse_graph.get(current, []):
            if dependent not in affected:
                affected.add(dependent)
                queue.append(dependent)
    return list(affected)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--changes", help="JSON list of changed image names", default="[]")
    parser.add_argument("--all", action="store_true", help="Build all images")
    args = parser.parse_args()

    all_images = get_all_images()
    _, reverse_graph = build_dependency_graph(all_images)

    if args.all:
        target_images = all_images
    else:
        try:
            changed = json.loads(args.changes)
            if not isinstance(changed, list):
                print("Error: --changes must be a JSON list", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON for --changes", file=sys.stderr)
            sys.exit(1)
            
        # Filter changed to only valid images
        changed = [img for img in changed if img in all_images]
        target_images = get_affected_images(changed, reverse_graph)

    # Generate Matrix
    matrix_include = []
    for img in target_images:
        config = load_image_config(img)
        matrix_include.append({
            "name": img,
            "path": f"images/{img}",
            "platforms": ",".join(config.get("platforms", ["linux/amd64"])) if config else "linux/amd64"
        })

    # Output for GitHub Actions
    output = {"include": matrix_include}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
