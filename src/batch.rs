use std::collections::HashMap;
use std::path::Path;

use chrono::Datelike;
use serde::Deserialize;

use crate::config::{Config, PaperSize};
use crate::layout;

/// Top-level YAML batch configuration.
#[derive(Debug, Deserialize)]
pub struct BatchConfig {
    #[serde(default)]
    pub defaults: Defaults,
    #[serde(default)]
    pub matrix: HashMap<String, Vec<serde_yml::Value>>,
    #[serde(default)]
    pub exclude: Vec<HashMap<String, serde_yml::Value>>,
    pub output: String,
    #[serde(default)]
    pub layout_options: HashMap<String, LayoutOptions>,
}

/// Default values applied to every matrix combination.
#[derive(Debug, Default, Deserialize)]
pub struct Defaults {
    pub layout: Option<String>,
    pub year: Option<i32>,
    pub month: Option<u32>,
    pub paper: Option<String>,
    pub font: Option<String>,
    pub heading_font: Option<String>,
    pub locale: Option<String>,
    pub margin: Option<f64>,
}

/// Per-layout options (for layouts that have custom flags).
#[derive(Debug, Default, Deserialize, Clone)]
pub struct LayoutOptions {
    pub abbreviate: Option<bool>,
    pub abbreviate_all: Option<bool>,
    pub brand: Option<String>,
    pub color: Option<bool>,
}

/// A single expanded matrix combination as string key-value pairs.
type Combination = HashMap<String, String>;

/// Compute the Cartesian product of all matrix axes.
fn expand_matrix(matrix: &HashMap<String, Vec<serde_yml::Value>>) -> Vec<Combination> {
    let mut result: Vec<Combination> = vec![HashMap::new()];

    for (key, values) in matrix {
        let mut new_result = Vec::with_capacity(result.len() * values.len());
        for combo in &result {
            for val in values {
                let mut new_combo = combo.clone();
                new_combo.insert(key.clone(), value_to_string(val));
                new_result.push(new_combo);
            }
        }
        result = new_result;
    }

    result
}

/// Remove combinations that match any exclude entry.
fn filter_excludes(
    combinations: Vec<Combination>,
    excludes: &[HashMap<String, serde_yml::Value>],
) -> Vec<Combination> {
    combinations
        .into_iter()
        .filter(|combo| {
            !excludes.iter().any(|exclude| {
                exclude
                    .iter()
                    .all(|(k, v)| combo.get(k).is_some_and(|cv| *cv == value_to_string(v)))
            })
        })
        .collect()
}

/// Convert a serde_yml::Value to a display string.
fn value_to_string(v: &serde_yml::Value) -> String {
    match v {
        serde_yml::Value::String(s) => s.clone(),
        serde_yml::Value::Number(n) => n.to_string(),
        serde_yml::Value::Bool(b) => b.to_string(),
        _ => format!("{v:?}"),
    }
}

/// Replace `{key}` placeholders in the template with values from the combination and defaults.
fn substitute_template(
    template: &str,
    combo: &Combination,
    defaults: &Defaults,
) -> Result<String, String> {
    let mut result = String::with_capacity(template.len());
    let mut chars = template.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '{' {
            let mut key = String::new();
            for ch in chars.by_ref() {
                if ch == '}' {
                    break;
                }
                key.push(ch);
            }
            if let Some(val) = resolve_key(&key, combo, defaults) {
                result.push_str(&val);
            } else {
                return Err(format!("unresolved template variable: {{{key}}}"));
            }
        } else {
            result.push(ch);
        }
    }

    Ok(result)
}

/// Look up a key first in the combination, then in defaults.
fn resolve_key(key: &str, combo: &Combination, defaults: &Defaults) -> Option<String> {
    if let Some(v) = combo.get(key) {
        return Some(v.clone());
    }
    match key {
        "layout" => defaults.layout.clone(),
        "year" => defaults.year.map(|y| y.to_string()),
        "month" => defaults.month.map(|m| m.to_string()),
        "paper" => defaults.paper.clone(),
        "font" => defaults.font.clone(),
        "locale" => defaults.locale.clone(),
        "margin" => defaults.margin.map(|m| m.to_string()),
        _ => None,
    }
}

