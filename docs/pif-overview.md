# PIF (Patient Intake Form) - Overview


## Install Dependencies

From your python environment, run the following:

`pip install mysql-connector-python`

Ensure your system is running in Canadian locale "en_CA.UTF-8" and "LANGUAGE=en_CA:en":

```
locale
locale d_fmt
localctl
timedatectl
```

To change locale:

```
sudo local-gen "en_CA.UTF-8"
sudo dpkg-reconfigure locals
(choose en_CA.UTF-8)
sudo update-locale LANGUAGE=en_CA:en
sudo localectl set-locale LANG=en_CA.UTF-8
(reboot the server for changes to take effect)
```

## Configuration Update

### Note on EMR DOB Picker Format

**Note:** For demographic creation, the EMR DOB picker may vary depending on the system configuration. The expected format for the EMR DOB picker is `dd-mm-yyyy`.

Please set your system language so that the EMR DOB picker uses the `dd-mm-yyyy` format.

**Example:**
`LANGUAGE=en_CA:en`

Update your AIMOA configuration based on your requirements.

## workflow-config-pif.yaml
In your `workflow-config-pif.yaml` file, add the following workflow to configure AIMOA with PIF

```yaml

workflow:
  steps:
    - name: query_pif
      true_next: exit
      false_next: exit

```

## config-pif.yaml
*Note: All fields are mandatory*

In your `config-pif.yaml` file, use the following fields to configure AIMOA with PIF

### `aimee_uid`
- **Type**: Integer  
- **Description**: Unique identifier for the user AIMOA for initiating the PIF process.  
- **Example**: `999998`

### `batch_size`
- **Type**: Integer  
- **Description**: The number of PIF records to be processed in one batch. This controls how many patient records will be handled at a time during the process.  
- **Example**: `50`

### `last_processed`
- **Type**: Integer  
- **Description**: Keeps track of the last processed PIF record ID. This is useful for continuing processing from where it was last left off in case of an interruption.  
- **Example**: `0`

### `confidential_unattached_id`
- **Type**: Integer  
- **Description**: A unique identifier used for creating a tickler notificaitons with AIMOA. This should be a demographic number.
- **Example**: `100`

### `error_msg_to`
- **Type**: Integer  
- **Description**: The identifier to whom error messages are sent when an issue occurs during PIF processing.  
- **Example**: `999998`

### `error_tickler_max_count`
- **Type**: Integer  
- **Description**: Maximum error count for stopping PIF processing
- **Example**: `5`

### `notify_row_count`
- **Type**: Integer  
- **Description**: Limit after which a notification is sent
- **Example**: `50`

### `exception_provider`
- **Type**: List of Strings  
- **Description**: A list of healthcare providers who are exceptions and should be treated differently when processing PIF records. Each entry in the list typically represents a combination of a provider's last name and first name.  
- **Example**:
  ```yaml
  - lastname, firstname
  ```

### `database`
- **Type**: String  
- **Description**: The name of the database used for storing and retrieving patient data for PIF processing.  
- **Example**: `test_db`


### `host`
- **Type**: String  
- **Description**: The IP address or hostname of the server where the database is hosted.  
- **Example**: `192.168.1.1`

### `table_name`
- **Type**: String  
- **Description**: The name of the table in the database where PIF records are stored.  
- **Example**: `test_table`

### `username`
- **Type**: String  
- **Description**: The username used for authenticating with the database.  
- **Example**: `test`

### `password`
- **Type**: String  
- **Description**: The password associated with the username for authenticating against the database.  
- **Example**: `test`

### `port`
- **Type**: Integer  
- **Description**: The port number used to connect to the database.  
- **Example**: `3306`

The above configuration applies when AIMOA is installed in the same environment as the PIF database.
If the PIF database is hosted in a different environment, it is recommended to use SSL for the database connection.
To enable this, use the following fields (pif_db_encrypt, ssl_ca,ssl_cert, ssl_key, ssl_verify_cert).

### `pif_db_encrypt`
- **Type**: Boolean  
- **Description**: Enable SSL for the database connection.
- **Example**: `false`

### `ssl_ca`
- **Type**: String  
- **Description**: Path to the ca.pem file.  
- **Example**: `./ca.pem`

### `ssl_cert`
- **Type**: String  
- **Description**: Path to the client-cert.pem file.  
- **Example**: `./client-cert.pem`

