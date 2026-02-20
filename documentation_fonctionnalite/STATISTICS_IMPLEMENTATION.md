# Statistics and Reports Implementation

## Overview

The statistics and reports feature provides comprehensive analytics and reporting capabilities for the payroll system. It includes various endpoints for analyzing payroll data, comparing periods, tracking employee history, and generating dashboard summaries.

## Service: StatisticsService

Location: `app/paie_app/services/statistics_service.py`

### Methods

#### 1. `get_period_summary(periode_id: int)`
Get comprehensive summary for a specific payroll period.

**Returns:**
- Period details (year, month, status, dates)
- Number of employees
- Total gross and net payroll
- Employer and employee contributions
- Total deductions
- Total employer cost
- Average salaries

#### 2. `get_annual_summary(annee: int)`
Get annual payroll summary with monthly breakdown.

**Returns:**
- Annual totals (gross, net, contributions)
- Monthly averages
- Monthly data breakdown
- Total employer cost for the year

#### 3. `get_employee_payroll_history(employe_id: int, annee: Optional[int], limit: int)`
Get payroll history for a specific employee.

**Parameters:**
- `employe_id`: Employee ID
- `annee`: Optional year filter
- `limit`: Maximum number of periods to return (default: 12)

**Returns:**
- Employee ID
- Number of periods
- Historical data (period, salaries, contributions, deductions)
- Totals and averages

#### 4. `get_deductions_summary(employe_id: Optional[int], type_retenue: Optional[str])`
Get summary of employee deductions.

**Parameters:**
- `employe_id`: Optional employee filter
- `type_retenue`: Optional deduction type filter

**Returns:**
- Number of active deductions
- Total monthly deductions
- Total already deducted
- Total remaining
- Breakdown by deduction type

#### 5. `get_alerts_summary(periode_id: Optional[int], severity: Optional[str], status: Optional[str])`
Get summary of payroll alerts.

**Parameters:**
- `periode_id`: Optional period filter
- `severity`: Optional severity filter
- `status`: Optional status filter

**Returns:**
- Total alerts
- Breakdown by severity
- Breakdown by status
- Breakdown by type

#### 6. `get_comparative_analysis(annee: int, mois: int, compare_to_previous: bool)`
Compare current period with previous period or same month last year.

**Parameters:**
- `annee`: Year
- `mois`: Month
- `compare_to_previous`: True for previous month, False for same mon
ault: 10)

**Returns:**
- List of top earners with salaries
- For period: individual period data
- For year: annual totals and averages

#### 8. `get_dashboard_summary(annee: Optional[int], mois: Optional[int])`
Get comprehensive dashboard summary.

**Parameters:**
- `annee`: Optional year (defaults to current year)
- `mois`: Optional month (defaults to current month)

**Returns:**
- Current period summary
- Active alerts summary
- Active deductions summary
- Top 5 earners
- Annual summary

## API Endpoints

All endpoints are under the `/statistics` prefix and require `payroll.view` permission (except deductions and alerts which use their respective permissions).

### 1. GET `/statistics/periode/{periode_id}/summary`
Get comprehensive summary for a specific payroll period.

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/periode/1/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "periode_id": 1,
  "annee": 2024,
  "mois": 2,
  "statut": "APPROVED",
  "date_debut": "2024-02-01",
  "date_fin": "2024-02-29",
  "nombre_employes": 50,
  "masse_salariale_brute": 125000.00,
  "masse_salariale_nette": 95000.00,
  "total_cotisations_patronales": 18750.00,
  "total_cotisations_salariales": 12500.00,
  "total_retenues": 5000.00,
  "cout_total_employeur": 143750.00,
  "moyenne_salaire_brut": 2500.00,
  "moyenne_salaire_net": 1900.00
}
```

### 2. GET `/statistics/annual/{annee}/summary`
Get annual payroll summary.

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/annual/2024/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "annee": 2024,
  "nombre_periodes": 12,
  "masse_salariale_brute_annuelle": 1500000.00,
  "masse_salariale_nette_annuelle": 1140000.00,
  "total_cotisations_patronales_annuelles": 225000.00,
  "total_cotisations_salariales_annuelles": 150000.00,
  "cout_total_employeur_annuel": 1725000.00,
  "moyenne_mensuelle_brute": 125000.00,
  "moyenne_mensuelle_nette": 95000.00,
  "donnees_mensuelles": [
    {
      "mois": 1,
      "masse_salariale_brute": 125000.00,
      "masse_salariale_nette": 95000.00,
      "nombre_employes": 50
    }
  ]
}
```

