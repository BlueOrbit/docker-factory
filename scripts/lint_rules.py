#!/usr/bin/env python3
import os
import sys
import yaml
from collections import deque

IMAGES_DIR = "images"

def load_image_config(image_name):
    """加载镜像的配置文件"""
    config_path = os.path.join(IMAGES_DIR, image_name, "image.yml")
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        return {"_error": str(e)}

def check_required_files():
    """检查每个镜像目录是否包含必需的文件"""
    if not os.path.exists(IMAGES_DIR):
        print(f"Directory {IMAGES_DIR} not found.")
        return True

    violations = []

    for image_name in os.listdir(IMAGES_DIR):
        image_path = os.path.join(IMAGES_DIR, image_name)
        if not os.path.isdir(image_path):
            continue

        # 检查 Dockerfile 是否存在
        dockerfile_path = os.path.join(image_path, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            violations.append(f"[RULE VIOLATION] {image_name}: 'Dockerfile' is missing.")

        # 检查 image.yml 是否存在且格式正确
        image_yml_path = os.path.join(image_path, "image.yml")
        if not os.path.exists(image_yml_path):
            violations.append(f"[RULE VIOLATION] {image_name}: 'image.yml' is missing.")
        else:
            config = load_image_config(image_name)
            if config is None:
                violations.append(f"[RULE VIOLATION] {image_name}: 'image.yml' could not be loaded.")
            elif "_error" in config:
                violations.append(f"[RULE VIOLATION] {image_name}: 'image.yml' has invalid YAML syntax: {config['_error']}")
            else:
                # 检查必需字段
                if "image_name" not in config:
                    violations.append(f"[RULE VIOLATION] {image_name}: 'image.yml' is missing 'image_name' field.")
                elif config["image_name"] != image_name:
                    violations.append(f"[RULE VIOLATION] {image_name}: 'image_name' in image.yml ('{config['image_name']}') does not match directory name.")

        # 检查 pre-build.sh 和 pre-build.requires 的配对
        pre_build_path = os.path.join(image_path, "pre-build.sh")
        requires_path = os.path.join(image_path, "pre-build.requires")

        if os.path.exists(pre_build_path):
            if not os.path.exists(requires_path):
                violations.append(f"[RULE VIOLATION] {image_name}: 'pre-build.sh' exists but 'pre-build.requires' is missing.")
            else:
                with open(requires_path, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        violations.append(f"[RULE VIOLATION] {image_name}: 'pre-build.requires' is empty.")

    return violations

def check_circular_dependencies():
    """检查是否存在循环依赖"""
    if not os.path.exists(IMAGES_DIR):
        return []

    all_images = [d for d in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, d))]
    
    # 构建依赖图
    graph = {img: [] for img in all_images}
    for img in all_images:
        config = load_image_config(img)
        if config and "_error" not in config:
            deps = config.get("depends_on", [])
            for dep in deps:
                if dep in graph:
                    graph[img].append(dep)
                else:
                    # 依赖的镜像不存在
                    return [f"[RULE VIOLATION] {img}: depends on non-existent image '{dep}'."]

    # 使用拓扑排序检测循环依赖
    in_degree = {img: 0 for img in all_images}
    for img in all_images:
        for dep in graph[img]:
            in_degree[img] += 1

    queue = deque([img for img in all_images if in_degree[img] == 0])
    sorted_count = 0

    while queue:
        current = queue.popleft()
        sorted_count += 1
        
        for img in all_images:
            if current in graph[img]:
                in_degree[img] -= 1
                if in_degree[img] == 0:
                    queue.append(img)

    if sorted_count != len(all_images):
        remaining = [img for img in all_images if in_degree[img] > 0]
        return [f"[RULE VIOLATION] Circular dependency detected among images: {', '.join(sorted(remaining))}"]

    return []

def main():
    """运行所有规则检查"""
    all_violations = []

    # 检查必需文件
    violations = check_required_files()
    all_violations.extend(violations)

    # 检查循环依赖
    violations = check_circular_dependencies()
    all_violations.extend(violations)

    if all_violations:
        print("\n".join(all_violations))
        print(f"\nTotal violations: {len(all_violations)}")
        return False
    
    print("All validation rules passed.")
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1)