### `ssl_key`
- **Type**: String  
- **Description**: Path to the client-key.pem file.  
- **Example**: `./client-key.pem`

### `ssl_verify_cert`
- **Type**: Boolean  
- **Description**: To verify SSL for the database connection.
- **Example**: `true`

### `primary_fsa_mrp_id`
- **Type**: Integer  
- **Description**: The emr user ID of the primary FSA "MRP" used for primary FSA patients.  
- **Example**: `999998`

### `primary_fsa_program_id`
- **Type**: Integer  
- **Description**: The emr user ID of the program associated with primary FSA patients.  
- **Example**: `999998`

### `primary_fsa_resident_id`
- **Type**: Integer  
- **Description**: The emr user ID of the primary FSA "resident" dropdown.
- **Example**: `999998`

### `primary_fsa_valid_prefixes`
- **Type**: List of Strings  
- **Description**: A list of valid postal code prefixes for patients who are eligible for primary FSA services.  
- **Example**:
  ```yaml
  - A0A
  - A1A
  - A2A
  ```
### `secondary_fsa_mrp_id`
- **Type**: Integer  
- **Description**: The ID of the secondary FSA MRP for secondary FSA patients.  
- **Example**: `999998`

### `secondary_fsa_msg_to`
- **Type**: Integer  
- **Description**: The user who should receive the message when a secondary FSA patient is processed.  
- **Example**: `123`

### `secondary_fsa_valid_prefixes`
- **Type**: List of Strings  
- **Description**: A list of valid postal code prefixes for patients who are eligible for secondary FSA services.  
- **Example**:
  ```yaml
  - A0A
  - A1A
  - A2A
  ```
### `secondary_fsa_message`
- **Type**: String  
- **Description**: A predefined message indicating that a patient is registered for FSA but is only eligible for a different program 
- **Example**: `Patient registered for primary fsa but eligible for secondary fsa only.`

### `site_name`
- **Type**: String  
- **Description**: The name of the clinic or healthcare facility where PIF processing is taking place.  
- **Example**: `Your Clinic Name`

## Using AIMOA for PIF

You can configure AIMOA to process PIF at any time interval, but the recommended interval is every 20 or 30 minutes. 

#### The basic commands for using PIF with ticklers are listed below.

For this, use site_name and aimee_uid in `config-pif.yaml` so that AIMOA can view the control messages.

**Control tickler message format:**

Eg 1:
```config:pif; skip_ids:250,258,260```
Eg 2:
```config:pif; skip_from:85; skip_to:200;```
Eg 3:
```stop:pif;```
Eg 4:
```aimoa:pif-status;```

**stop: pif;** Only if this message is present will AIMOA stop processing. **Remove to continue processing.** AIMOA will generate this to stop further processing if the error count exceeds the limit specified by `error_tickler_max_count`

**skip_from: 85; skip_to:200;** Will skip processing documents from ID 85 to 200. Not mandatory.

**skip_ids: 250, 251;** Will skip documents with IDs 250 and 251 when used. Not mandatory, use only when required."

**aimoa:pif-status;** AIMOA provides information about the last processed PIF documents. Not mandatory, use only when required."

## Example
**aimoa:pif-status;**
```
Started task at 2026-01-10 13:56:12;Completed task at 2026-01-10 13:56:28;Processed 3 files during execution.
```

## Common Error Notifications

When AIMOA encounters an error, it will notify the error manager or the designated person based on the configurations.
```
Error when processing PIF Id : 123; Firstname , Firstname (DOB #HCN)
```
The above notification occurs when the system encounters an issue, and this message will be sent to error_msg_to. The system will continue processing, but the PIF ID must be reviewed for error correction. Additionally, the demographic will not be created.

```
HCN validation error, please check that the demographic information is accurate and complete. PIF Id : 123; Firstname , Firstname (DOB #HCN)
```
The above notification occurs when the system encounters an HCN validation error, and this message will be sent to error_msg_to. The system will continue processing, but the PIF ID must be reviewed for error correction.

```
Patient registered for primary fsa but eligible for secondary fsa only.
```
The above notification occurs when a patient registers for primary FSA but is only eligible for secondary FSA, and this message will be sent to error_msg_to. The system will continue processing, but the PIF ID must be reviewed for error correction.

The system will also send a notification if the postal code is invalid.