### 3. GET `/statistics/employee/{employe_id}/history`
Get payroll history for a specific employee.

**Query Parameters:**
- `annee` (optional): Filter by year
- `limit` (optional): Maximum number of periods (default: 12, max: 24)

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/employee/123/history?annee=2024&limit=12" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "employe_id": 123,
  "nombre_periodes": 12,
  "historique": [
    {
      "periode_id": 12,
      "annee": 2024,
      "mois": 12,
      "salaire_base": 2000.00,
      "salaire_brut": 2500.00,
      "salaire_net": 1900.00,
      "cotisations_salariales": {...},
      "retenues_diverses": {...}
    }
  ],
  "total_brut": 30000.00,
  "total_net": 22800.00,
  "moyenne_brute": 2500.00,
  "moyenne_nette": 1900.00
}
```

### 4. GET `/statistics/deductions/summary`
Get summary of employee deductions.

**Query Parameters:**
- `employe_id` (optional): Filter by employee
- `type_retenue` (optional): Filter by deduction type

**Permission Required:** `retenue.view`

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/deductions/summary?employe_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "nombre_retenues_actives": 5,
  "total_mensuel": 500.00,
  "total_deja_deduit": 2000.00,
  "total_restant": 3000.00,
  "par_type": {
    "PRET": {
      "count": 2,
      "total_monthly": 300.00,
      "total_deducted": 1200.00,
      "total_remaining": 1800.00
    },
    "AVANCE": {
      "count": 3,
      "total_monthly": 200.00,
      "total_deducted": 800.00,
      "total_remaining": 1200.00
    }
  }
}
```

### 5. GET `/statistics/alerts/summary`
Get summary of payroll alerts.

**Query Parameters:**
- `periode_id` (optional): Filter by period
- `severity` (optional): Filter by severity
- `status` (optional): Filter by status

**Permission Required:** `alert.view`

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/alerts/summary?status=ACTIVE" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_alertes": 15,
  "par_severite": {
    "HIGH": 3,
    "MEDIUM": 8,
    "LOW": 4
  },
  "par_statut": {
    "ACTIVE": 10,
    "RESOLVED": 5
  },
  "par_type": {
    "MISSING_DATA": 5,
    "CALCULATION_ERROR": 3,
    "VALIDATION_WARNING": 7
  }
}
```

### 6. GET `/statistics/comparative/{annee}/{mois}`
Compare current period with previous period or same month last year.

**Query Parameters:**
- `compare_to_previous` (optional): True for previous month, False for same month last year (default: True)

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/comparative/2024/2?compare_to_previous=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "periode_actuelle": {
    "annee": 2024,
    "mois": 2,
    "donnees": {...}
  },
  "periode_comparaison": {
    "annee": 2024,
    "mois": 1,
    "donnees": {...}
  },
  "comparaison_disponible": true,
  "differences": {
    "nombre_employes": {
      "valeur": 2,
      "pourcentage": 4.17
    },
    "masse_salariale_brute": {
      "valeur": 5000.00,
      "pourcentage": 4.17
    },
    "masse_salariale_nette": {
      "valeur": 3800.00,
      "pourcentage": 4.17
    },
    "cotisations_patronales": {
      "valeur": 750.00,
      "pourcentage": 4.17
    },
    "cotisations_salariales": {
      "valeur": 500.00,
      "pourcentage": 4.17
    }
  }
}
```

### 7. GET `/statistics/top-earners`
Get top earners for a period or year.

**Query Parameters:**
- `periode_id` (optional): Period ID for single period analysis
- `annee` (optional): Year for annual analysis
- `limit` (optional): Maximum number of results (default: 10, max: 50)

**Note:** Either `periode_id` or `annee` must be provided.

**Example (by period):**
```bash
curl -X GET "http://localhost:8000/statistics/top-earners?periode_id=1&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "employe_id": 45,
    "salaire_brut": 5000.00,
    "salaire_net": 3800.00,
    "periode_id": 1
  },
  {
    "employe_id": 23,
    "salaire_brut": 4500.00,
    "salaire_net": 3420.00,
    "periode_id": 1
  }
]
```

**Example (by year):**
```bash
curl -X GET "http://localhost:8000/statistics/top-earners?annee=2024&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "employe_id": 45,
    "total_brut": 60000.00,
    "total_net": 45600.00,
    "nombre_periodes": 12,
    "moyenne_brute": 5000.00,
    "moyenne_nette": 3800.00
  }
]
```

### 8. GET `/statistics/dashboard`
Get comprehensive dashboard summary.

**Query Parameters:**
- `annee` (optional): Year (defaults to current year)
- `mois` (optional): Month (defaults to current month)

