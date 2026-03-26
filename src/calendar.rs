use chrono::{Datelike, NaiveDate, Weekday};

/// Iterate over every day in a month.
#[allow(dead_code)]
pub fn days_in_month(year: i32, month: u32) -> impl Iterator<Item = NaiveDate> {
    let first = NaiveDate::from_ymd_opt(year, month, 1).unwrap();
    let count = last_day_of_month(year, month) as usize;
    (0..count).map(move |d| first + chrono::Days::new(d as u64))
}

/// Iterate over a 12-month span starting at (year, month).
#[allow(dead_code)]
pub fn year_span(year: i32, start_month: u32) -> impl Iterator<Item = NaiveDate> {
    let first = NaiveDate::from_ymd_opt(year, start_month, 1).unwrap();
    let (end_year, end_month) = if start_month == 1 {
        (year, 12)
    } else {
        (year + 1, start_month - 1)
    };
    let end = NaiveDate::from_ymd_opt(end_year, end_month, last_day_of_month(end_year, end_month))
        .unwrap();
    let count = (end - first).num_days() as usize + 1;
    (0..count).map(move |d| first + chrono::Days::new(d as u64))
}

/// Check if a date falls on Saturday or Sunday.
pub fn is_weekend(date: NaiveDate) -> bool {
    matches!(date.weekday(), Weekday::Sat | Weekday::Sun)
}

/// Get the last day of a month (28, 29, 30, or 31).
pub fn last_day_of_month(year: i32, month: u32) -> u32 {
    let next = if month == 12 {
        NaiveDate::from_ymd_opt(year + 1, 1, 1)
    } else {
        NaiveDate::from_ymd_opt(year, month + 1, 1)
    };
    (next.unwrap() - chrono::Days::new(1)).day()
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Weekday;

    #[test]
    fn feb_non_leap() {
        let days: Vec<_> = days_in_month(2026, 2).collect();
        assert_eq!(days.len(), 28);
        assert_eq!(days[0], NaiveDate::from_ymd_opt(2026, 2, 1).unwrap());
        assert_eq!(days[27], NaiveDate::from_ymd_opt(2026, 2, 28).unwrap());
    }

    #[test]
    fn feb_leap() {
        let days: Vec<_> = days_in_month(2024, 2).collect();
        assert_eq!(days.len(), 29);
    }

    #[test]
    fn january_31_days() {
        let days: Vec<_> = days_in_month(2026, 1).collect();
        assert_eq!(days.len(), 31);
        assert_eq!(days[0].day(), 1);
        assert_eq!(days[30].day(), 31);
    }

    #[test]
    fn december_31_days() {
        let days: Vec<_> = days_in_month(2026, 12).collect();
        assert_eq!(days.len(), 31);
    }

    #[test]
    fn weekend_detection() {
        // 2026-03-21 is Saturday
        assert!(is_weekend(NaiveDate::from_ymd_opt(2026, 3, 21).unwrap()));
        // 2026-03-22 is Sunday
        assert!(is_weekend(NaiveDate::from_ymd_opt(2026, 3, 22).unwrap()));
        // 2026-03-23 is Monday
        assert!(!is_weekend(NaiveDate::from_ymd_opt(2026, 3, 23).unwrap()));
    }

    #[test]
    fn last_day_feb_non_leap() {
        assert_eq!(last_day_of_month(2026, 2), 28);
    }

    #[test]
    fn last_day_feb_leap() {
        assert_eq!(last_day_of_month(2024, 2), 29);
    }

    #[test]
    fn year_span_from_march() {
        let days: Vec<_> = year_span(2026, 3).collect();
        assert_eq!(days[0], NaiveDate::from_ymd_opt(2026, 3, 1).unwrap());
        let last = days.last().unwrap();
        assert_eq!(*last, NaiveDate::from_ymd_opt(2027, 2, 28).unwrap());
    }

    #[test]
    fn year_span_from_january() {
        let days: Vec<_> = year_span(2026, 1).collect();
        assert_eq!(days[0], NaiveDate::from_ymd_opt(2026, 1, 1).unwrap());
        let last = days.last().unwrap();
        assert_eq!(*last, NaiveDate::from_ymd_opt(2026, 12, 31).unwrap());
        assert_eq!(days.len(), 365);
    }

    #[test]
    fn is_weekend_saturday() {
        // Find a known Saturday: 2026-03-28
        let date = NaiveDate::from_ymd_opt(2026, 3, 28).unwrap();
        assert_eq!(date.weekday(), Weekday::Sat);
        assert!(is_weekend(date));
    }
}