/// Resolve a combination + defaults into a layout name and Config.
fn resolve_combination(
    combo: &Combination,
    defaults: &Defaults,
    output_path: &str,
) -> Result<(String, Config), String> {
    let today = chrono::Local::now().date_naive();

    let layout_name = combo
        .get("layout")
        .cloned()
        .or_else(|| defaults.layout.clone())
        .ok_or("no 'layout' specified in matrix or defaults")?;

    // Validate layout name
    if !layout::LAYOUT_NAMES.contains(&layout_name.as_str()) {
        return Err(format!(
            "unknown layout: '{}'. Available: {:?}",
            layout_name,
            layout::LAYOUT_NAMES
        ));
    }

    let paper_str = combo
        .get("paper")
        .cloned()
        .or_else(|| defaults.paper.clone())
        .unwrap_or_else(|| "A4".into());

    let paper = PaperSize::from_str(&paper_str)
        .ok_or_else(|| format!("unknown paper size: '{paper_str}'"))?;

    let year = combo
        .get("year")
        .and_then(|v| v.parse().ok())
        .or(defaults.year)
        .unwrap_or(today.year());

    let month = combo
        .get("month")
        .and_then(|v| v.parse().ok())
        .or(defaults.month)
        .unwrap_or(today.month());

    if !(1..=12).contains(&month) {
        return Err(format!("month out of range: {month}"));
    }

    let font = combo
        .get("font")
        .cloned()
        .or_else(|| defaults.font.clone())
        .unwrap_or_else(|| "Sans".into());

    let heading_font = combo
        .get("heading_font")
        .cloned()
        .or_else(|| defaults.heading_font.clone());

    let locale = combo
        .get("locale")
        .cloned()
        .or_else(|| defaults.locale.clone())
        .unwrap_or_else(|| "en_US".into());

    let margin_mm = combo
        .get("margin")
        .and_then(|v| v.parse().ok())
        .or(defaults.margin)
        .unwrap_or(5.0);

    let config = Config {
        year,
        month,
        output: output_path.to_string(),
        paper,
        margin_mm,
        font,
        heading_font,
        locale,
    };

    Ok((layout_name, config))
}

/// Build a boxed Layout from a name and optional per-layout options.
fn build_layout(
    name: &str,
    options: Option<&LayoutOptions>,
) -> Result<Box<dyn layout::Layout>, String> {
    let opts = options.cloned().unwrap_or_default();
    match name {
        "month" => Ok(Box::new(layout::month::MonthLayout)),
        "big" => Ok(Box::new(layout::big::BigLayout)),
        "classic" => Ok(Box::new(layout::classic::ClassicLayout {
            abbreviate: opts.abbreviate.unwrap_or(false),
            abbreviate_all: opts.abbreviate_all.unwrap_or(false),
            brand: opts.brand.unwrap_or_default(),
            color_numbers: opts.color.unwrap_or(false),
        })),
        "column" => Ok(Box::new(layout::column::ColumnLayout {
            abbreviate: opts.abbreviate.unwrap_or(false),
            abbreviate_all: opts.abbreviate_all.unwrap_or(false),
        })),
        "oneyear" => Ok(Box::new(layout::oneyear::OneYearLayout)),
        _ => Err(format!(
            "unknown layout: '{}'. Available: {:?}",
            name,
            layout::LAYOUT_NAMES
        )),
    }
}