**Example:**
```bash
curl -X GET "http://localhost:8000/statistics/dashboard?annee=2024&mois=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "annee": 2024,
  "mois": 2,
  "periode_actuelle": {
    "periode_id": 2,
    "nombre_employes": 50,
    "masse_salariale_brute": 125000.00,
    ...
  },
  "alertes": {
    "total_alertes": 5,
    "par_severite": {...},
    "par_statut": {...},
    "par_type": {...}
  },
  "retenues_actives": {
    "nombre_retenues_actives": 15,
    "total_mensuel": 5000.00,
    ...
  },
  "top_earners": [
    {
      "employe_id": 45,
      "salaire_brut": 5000.00,
      ...
    }
  ],
  "resume_annuel": {
    "annee": 2024,
    "masse_salariale_brute_annuelle": 250000.00,
    ...
  }
}
```

## Permissions

The statistics endpoints use the following permissions:

- **Period, Annual, Employee, Comparative, Top Earners, Dashboard**: `payroll.view`
- **Deductions Summary**: `retenue.view`
- **Alerts Summary**: `alert.view`

## Use Cases

### 1. Management Dashboard
Use the `/statistics/dashboard` endpoint to display a comprehensive overview of the current payroll status, including active alerts, deductions, and top earners.

### 2. Period Analysis
Use `/statistics/periode/{periode_id}/summary` to analyze a specific payroll period and verify calculations.

### 3. Annual Reporting
Use `/statistics/annual/{annee}/summary` to generate annual reports for accounting and budgeting purposes.

### 4. Employee Salary History
Use `/statistics/employee/{employe_id}/history` to review an employee's salary history for performance reviews or audits.

### 5. Trend Analysis
Use `/statistics/comparative/{annee}/{mois}` to identify trends and changes in payroll costs over time.

### 6. Deduction Tracking
Use `/statistics/deductions/summary` to monitor active deductions and remaining balances.

### 7. Alert Monitoring
Use `/statistics/alerts/summary` to track and manage payroll alerts by severity and status.

### 8. Compensation Analysis
Use `/statistics/top-earners` to analyze compensation distribution and identify high earners.

## Integration with Audit System

All statistics endpoints are automatically audited through the existing audit middleware. The following actions are logged:

- Viewing period summaries
- Generating annual reports
- Accessing employee history
- Viewing deduction summaries
- Accessing alert summaries
- Running comparative analyses
- Viewing top earners
- Accessing dashboard

## Performance Considerations

1. **Caching**: Consider implementing caching for frequently accessed statistics (e.g., dashboard, annual summaries)
2. **Pagination**: Employee history and top earners support limit parameters to control result size
3. **Filtering**: Use query parameters to filter results and reduce data transfer
4. **Async Operations**: All database operations are asynchronous for better performance

## Future Enhancements

Potential improvements for the statistics feature:

1. **Export to Excel/PDF**: Add export capabilities for statistics reports
2. **Scheduled Reports**: Implement automated report generation and email delivery
3. **Custom Date Ranges**: Support custom date range queries
4. **Graphical Data**: Add endpoints that return data formatted for charts and graphs
5. **Predictive Analytics**: Implement forecasting based on historical data
6. **Department-level Statistics**: Add department-based filtering and analysis
7. **Real-time Updates**: Implement WebSocket support for live dashboard updates
8. **Custom Metrics**: Allow users to define custom KPIs and metrics

## Testing

To test the statistics endpoints:

1. Ensure you have payroll data in the database (periods, entries, deductions, alerts)
2. Obtain a valid authentication token with appropriate permissions
3. Use curl, Postman, or any HTTP client to call the endpoints
4. Verify the returned data matches expected calculations

Example test sequence:
```bash
# 1. Get dashboard summary
curl -X GET "http://localhost:8000/statistics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Get period summary
curl -X GET "http://localhost:8000/statistics/periode/1/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Get annual summary
curl -X GET "http://localhost:8000/statistics/annual/2024/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Get comparative analysis
curl -X GET "http://localhost:8000/statistics/comparative/2024/2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Common Issues

1. **404 Not Found**: Ensure the period/employee exists in the database
2. **403 Forbidden**: Verify the user has the required permissions
3. **400 Bad Request**: Check query parameters are valid
4. **500 Internal Server Error**: Check database connection and data integrity

### Debug Tips

- Enable debug logging to see SQL queries
- Use the audit log to track API access
- Verify data exists before running statistics queries
- Check for null values in calculations

---

**Implementation Date**: 2024-02-17
**Status**: ✅ COMPLETE
