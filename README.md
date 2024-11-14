# Homology Data Fetcher

This script fetches homology information for a list of gene IDs from the Ensembl REST API. The input gene IDs are read from an Excel file, and the output is written to a CSV file. The script can be customized to fetch various types of homology information and sequences (e.g., orthologue, paralogues, protein sequences).

## Prerequisites

Before running this script, ensure you have the following installed on your system:

1. Python 3.x
2. Required Python libraries:

```bash
pip install pandas numpy requests argparse openpyxl
```

The `openpyxl` library is needed to read and write Excel files.

## Usage

### Command-Line Arguments

The script takes several command-line arguments to customize the input, output, and the type of data fetched from the Ensembl API. Here is a breakdown of the arguments:

- **file** (required): Path to the input Excel file that contains a list of gene IDs.
- **species** (required): Species for the homology search (e.g., "human", "mouse").
- **out** (required): Path to the output file where the CSV results will be saved.
- **--tspecies** (optional): Species of homology to return. You can specify types like `mus_musculus` or `homo_sapiens`.
- **--type** (optional): Type of homology to return (default: `orthologs`). You can specify types like `orthologue`, `paralogues` or `projections`.
- **--sequence** (optional): Type of sequence to retrieve (default: `none`). Other options include `cdna` or `none`.

### Input File

The input Excel file should contain at least one sheet named `Sheet1` with a column named `gene_ids` listing gene IDs for which homology information will be fetched.

### Example Excel File Format (Sheet1):

| gene_ids  |
|-----------|
| ENSG00000139618 |
| ENSG00000268895 |
| ENSG00000157764 |
| ENSG00000248378 |

### Running the Script

Once you have the input Excel file ready, you can run the script using the following command:

```bash
cd src
python ensembl_rest.py ../data/find_paralogue_humans.xlsx homo_sapiens output.csv --type paralogues 
```

#### Example Breakdown:

- `file.xlsx`: Path to the Excel file containing gene IDs.
- `human`: The target species for the homology search (e.g., for searching human genes).
- `output.csv`: Path to save the output CSV file with the results.
- `--type paralogues`: Specifies that the script will fetch paralogous genes.
- `--sequence protein`: Specifies that the script will fetch protein sequences.

### Output

The output file will be a CSV that contains the following columns added to `Sheet1`:

- **Count**: The number of homologous genes found for each gene ID.
- **<homology_type>**: A column named after the homology type specified (e.g., paralogues), containing a comma-separated list of homologous gene IDs.

### Example Output CSV Format:

| gene_ids       | Count | paralogues          |
|----------------|-------|---------------------|
| ENSG00000139618 | 2     | ENSP00000369497,ENSP00000369498 |
| ENSG00000268895 | 0     |                     |
| ENSG00000157764 | 1     | ENSP00000256079     |
| ENSG00000248378 | 0     |                     |

## Error Handling

The script handles common errors such as:

- HTTP errors (e.g., bad API responses)
- Connection issues
- Timeout errors

For each error, the script will print an error message and continue processing the remaining gene IDs.