/// Run all matrix combinations from a YAML batch config file.
pub fn run_batch(path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let contents = std::fs::read_to_string(path)?;
    let batch: BatchConfig = serde_yml::from_str(&contents)?;

    let combinations = expand_matrix(&batch.matrix);
    let combinations = filter_excludes(combinations, &batch.exclude);

    let total = combinations.len();
    eprintln!("Matrix expanded to {total} combination(s)");

    // Resolve all output paths first to detect duplicates and validate early
    let mut resolved: Vec<(String, Config, String)> = Vec::with_capacity(total);
    for (i, combo) in combinations.iter().enumerate() {
        let output_path = substitute_template(&batch.output, combo, &batch.defaults)
            .map_err(|e| format!("combination {}: {e}", i + 1))?;

        let (layout_name, config) = resolve_combination(combo, &batch.defaults, &output_path)
            .map_err(|e| format!("combination {} ({}): {e}", i + 1, output_path))?;

        resolved.push((layout_name, config, output_path));
    }

    // Check for duplicate output paths
    let mut seen_paths: HashMap<&str, usize> = HashMap::new();
    for (i, (_, _, path)) in resolved.iter().enumerate() {
        if let Some(prev) = seen_paths.insert(path.as_str(), i) {
            return Err(format!(
                "duplicate output path '{}' from combinations {} and {}",
                path,
                prev + 1,
                i + 1,
            )
            .into());
        }
    }

    // Render all combinations
    let mut errors: Vec<(usize, String, String)> = Vec::new();

    for (i, (layout_name, config, output_path)) in resolved.iter().enumerate() {
        // Create parent directories
        if let Some(parent) = Path::new(&config.output).parent()
            && !parent.as_os_str().is_empty()
        {
            std::fs::create_dir_all(parent)?;
        }

        let layout_opts = batch.layout_options.get(layout_name.as_str());
        let layout = build_layout(layout_name, layout_opts)
            .map_err(|e| format!("combination {}: {e}", i + 1))?;

        eprint!("[{}/{}] {} ... ", i + 1, total, output_path);
        match crate::render_one(layout.as_ref(), config) {
            Ok(()) => {}
            Err(e) => {
                eprintln!("FAILED: {e}");
                errors.push((i, output_path.clone(), e.to_string()));
            }
        }
    }

    if errors.is_empty() {
        eprintln!("All {total} file(s) generated successfully.");
        Ok(())
    } else {
        eprintln!(
            "\n{}/{} succeeded, {} failed:",
            total - errors.len(),
            total,
            errors.len()
        );
        for (i, path, msg) in &errors {
            eprintln!("  [{}] {}: {}", i + 1, path, msg);
        }
        Err(format!("{} of {} combination(s) failed", errors.len(), total).into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expand_matrix_single_axis() {
        let mut matrix = HashMap::new();
        matrix.insert(
            "layout".to_string(),
            vec![
                serde_yml::Value::String("month".into()),
                serde_yml::Value::String("big".into()),
                serde_yml::Value::String("classic".into()),
            ],
        );

        let result = expand_matrix(&matrix);
        assert_eq!(result.len(), 3);
    }

    #[test]
    fn expand_matrix_two_axes() {
        let mut matrix = HashMap::new();
        matrix.insert(
            "layout".to_string(),
            vec![
                serde_yml::Value::String("month".into()),
                serde_yml::Value::String("big".into()),
            ],
        );
        matrix.insert(
            "paper".to_string(),
            vec![
                serde_yml::Value::String("A4".into()),
                serde_yml::Value::String("A3".into()),
                serde_yml::Value::String("A2".into()),
            ],
        );

        let result = expand_matrix(&matrix);
        assert_eq!(result.len(), 6);
    }

    #[test]
    fn expand_matrix_empty() {
        let matrix = HashMap::new();
        let result = expand_matrix(&matrix);
        assert_eq!(result.len(), 1);
        assert!(result[0].is_empty());
    }

    #[test]
    fn filter_excludes_removes_matching() {
        let mut matrix = HashMap::new();
        matrix.insert(
            "layout".to_string(),
            vec![
                serde_yml::Value::String("month".into()),
                serde_yml::Value::String("big".into()),
            ],
        );
        matrix.insert(
            "paper".to_string(),
            vec![
                serde_yml::Value::String("A4".into()),
                serde_yml::Value::String("A3".into()),
            ],
        );

        let combinations = expand_matrix(&matrix);
        assert_eq!(combinations.len(), 4);

        let mut exclude_entry = HashMap::new();
        exclude_entry.insert("layout".to_string(), serde_yml::Value::String("big".into()));
        exclude_entry.insert("paper".to_string(), serde_yml::Value::String("A3".into()));

        let filtered = filter_excludes(combinations, &[exclude_entry]);
        assert_eq!(filtered.len(), 3);

        // The excluded combination should not be present
        assert!(!filtered.iter().any(|c| {
            c.get("layout") == Some(&"big".to_string()) && c.get("paper") == Some(&"A3".to_string())
        }));
    }

    #[test]
    fn substitute_template_basic() {
        let mut combo = HashMap::new();
        combo.insert("layout".to_string(), "month".to_string());
        combo.insert("year".to_string(), "2026".to_string());

        let defaults = Defaults::default();

        let result = substitute_template("{layout}_{year}.pdf", &combo, &defaults).unwrap();
        assert_eq!(result, "month_2026.pdf");
    }

    #[test]
    fn substitute_template_with_defaults() {
        let combo = HashMap::new();
        let defaults = Defaults {
            year: Some(2026),
            layout: Some("big".into()),
            ..Default::default()
        };

        let result = substitute_template("{layout}_{year}.pdf", &combo, &defaults).unwrap();
        assert_eq!(result, "big_2026.pdf");
    }

    #[test]
    fn substitute_template_missing_var() {
        let combo = HashMap::new();
        let defaults = Defaults::default();

        let result = substitute_template("{unknown}.pdf", &combo, &defaults);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("unknown"));
    }

    #[test]
    fn value_to_string_converts_types() {
        assert_eq!(
            value_to_string(&serde_yml::Value::String("hello".into())),
            "hello"
        );
        assert_eq!(
            value_to_string(&serde_yml::Value::Number(serde_yml::Number::from(42))),
            "42"
        );
        assert_eq!(value_to_string(&serde_yml::Value::Bool(true)), "true");
    }
}
