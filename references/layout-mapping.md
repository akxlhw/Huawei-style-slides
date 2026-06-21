# Layout Mapping

35 layouts, all PPTX + HTML dual-track. Each row shows the content need, the
MckEngine method (PPTX track) and the HTML slide_type.

## Frame layouts

| Content Need | Layout | MckEngine Method | HTML slide_type |
|--------------|--------|------------------|-----------------|
| Cover | cover | `eng.cover()` | cover |
| Closing | closing | `eng.closing()` | closing |
| Agenda | toc | `eng.toc()` | toc |
| Funnel | funnel | `eng.funnel()` ⚠️RETIRED | funnel |

## Narrative layouts

| Content Need | Layout | MckEngine Method | HTML slide_type |
|--------------|--------|------------------|-----------------|
| Executive summary | executive_summary | `eng.executive_summary()` | executive_summary |
| Key metric | big_number | `eng.big_number()` | big_number |
| Three metrics | three_stat | `eng.three_stat()` | three_stat |
| Timeline | timeline | `eng.timeline()` | timeline |
| Action plan | action_items | `eng.action_items()` | action_items |
| Quote | quote | `eng.quote()` | quote |

## Stat / card layouts

| Content Need | Layout | MckEngine Method | HTML slide_type |
|--------------|--------|------------------|-----------------|
| Metric cards | metric_cards | `eng.metric_cards()` | metric_cards |
| 4-column overview | four_column | `eng.four_column()` | four_column |
| Icon grid | icon_grid | `eng.icon_grid()` | icon_grid |
| Icon + stat grid | icon_stat_grid | native `_render_icon_stat_grid` | icon_stat_grid |
| Pyramid steps | pyramid_steps | `eng.pyramid()` (staircase) | pyramid_steps |

## Table layouts

| Content Need | Layout | MckEngine Method | HTML slide_type |
|--------------|--------|------------------|-----------------|
| Data table | data_table | `eng.data_table()` | data_table |
| Table + insight | table_insight | `eng.table_insight()` | table_insight |
| Checklist / status | checklist_status | `eng.checklist()` | checklist_status |
| Scorecard | scorecard | `eng.scorecard()` | scorecard |

## Data charts

| Content Need | Layout | MckEngine Method | HTML slide_type | Gate limit |
|--------------|--------|------------------|-----------------|------------|
| Grouped bar | grouped_bar | `eng.grouped_bar()` | grouped_bar | ≤6 cats × ≤2 series |
| Horizontal bar | horizontal_bar | `eng.horizontal_bar()` | horizontal_bar | — |
| Donut | donut_chart | `eng.donut()` | donut_chart | ≤6 segments |
| KPI tracker | kpi_tracker | `eng.kpi_tracker()` | kpi_tracker | — |
| Radar / spider | radar_chart | native `_render_radar_chart` | radar_chart | 3-6 axes |
| Gantt | gantt_chart | native `_render_gantt_chart` | gantt_chart | ≤6 tasks |
| Harvey ball matrix | harvey_ball_compare | `eng.harvey_ball_table()` | harvey_ball_compare | scores 0-4 |

## Huawei logic diagrams (SmartArt-style)

| Content Need | Layout | MckEngine Method | HTML slide_type |
|--------------|--------|------------------|-----------------|
| Ecosystem ring (同心圆) | ecosystem_ring | native `_render_huawei_ring` | ecosystem_ring |
| Cycle / loop | cycle | `eng.cycle()` | cycle |
| Value chain / flow | value_chain | `eng.value_chain()` | value_chain |
| Decision tree | decision_tree | `eng.decision_tree()` | decision_tree |
| 2×2 matrix | matrix_2x2 | `eng.matrix_2x2()` | matrix_2x2 |
| SWOT | swot | `eng.swot()` | swot |
| Side-by-side | side_by_side | `eng.side_by_side()` | side_by_side |
| Case study (SAR) | case_study | `eng.case_study()` | case_study |
| Swim lane | swim_lane | native `_render_swim_lane` | swim_lane |
| True pyramid | pyramid_triangle | native `_render_pyramid_triangle` | pyramid_triangle |

## Gate constraints (gate_check_s3.py)

| Layout | Constraint |
|--------|-----------|
| donut / pie | segments ≤ 6 |
| grouped_bar | categories ≤ 6, series ≤ 3 (use ≤2 to avoid legend overflow) |
| process_chevron | steps ≤ 5 |
| matrix_2x2 | exactly 4 quadrants |
| All content slides | non-empty `source`, title > 10 chars |

## Native renderers

Layouts marked "native" are drawn directly with python-pptx shapes in
`scripts/pptx_renderer.py` (not via a built-in MckEngine method), because
MckEngine lacks a swim-lane / radar / gantt / concentric-ring primitive.
They all follow the standard pattern: `eng._ns()` → `add_action_title` → draw → `_footer`.
