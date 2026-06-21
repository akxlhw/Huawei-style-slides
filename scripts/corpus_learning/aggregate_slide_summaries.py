"""
跨页聚合分析

聚合所有slide_summary，提取模式和规则。
"""
import os
import json
from collections import Counter, defaultdict


def aggregate_summaries(corpus_dir):
    """聚合所有slide summary"""
    summary_dir = os.path.join(corpus_dir, "slide_summaries")
    agg_dir = os.path.join(corpus_dir, "aggregate")
    os.makedirs(agg_dir, exist_ok=True)

    # 读取所有summary
    summaries = []
    for f in sorted(os.listdir(summary_dir)):
        if f.endswith('.json') and not f.endswith('_raw.txt'):
            path = os.path.join(summary_dir, f)
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if 'error' not in data or data.get('quality_for_learning') != 'exclude':
                    summaries.append(data)

    print(f"Loaded {len(summaries)} summaries")

    # 过滤
    filtered = [s for s in summaries if s.get('quality_for_learning') != 'exclude']
    excluded = [s for s in summaries if s.get('quality_for_learning') == 'exclude']

    with open(os.path.join(agg_dir, 'filtered_slide_summaries.json'), 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    with open(os.path.join(agg_dir, 'excluded_slide_summaries.json'), 'w', encoding='utf-8') as f:
        json.dump(excluded, f, ensure_ascii=False, indent=2)

    # 1. Page type distribution
    type_counter = Counter(s.get('page_type', 'other') for s in filtered)
    with open(os.path.join(agg_dir, 'page_type_distribution.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(type_counter.most_common()), f, ensure_ascii=False, indent=2)

    # 2. Title patterns
    title_patterns = []
    for s in filtered:
        ta = s.get('title_analysis', {})
        if ta:
            title_patterns.append({
                'slide_id': s.get('slide_id'),
                'page_type': s.get('page_type'),
                'is_conclusion': ta.get('is_direct_conclusion'),
                'pattern': ta.get('title_pattern'),
                'strength': ta.get('strength'),
            })
    with open(os.path.join(agg_dir, 'title_patterns.json'), 'w', encoding='utf-8') as f:
        json.dump(title_patterns, f, ensure_ascii=False, indent=2)

    # 3. Reusable rules
    all_rules = []
    for s in filtered:
        rules = s.get('reusable_generation_rules', [])
        for r in rules:
            all_rules.append(r)
    rule_counter = Counter(all_rules)
    with open(os.path.join(agg_dir, 'reusable_rules_raw.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(rule_counter.most_common(50)), f, ensure_ascii=False, indent=2)

    # 4. Avoid patterns
    all_avoids = []
    for s in filtered:
        avoids = s.get('avoid_patterns', [])
        for a in avoids:
            all_avoids.append(a)
    avoid_counter = Counter(all_avoids)
    with open(os.path.join(agg_dir, 'avoid_patterns_raw.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(avoid_counter.most_common(30)), f, ensure_ascii=False, indent=2)

    # 5. Layout patterns by page type
    layout_by_type = defaultdict(list)
    for s in filtered:
        pt = s.get('page_type', 'other')
        vl = s.get('visual_layout', {})
        if vl:
            layout_by_type[pt].append({
                'slide_id': s.get('slide_id'),
                'layout_type': vl.get('layout_type'),
                'density': vl.get('density'),
            })
    with open(os.path.join(agg_dir, 'visual_layout_patterns.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(layout_by_type), f, ensure_ascii=False, indent=2)

    # 6. Content structure patterns
    structure_by_type = defaultdict(list)
    for s in filtered:
        pt = s.get('page_type', 'other')
        cs = s.get('content_structure', {})
        if cs:
            structure_by_type[pt].append({
                'slide_id': s.get('slide_id'),
                'structure_type': cs.get('structure_type'),
                'logic_flow': cs.get('logic_flow'),
            })
    with open(os.path.join(agg_dir, 'content_structure_patterns.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(structure_by_type), f, ensure_ascii=False, indent=2)

    print(f"\n=== Aggregate Complete ===")
    print(f"Filtered: {len(filtered)}, Excluded: {len(excluded)}")
    print(f"Page types: {dict(type_counter.most_common(10))}")
    print(f"Output: {agg_dir}")
