import ensembl_rest
import pandas as pd
import requests, sys
import numpy as np
import re
import argparse


def load_excel_file(file_name):
    """
    Load an Excel file with multiple sheets into a dictionary of DataFrames.
    
    :param file_name: str - Path to the Excel file
    :return: dict - Dictionary where the key is the sheet name and the value is the corresponding DataFrame
    """

    xls = pd.ExcelFile(file_name)

    dfs = pd.read_excel(file_name, sheet_name=None)
    return dfs


def write_excel_file(dfs, result, stype, out_file):
    """
    Write results into an existing DataFrame from an Excel sheet and save it as a CSV file.
    
    :param dfs: dict - Dictionary of DataFrames
    :param result: list - List of results containing homologous gene data
    :param stype: str - Type of homology
    :param out_file: str - Path to save the output CSV file
    """
    # Add the 'Count' column in the DataFrame from the result array
    dfs['Sheet1']["Count"] = np.array(result)[:,0]
    # Add the column for the homology type from the result array
    dfs['Sheet1'][stype] = np.array(result)[:,1]
    # Save the modified DataFrame to a CSV file
    dfs['Sheet1'].to_csv(out_file, sep=',')
    return 0


def process_result_data(decoded, species, tspecies):
    """
    Process and extract relevant homology data from the API response.
    
    :param decoded: dict - Decoded JSON response from Ensembl API
    :param tspecies: str - Target species for homology
    :return: list - List containing the count of homologs and a string of homolog gene IDs
    """
    # Check if data and homologies exist in the response
    if decoded["data"] and decoded["data"][0] and decoded["data"][0]['homologies']:
        homos = decoded["data"][0]['homologies']  # Get homologies
        para_count = len(homos)  # Count the number of homologs

        paras = []  # List to store homolog gene IDs
        if para_count > 0:
            for p in homos:
                para = p['target']  # Get target gene from homology
                # Only consider homologies that match the target species
                if para['species'] != tspecies:
                    continue
                paras.append(para['id'])  # Append homolog gene ID
            paras_str = ','.join(paras)  # Join homolog gene IDs as a comma-separated string
        else:
            para_count = 0
            paras_str = ''
    else:
        para_count = 0
        paras_str = ''
    return [para_count, paras_str]  # Return count and homolog gene IDs




def fetch_data_from_ensembl(dfs, species, tspecies, stype, sequence):
    """
    Fetch homology data for each gene in the input Excel file using the Ensembl REST API.
    
    :param dfs: dict - Dictionary of DataFrames
    :param tspecies: str - Target species for homology
    :param stype: str - Type of homology (e.g., paralogues)
    :param sequence: str - Type of sequence (e.g., protein)
    :return: list - List of results containing homology count and homolog gene IDs
    """
    genes = dfs['Sheet1']['gene_ids']  # Get gene IDs from the Excel sheet
    server = "https://rest.ensembl.org"  # Base URL for the Ensembl REST API

    result = []  # List to store results
    c = 0  # Counter for processed genes
    for gene in genes:
        if isinstance(gene, str):  # Ensure the gene ID is a string
            ext = "/homology/id/"  # API endpoint for homology
            ext += species + "/" + gene + "?type=" + stype + ";sequence=" + sequence  # Construct the API URL

            if (tspecies):
                ext += ";target_species=" + tspecies
            
            # Make the API request
            try:
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                r.raise_for_status()  # Raise an error for bad HTTP responses
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred for gene {gene}: {http_err}")
            except requests.exceptions.ConnectionError as conn_err:
                print(f"Connection error occurred for gene {gene}: {conn_err}")
            except requests.exceptions.Timeout as timeout_err:
                print(f"Timeout occurred for gene {gene}: {timeout_err}")
            except requests.exceptions.RequestException as req_err:
                print(f"An error occurred for gene {gene}: {req_err}")
            except Exception as e:
                print(f"An unexpected error occurred for gene {gene}: {e}")
            else:
                # If the API request is successful, process the result data
                print(c, gene, "is processed successfully")
                data = r.json()  # Decode the JSON response
                target_genes = process_result_data(data, species, tspecies)  # Process the response to get homolog gene info
                result.append(target_genes)  # Add the result to the list

            c += 1  # Increment the counter for processed genes
    return result  # Return the list of results


def main():
    # Setting up argument parsing
    parser = argparse.ArgumentParser(description="Fetch  homology information for gene IDs from an Excel file.")
    
    # Required argument: the Excel file path
    parser.add_argument("file", help="Path to the Excel file containing gene IDs.")
    
    # Required argument: name of target species of the result genes
    parser.add_argument("species", help="Species of the input genes.")

    # Required argument: the name of output Excel file path
    parser.add_argument("out", help="Path to the output Excel file.")

    # Optional argument: the type of homology to return from this call Enum(orthologues, paralogues, projections, all). 
    parser.add_argument("--type", default="orthologues", help="Type of homology.")

    # Optional argument: target species of the output genes. 
    parser.add_argument("--tspecies", help="Target species of the output genes.")

    # Optional argument: the type of sequence to bring back (none, cdna, protein). 
    parser.add_argument("--sequence", default="none", help="Type of homology.")
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Load Excel file
    gene_data = load_excel_file(args.file)

    # Fetch the required data from ensembl
    result = fetch_data_from_ensembl(gene_data, args.species, args.tspecies, args.type, args.sequence)

    # Write the results to the output file
    write_excel_file(gene_data, result, args.type, args.out)


if __name__ == "__main__":
    main()
