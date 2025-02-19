import pandas as pd
import rpy2.robjects as robjects


def run_r_script(r_file, y_data, x_data, new_x):
    with open(r_file, "r") as file:
        r_code = file.read()

    # Load R script
    robjects.r(r_code)

    # Assuming the R script defines a function named 'process_data'
    r_func = robjects.globalenv['process_data']

    # Convert inputs into R-compatible formats
    y_vector = robjects.FloatVector(y_data)
    x_vector = robjects.FloatVector(x_data)
    new_x_vector = robjects.FloatVector(new_x)

    # Call R function
    result = r_func(y_vector, x_vector, new_x_vector)

    # Convert result to dictionary
    result_dict = {name: str(result[i]) for i, name in enumerate(result.names)}

    return result_dict


def clean_output(result_dict):
    cleaned_results = {}

    for key, value in result_dict.items():
        clean_value = value.replace('[1]', '').replace("\\n", "\n")
        clean_value = clean_value.split("\n")

        cleaned_results[key.upper()] = clean_value

    return cleaned_results


if __name__ == "__main__":
    r_script_path = "analysis_files/testing_josh_analysis.R"  # Replace with your R script path

    # Reading file into usable data
    df = pd.read_csv("some_data.txt", delim_whitespace=True, header=None, names=["x", "y"])
    y_values = df["y"].tolist()
    x_values = df["x"].tolist()

    new_x_values = [30]  # New value for prediction

    output = run_r_script(r_script_path, y_values, x_values, new_x_values)
    nice_output = clean_output(output)

    # Print formatted output
    for key, value in nice_output.items():
        print("========", key, "========")
        print("\n".join(value))
