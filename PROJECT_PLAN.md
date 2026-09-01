# Uber Mobility Intelligence & Booking Prediction System

## 1. Business Problem
Diagnosing ride fulfillment bottlenecks (No Driver Found, Customer & Driver Cancellations) across Delhi NCR to optimize dispatch efficiency and customer retention.

## 2. Target Variable & Leakage Rule
* **Target:** `Booking Status` (Multi-class: Completed, Cancelled by Driver, Cancelled by Customer, No Driver Found, Incomplete)
* **Prediction Point (T0):** The moment a rider hits "Book Ride".
* **Leakage Guard:** Strictly ban post-booking attributes (`Ride Distance`, `Booking Value`, `Driver Ratings`, `Customer Rating`, `Payment Method`, `Cancellation Reasons`) from ML prediction inputs.

## 3. Tech Stack
* **Storage & Queries:** PostgreSQL
* **Analysis & Modeling:** Python (Pandas, Scikit-Learn, XGBoost, SHAP)
* **BI & Storytelling:** Microsoft Power BI
* **App Layer:** Streamlit

## 4. Execution Phases
1. Phase 1: Data Understanding & Initial Profiling
2. Phase 2: Data Quality & Business Rules Validation
3. Phase 3: Context-Aware Data Cleaning
4. Phase 4 & 5: PostgreSQL Database & Business SQL Analysis
5. Phase 6 & 7: Exploratory Data Analysis & Strategic Insights
6. Phase 8: Feature Engineering & Leakage Audit
7. Phase 9: Power BI Executive Dashboard
8. Phase 10 - 13: Multi-Class ML Engine & Interpretability (SHAP)
9. Phase 14: Customer Behavioral Segmentation (RFM + Completion)
10. Phase 15 & 16: Location Intelligence & Operations Strategy
11. Phase 17: Streamlit Production App
12. Phase 18 - 20: GitHub, Documentation & Portfolio Showcase