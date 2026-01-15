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

def topological_sort_with_layers(images, graph):
    """对镜像进行拓扑排序，返回分层结构
    
    Returns:
        list[list[str]]: 分层的镜像列表，每层可以并行构建
    
    Raises:
        SystemExit: 如果检测到循环依赖
    """
    # 计算每个镜像的入度
    in_degree = {img: 0 for img in images}
    for img in images:
        for dep in graph.get(img, []):
            if dep in images:
                in_degree[img] += 1
    
    # 使用 Kahn 算法进行分层拓扑排序
    layers = []
    remaining = set(images)
    
    while remaining:
        # 找出当前层所有入度为 0 的镜像
        current_layer = [img for img in remaining if in_degree[img] == 0]
        
        if not current_layer:
            # 无法继续，说明存在循环依赖
            print(f"Error: Circular dependency detected among images: {sorted(remaining)}", file=sys.stderr)
            print("Please check the 'depends_on' configuration in image.yml files.", file=sys.stderr)
            sys.exit(1)
        
        layers.append(sorted(current_layer))
        
        # 从剩余集合中移除当前层
        for img in current_layer:
            remaining.remove(img)
        
        # 更新依赖当前层镜像的其他镜像的入度
        for img in remaining:
            for dep in graph.get(img, []):
                if dep in current_layer:
                    in_degree[img] -= 1
    
    return layers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--changes", help="JSON list of changed image names", default="[]")
    parser.add_argument("--all", action="store_true", help="Build all images")
    args = parser.parse_args()

    all_images = get_all_images()
    graph, reverse_graph = build_dependency_graph(all_images)

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

    # 对目标镜像进行分层拓扑排序
    layers = topological_sort_with_layers(target_images, graph)

    # 生成分层矩阵，每层可以并行构建
    layered_output = []
    for layer_idx, layer_images in enumerate(layers):
        layer_matrix = []
        for img in layer_images:
            config = load_image_config(img)
            layer_matrix.append({
                "name": img,
                "path": f"images/{img}",
                "platforms": ",".join(config.get("platforms", ["linux/amd64"])) if config else "linux/amd64"
            })
        layered_output.append({
            "layer": layer_idx,
            "include": layer_matrix
        })

    # 输出分层结构供 GitHub Actions 使用
    output = {"layers": layered_output}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
