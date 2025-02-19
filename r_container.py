import os
import re

import pandas as pd
import rpy2.robjects as robjects


class RAnalysisContainer:
    def __init__(self, r_script_path):
        """
        Initializes the container with the path to the R script and extracts input argument names.
        :param r_script_path: Path to the R script to be executed.
        """
        if not os.path.exists(r_script_path):
            raise FileNotFoundError(f"R script not found: {r_script_path}")

        self.r_script_path = os.path.normpath(r_script_path)
        self.input_keys = self._extract_function_arguments()

    def run(self, **inputs):
        """
        Runs the R script with the given input data.
        :param inputs: Keyword arguments matching the expected input keys.
        :return: Cleaned results dictionary.
        """
        if set(inputs.keys()) != set(self.input_keys):
            raise ValueError(f"Expected inputs: {self.input_keys}, but got: {list(inputs.keys())}")

        result = self._run_r_script(inputs)
        return self._clean_output(result)

    def _run_r_script(self, inputs):
        try:
            with open(self.r_script_path, "r") as file:
                r_code = file.read()
        except Exception as e:
            raise RuntimeError(f"Error reading R script: {e}")

        try:
            # Load R script
            robjects.r(r_code)

            # Extract function name dynamically
            function_name = "process_data"  # Assuming the function is named process_data
            r_func = robjects.globalenv[function_name]

            # Convert inputs into R-compatible formats
            r_inputs = [self._convert_to_r_type(inputs[key]) for key in self.input_keys]

            # Call R function
            result = r_func(*r_inputs)

            # Handle NULLType result
            if not hasattr(result, 'names') or result.names is None:
                raise ValueError(
                    "R function did not return a named list. Ensure the function returns a list with named elements.")

            # Convert result to dictionary
            return {name: str(result[i]) for i, name in enumerate(result.names)}
        except Exception as e:
            raise RuntimeError(f"Error executing R function: {e}")

    def _convert_to_r_type(self, value):
        """
        Converts Python data types into R-compatible types.
        """
        if isinstance(value, list) and all(isinstance(v, (int, float)) for v in value):
            return robjects.FloatVector(value)
        elif isinstance(value, list) and all(isinstance(v, str) for v in value):
            return robjects.StrVector(value)
        elif isinstance(value, str):
            return robjects.StrVector([value])
        else:
            raise TypeError(f"Unsupported input type: {type(value)}")

    def _extract_function_arguments(self):
        """
        Extracts function argument names from the R script.
        :return: List of argument names.
        """
        with open(self.r_script_path, "r") as file:
            r_code = file.read()

        match = re.search(r'process_data\s*<-\s*function\((.*?)\)', r_code)
        if match:
            args = match.group(1).split(',')
            return [arg.strip() for arg in args]
        else:
            raise ValueError("Could not extract function arguments from R script.")

    def _clean_output(self, result_dict):
        """
        Cleans and formats the output from the R script.
        :param result_dict: Dictionary of raw R script results.
        :return: Dictionary with cleaned and formatted values.
        """
        cleaned_results = {}

        for key, value in result_dict.items():
            clean_value = value.replace('[1]', '').replace("\\n", "\n")
            clean_value = clean_value.split("\n")
            cleaned_results[key.upper()] = clean_value

        return cleaned_results


if __name__ == "__main__":
    r_script_path = "analysis_files/testing_josh_analysis.R"

    container = RAnalysisContainer(r_script_path)

    # output = container.run(data="hello")

    # Get input data
    df = pd.read_csv("some_data.txt", sep='\s+', header=None, names=["x", "y"])
    y_values = df["y"].tolist()
    x_values = df["x"].tolist()
    new_x_values = [30]

    output = container.run(y=y_values, x=x_values, new_x=new_x_values)

    # Combine formatted output string
    full_result_string = ""
    for key, value in output.items():
        full_result_string += f"======== {key} ========\n"
        section_string = '\n'.join(value)
        full_result_string += f"{section_string}\n"

    # Write to file
    with open("container_results.txt", "w") as f:
        f.write(full_result_string)
    print("Results written to container_results.txt")
