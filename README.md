# DSA 8670 Week 7: Codex CLI Hands-On — Ames Housing Analysis

**Author:** Seth Rueger  
**Codex session:** October 13–14, 2026

## 1. Analytical Question

**How does the relationship between lot size and sale price change across neighborhoods?**

Lot size and location can both influence residential property values, but their relationships may differ across neighborhoods. This analysis investigates whether the estimated association between lot area and sale price varies by neighborhood rather than assuming that a single relationship applies uniformly across Ames, Iowa.

The goal is to produce a reproducible analytical workflow that includes data validation, cleaning, statistical modeling, model comparison, visualizations, and an interpretable summary of the findings.

## 2. Summary of Findings

Using 2,930 Ames Housing sales, I estimated neighborhood-specific linear associations between lot area and sale price across 28 neighborhoods. The estimated increase in sale price was approximately **$16.90 per additional square foot of lot area in NridgHt**, compared with **$4.81 in NAmes**. The estimated relationships varied across neighborhoods, supporting the use of neighborhood-specific slopes to examine these differences.

Four neighborhoods have fewer than 20 sales: Blueste (10), Greens (8), GrnHill (2), and Landmrk (1). These small sample sizes warrant caution when interpreting their estimates. In particular, a meaningful within-neighborhood slope cannot be estimated from Landmrk's single observation.

The analysis also compares a linear interaction model with a quadratic sensitivity model. The quadratic model had a higher R-squared and lower Akaike information criterion (AIC), indicating a better fit to the observed data under these measures. However, better in-sample fit does not establish better predictive performance on unseen data.

The script reports a joint test of neighborhood-specific slopes. Because some neighborhoods have very small samples, the test should be interpreted cautiously rather than treated as conclusive evidence that all neighborhood relationships differ. Overall, these findings describe statistical associations in the observed dataset, not causal effects.

## 3. Data and Analytical Approach

### Data validation and cleaning

The analysis uses `data/AmesHousing.csv`, containing 2,930 observations and 82 columns. The workflow checks for missing values, duplicate rows, and nonpositive values in the fields required for the analysis: `Lot Area`, `SalePrice`, and `Neighborhood`.

All 2,930 rows had usable values for these required fields. Potential outliers were identified using the interquartile range (IQR) method and flagged rather than automatically removed. This preserves the original observations while making potential extreme values available for review.

### Statistical modeling

The primary analysis uses ordinary least squares (OLS) regression with neighborhood-specific lot-area slopes. HC3 robust standard errors are used to account for potential heteroskedasticity when estimating uncertainty.

A quadratic interaction model serves as a sensitivity check against the primary linear specification. Comparing the models provides additional context about whether allowing a nonlinear relationship improves fit to the observed data. Model fit statistics are interpreted as measures of in-sample fit, not as substitutes for out-of-sample validation.

### Interpretation and limitations

The estimated slopes describe the association between lot area and sale price within each neighborhood, holding the model's specified structure constant. They should not be interpreted as causal effects.

Sample size is an important limitation, particularly for neighborhoods with fewer than 20 sales. Estimates from these groups may be unstable or difficult to interpret, and Landmrk's slope is not estimable from one observation. The analysis also does not establish how accurately the models would predict future sale prices.

## 4. Repository Contents

### Source data and analysis

- `data/AmesHousing.csv` — source Ames Housing dataset.
- `analysis/ames_analysis.py` — Python script for data validation, cleaning, statistical modeling, and output generation.
- `analysis/ames_analysis.csv` — cleaned analysis dataset used in the modeling workflow.
- `analysis/analysis_diagnostics.json` — machine-readable summary of data checks, row counts, outlier flags, and model diagnostics.

### Results and visualizations

- `analysis/results_table.csv` — neighborhood-specific slope estimates, robust standard errors, confidence intervals, and small-sample flags.
- `analysis/model_comparison.csv` — comparison of the linear interaction model and quadratic sensitivity model, including model-fit statistics.
- `analysis/neighborhood_lot_price_summary.csv` — neighborhood-level descriptive statistics and estimated lot-area relationships.
- `analysis/chart.png` — presentation chart of neighborhood-specific slope estimates.
- `analysis/results_table.png` — image version of the results table and model comparison.
- `analysis/lot_area_sale_price_by_neighborhood.png` — exploratory visualization of lot area and sale price by neighborhood.
- `analysis/findings-narrative.txt` — plain-language summary of the findings, uncertainty, and limitations.

### Documentation of the AI-assisted workflow

- `prompts/prompt-history.md` — record of the prompts used during the Codex session.
- `log/ai-workflow-log.md` — per-prompt workflow log documenting the process and analytical development.
- `reflection.md` — reflection on the workflow, challenges, validation, and lessons learned.

The repository may also contain `.gitkeep`, which helps Git track a directory, and `.ipynb_checkpoints`, which is associated with Jupyter notebook checkpoint files. These are supporting files rather than analytical deliverables.

## 5. Reproducing the Analysis

Run the following commands from the repository root. Python must be installed before starting.

Install the required packages if they are not already available:

```bash
python -m pip install pandas numpy matplotlib statsmodels
```

Run the analysis script:

```bash
python analysis/ames_analysis.py
```

The script reads the source dataset, performs the documented data checks and cleaning steps, fits the statistical models, and generates analytical outputs under the `analysis/` directory. The existing CSV, JSON, and image artifacts in the repository provide the documented results of the completed workflow.

For reproducibility, run the script from the repository root and retain the source dataset at `data/AmesHousing.csv`. The generated outputs should be checked against the committed artifacts if the script, data, or analysis settings are changed.

## 6. Project Takeaway

This project demonstrates an end-to-end, AI-assisted analytical workflow: defining a focused research question, inspecting and validating data, developing a reusable Python analysis, comparing model specifications, producing interpretable outputs, and independently checking key results.

The workflow also emphasizes that generating code and results is not sufficient by itself. Analytical assumptions, small-sample limitations, model interpretation, output consistency, and reproducibility must be evaluated before presenting conclusions. The prompt history, workflow log, analysis artifacts, and reflection document how the work developed and how the results were reviewed.