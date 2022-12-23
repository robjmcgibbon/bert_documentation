Scripts to automatically generate the SWIFT output list from the data in the
COLIBRE spreadsheet, and to check that the snapshot actually matches that
output list (since variables missing from the output list are always output,
without lossy compression).

The procedure works as follows:
 1. Copy the contents of the 4 particle type specific blocks in the COLIBRE
    spreadsheet into text files called `Gas.txt`, `DM.txt`, `Stars.txt` and
    `BH.txt`. Do not copy any of the headers or footers of the table. Copy-paste
    will separate the columns with tab characters; that is what we want.
    If running with globular clusters, make sure to delete the duplicate
    `TidalTensors` field (do not remove the duplicate from the normal star
    fields table; that will omit it from the output list if not running with
    globular clusters, which means the tidal tensores will be output, without
    any lossy compression).
 2. Run `make_output_list.py`. This will convert the `.txt` file information
    into a file called `colibre_default_output_list.yml` that is compatible
    with SWIFT.
 3. Run a SWIFT simulation using this output list.
 4. Run `generate_output_report.py` on a snapshot of this run. This will
    create another `.yml` file with relevant information about the datasets
    in the snapshot file.
 5. Run `check_output.py`. This script will use information from the `.txt`
    files and the `.yml` file produced in step 4 to check if the snapshot
    matches the expectations from the table. Any quantities that are wrongly
    output, missing in the snapshot or output with the wrong type or compression
    are flagged.
