from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = Path(__file__).resolve().parent
SOURCE = ROOT / 'data' / 'AmesHousing.csv'
CLEANED = ANALYSIS_DIR / 'ames_analysis.csv'
RESULTS = ANALYSIS_DIR / 'results_table.csv'
MODEL_COMPARISON = ANALYSIS_DIR / 'model_comparison.csv'
PLOT = ANALYSIS_DIR / 'results_plot.png'
REQUIRED = ['Lot Area', 'SalePrice', 'Neighborhood']

def main():
    # Load and clean the source without modifying it. Keep all columns for valid rows.
    data = pd.read_csv(SOURCE)
    for col in ['Lot Area', 'SalePrice']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data['Neighborhood'] = data['Neighborhood'].astype('string').str.strip()
    data.loc[data['Neighborhood'].eq(''), 'Neighborhood'] = pd.NA
    missing_counts = data[REQUIRED].isna().sum().astype(int)
    exact_duplicates = int(data.duplicated().sum())
    nonpositive_lot = int((data['Lot Area'].notna() & (data['Lot Area'] <= 0)).sum())
    nonpositive_price = int((data['SalePrice'].notna() & (data['SalePrice'] <= 0)).sum())
    data = data.dropna(subset=REQUIRED).copy()
    data = data[(data['Lot Area'] > 0) & (data['SalePrice'] > 0)].copy()
    data['Neighborhood'] = data['Neighborhood'].astype(str)

    # Identify IQR outliers for the report; retain them in the analysis.
    outlier_counts = {}
    for col in ['Lot Area', 'SalePrice']:
        q1, q3 = data[col].quantile([.25, .75])
        iqr = q3 - q1
        outlier_counts[col] = int(((data[col] < q1 - 1.5*iqr) | (data[col] > q3 + 1.5*iqr)).sum())
    data.to_csv(CLEANED, index=False)

    # Primary model allows a separate linear lot-area slope in each neighborhood.
    linear_formula = 'Q("SalePrice") ~ Q("Lot Area") * C(Neighborhood)'
    linear = smf.ols(linear_formula, data=data).fit(cov_type='HC3')
    neighborhoods = sorted(data['Neighborhood'].unique())
    reference = neighborhoods[0]
    interaction_idx = [i for i, name in enumerate(linear.params.index)
                       if name.startswith('Q("Lot Area"):C(Neighborhood)[T.')]
    interaction_test = linear.wald_test(np.eye(len(linear.params))[interaction_idx], scalar=True)

    rows = []
    for neighborhood in neighborhoods:
        weights = pd.Series(0.0, index=linear.params.index)
        weights['Q("Lot Area")'] = 1.0
        if neighborhood != reference:
            term = f'Q("Lot Area"):C(Neighborhood)[T.{neighborhood}]'
            if term in weights.index:
                weights[term] = 1.0
        slope = float(weights @ linear.params)
        variance = float(weights @ linear.cov_params() @ weights)
        se = np.sqrt(max(variance, 0.0))
        n = int((data['Neighborhood'] == neighborhood).sum())
        rows.append({
            'Neighborhood': neighborhood, 'n': n,
            'slope_usd_per_sqft': slope, 'robust_se': se,
            'ci95_low': slope - 1.96*se, 'ci95_high': slope + 1.96*se,
            'small_sample_flag_n_lt_20': n < 20,
        })
    results = pd.DataFrame(rows).sort_values('slope_usd_per_sqft', ascending=False)
    results.to_csv(RESULTS, index=False)

    # Quadratic model is a sensitivity check because earlier diagnostics suggested curvature.
    quadratic_formula = 'Q("SalePrice") ~ (Q("Lot Area") + I(Q("Lot Area")**2)) * C(Neighborhood)'
    quadratic = smf.ols(quadratic_formula, data=data).fit()
    comparison = pd.DataFrame([
        {'model':'Linear interaction (primary)', 'n':len(data), 'r_squared':linear.rsquared,
         'adjusted_r_squared':linear.rsquared_adj, 'aic':linear.aic,
         'purpose':'Neighborhood-specific linear slopes; HC3 robust inference'},
        {'model':'Quadratic interaction (sensitivity)', 'n':len(data), 'r_squared':quadratic.rsquared,
         'adjusted_r_squared':quadratic.rsquared_adj, 'aic':quadratic.aic,
         'purpose':'Allows curvature in lot area; exploratory sensitivity check'},
    ])
    comparison.to_csv(MODEL_COMPARISON, index=False)

    # Plot all neighborhoods with at least 20 sales for legibility; CSV includes all groups.
    plot_data = results.loc[~results['small_sample_flag_n_lt_20']].sort_values('slope_usd_per_sqft')
    fig, ax = plt.subplots(figsize=(9, max(6, .32*len(plot_data))))
    xerr = np.vstack([plot_data['slope_usd_per_sqft'] - plot_data['ci95_low'],
                      plot_data['ci95_high'] - plot_data['slope_usd_per_sqft']])
    ax.errorbar(plot_data['slope_usd_per_sqft'], plot_data['Neighborhood'], xerr=xerr,
                fmt='o', color='#315f8a', ecolor='#8ba8c2', capsize=3, markersize=5)
    ax.axvline(0, color='#b34a3c', linestyle='--', linewidth=1)
    ax.set_xlabel('Estimated sale price change per additional lot-area sq ft (USD)')
    ax.set_ylabel('Neighborhood')
    ax.set_title('Neighborhood-specific lot area slopes (95% HC3 confidence intervals)')
    ax.text(0, -0.13, 'Linear interaction model; chart shows neighborhoods with n ≥ 20. Full table includes every neighborhood.',
            transform=ax.transAxes, ha='left', va='top', fontsize=8, color='#444')
    ax.grid(axis='x', alpha=.2)
    fig.tight_layout()
    fig.savefig(PLOT, dpi=180, bbox_inches='tight')
    plt.close(fig)

    print('ANALYSIS SUMMARY')
    print(f'Source rows: {len(pd.read_csv(SOURCE)):,}; analysis rows: {len(data):,}; columns retained: {data.shape[1]}')
    print(f'Missing required fields: {missing_counts.to_dict()}')
    print(f'Exact duplicates found: {exact_duplicates}; nonpositive Lot Area/SalePrice: {nonpositive_lot}/{nonpositive_price}')
    print(f'IQR outlier flags retained: {outlier_counts}')
    print(f'Neighborhoods: {len(neighborhoods)}; groups with n < 20: {int((results.n < 20).sum())}')
    print('PRIMARY MODEL: OLS linear interaction with HC3 robust standard errors')
    print(f'Formula: {linear_formula}')
    print(f'R-squared={linear.rsquared:.4f}; adjusted R-squared={linear.rsquared_adj:.4f}; AIC={linear.aic:.1f}')
    print(f'Joint Wald test that neighborhood slopes are equal: p={float(interaction_test.pvalue):.4g}')
    print('SENSITIVITY MODEL: quadratic interaction')
    print(f'R-squared={quadratic.rsquared:.4f}; adjusted R-squared={quadratic.rsquared_adj:.4f}; AIC={quadratic.aic:.1f}')
    print('Lower AIC favors the quadratic fit in this sample; it is a sensitivity comparison, not a predictive validation.')
    print(f'Outputs: {CLEANED.name}, {RESULTS.name}, {MODEL_COMPARISON.name}, {PLOT.name}')
    print('Main results: neighborhood slopes in USD per additional sq ft (95% HC3 CI)')
    print(results[['Neighborhood','n','slope_usd_per_sqft','ci95_low','ci95_high']]
          .to_string(index=False, formatters={k:'{:,.2f}'.format for k in ['slope_usd_per_sqft','ci95_low','ci95_high']}))
    print('Interpretation: associations are not causal; very small neighborhood samples have unstable slope estimates.')

if __name__ == '__main__':
    main()
