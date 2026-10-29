import statistics
import pandas as pd

data =  pd.read_csv("demo-loan.csv")
columns = data.columns.tolist()
def count_values(data,column):  # counts values in a columb
    values = data[column].dropna()
    return int(values.astype(str).str.strip().ne("").sum())
def count_columns(columns): #counts how many columbs their are
    return len(columns) if columns else 0

def name_columns(columns): # returns names of each column
    return columns if columns else []

def numerical_values(data, column): # returns only usable data from a colunm so calc functions dont break
    values = pd.to_numeric(data[column], errors="coerce")
    return values.dropna().tolist()
        
def calc_mean(data, column): #calculates the mean of a particular row of data
    values = numerical_values(data,column)
    if not values:
        return None
    return sum (values) / len(values)
def calc_range(data, column): #returns range of values
    values = numerical_values(data, column)
    if not values:
        return None
    return max(values) - min(values)
def calc_minimum(data, column): #returns mimimum value
    values = numerical_values(data,column)
    if not values:
        return None
    return min(values)
def calc_maximum(data, column): #returns maximum value
    values = numerical_values(data,column)
    if not values:
        return None
    return max(values)
def calc_standard_deviation(data, column): # returns standard deviation
    values = numerical_values(data, column)
    if len(values) < 2:
        return None
    return statistics.stdev(values)
def count_missing(data,column):
    values = data[column]
    return int((values.isna() | values.astype(str).str.strip().eq("")).sum())
def is_numerical(data, column):
    values = pd.to_numeric(data[column], errors="coerce")
    return values.notna().sum() > 0
def calc_total_loan_amount(data,column):
    values = numerical_values(data, column)
    if not values:
        return None
    return sum(values)
def calc_average_by_type(data):
    data = data.copy()
    data["loan_amount"] = pd.to_numeric(data["loan_amount"],errors = "coerce")
    average_by_type = data.groupby("loan_type")["loan_amount"].mean()
    return average_by_type
def calc_average_ltv_by_occupancy(data):
    data = data.copy()
    data["ltv_ratio"] = pd.to_numeric(data["ltv_ratio"], errors="coerce")
    average_ltv = data.groupby("occupancy_type")["ltv_ratio"].mean()
    return average_ltv
def calc_pull_through_by_officer(data):
    data = data.copy()

    funded = data["funding_date"].notna() & (
        data["funding_date"].astype(str).str.strip() != ""
    )

    data["funded"] = funded

    pull_through = data.groupby("loan_officer").agg(
        total_loans=("funded", "size"),
        funded_loans=("funded", "sum")
    )

    pull_through["pull_through_rate"] = (
        pull_through["funded_loans"] / pull_through["total_loans"] * 100
    )

    return pull_through
def generate_report(data):
    columns = data.columns.tolist()
    docu = []
    docu.append(("Total loan records", len(data)))
    docu.append(("Total columns", count_columns(columns)))
    docu.append(("Total loan amount", calc_total_loan_amount(data, "loan_amount")))
    for column in columns:
        if is_numerical(data, column):
                docu.append((f"{column} - Mean", calc_mean(data, column)))
                docu.append((f"{column} - Range", calc_range(data, column)))
                docu.append((f"{column} - Minimum", calc_minimum(data, column)))
                docu.append((f"{column} - Maximum", calc_maximum(data, column)))
                docu.append((
                    f"{column} - Standard deviation",
                    calc_standard_deviation(data, column)
                ))
    for column in columns:
        docu.append((f"{column} - Valid entries", count_values(data, column)))
        docu.append((f"{column} - Missing entries", count_missing(data, column)))

    for column in columns:
        docu.append((f"{column} - Valid entries", count_values(data, column)))
        docu.append((f"{column} - Missing entries", count_missing(data, column)))   

    for loan_type, average in calc_average_by_type(data).items():
        docu.append((f"Average loan amount - {loan_type}", average))

    for occupancy, average in calc_average_ltv_by_occupancy(data).items():
        docu.append((f"Average LTV - {occupancy}", average))

    pull_through = calc_pull_through_by_officer(data)
    for officer, result in pull_through.iterrows():
        docu.append((f"{officer} - Total loans", result["total_loans"]))
        docu.append((f"{officer} - Funded loans", result["funded_loans"]))
        docu.append((
            f"{officer} - Pull-through rate",
            f"{result['pull_through_rate']:.2f}%"
        ))
    rows = ""
    for name, result in docu:
        if result is None or pd.isna(result):
            result = "N/A"
        elif isinstance(result, (int, float)):
            result = f"{result:,.2f}"

        rows += f"<tr><td>{name}</td><td>{result}</td></tr>"

    html = f""" 
    <html>
    <head>
        <title>CSV Analysis Report</title>
    </head>
    <body>
        <h1>CSV Analysis Report</h1>
        <table border="1" cellpadding="6">
            <tr><th>Statistic</th><th>Result</th></tr>
            {rows}
        </table>
    </body>
    </html>
    """
    with open("report.html", "w", encoding="utf-8") as file:
        file.write(html)
generate_report(data)
print("your report is ready: report.html")