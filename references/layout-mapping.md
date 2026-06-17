# Layout Mapping

## PPTX → MckEngine

| Content Need | MckEngine Method | Notes |
|--------------|------------------|-------|
| Cover | `eng.cover()` | title, subtitle, author, date |
| TOC | `eng.toc()` | 3-5 chapter items |
| Executive summary | `eng.executive_summary()` | headline + 3 bullets |
| Key metric | `eng.big_number()` | number + unit + description |
| Data table | `eng.data_table()` | headers + rows |
| Table + insight | `eng.table_insight()` | recommended opening slide |
| Funnel | `eng.funnel()` | recruitment funnel stages |
| 2×2 matrix | `eng.matrix_2x2()` | priority or 9-box style |
| Timeline | `eng.timeline()` | milestones |
| Action plan | `eng.action_items()` | owner / timeline / action |
| Closing | `eng.closing()` | title + message |

## HTML → slide_type

| Content Need | slide_type | Notes |
|--------------|------------|-------|
| Cover | cover | big title, subtitle, meta |
| TOC | toc | numbered sections |
| Executive summary | executive_summary | headline + bullets |
| Data table | data_table | HTML table |
| Funnel | funnel | vertical/horizontal bars |
| 2×2 matrix | matrix_2x2 | CSS grid quadrants |
| Timeline | timeline | horizontal nodes |
| Action plan | action_grid | cards |
| Closing | closing | CTA / thank you |
