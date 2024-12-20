# import the libraries
from datetime import timedelta
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# Default arguments
default_args = {
    'owner': 'Bouba_Ismaila',
    'start_date': days_ago(0),
    'email': ['bayolaismaila@gmail.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,  # Fixed syntax
    'email_on_retry': True,    # Fixed syntax
}

# Define the DAG
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='Apache Airflow Final Assignment',
    schedule_interval=timedelta(days=1),
)
# Defining the tasks
# Defining download task
download = BashOperator(
    task_id='download',
   bash_command = (
    'curl "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz" '
    '-o ./dags/finalassignment/tolldata.tgz'
),
    dag=dag,
)

# Defining unzip task
unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command=(
        'tar -xzf /Babayola/airflow-dags/dags/finalassignment/tolldata.tgz '
        '-C /Babayola/airflow-dags/dags/finalassignment/'
    ),
    dag=dag,
)

# Defining csv data extract task
extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command=(
        "cut -d',' -f1-4 /Babayola/airflow-dags/dags/finalassignment/vehicle_data.csv > "
        "/Babayola/airflow-dags/dags/finalassignment/csv_data.csv"
    ),
    dag=dag,
)

# defining tsv data extract task
extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command=(
        "cut -f2,4-5 /Babayola/airflow-dags/dags/finalassignment/tollplaza-data.tsv > "
        "/Babayola/airflow-dags/dags/finalassignment/tsv_data.csv"
    ),
    dag=dag,
)

# Defining extract fixed-width data task using awk
extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command=(
        "echo 'Type of Payment code,Vehicle Code' > /Babayola/airflow-dags/dags/finalassignment/fixed_width_data.csv && "
        "awk '{print substr($0, 44, 9), substr($0, 58, 5)}' /Babayola/airflow-dags/dags/finalassignment/payment-data.txt >> "
        "/Babayola/airflow-dags/dags/finalassignment/fixed_width_data.csv"
    ),
    dag=dag,
)

# Defining consolidate data
consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command=(
        "paste -d ',' /Babayola/airflow-dags/dags/finalassignment/csv_data.csv "
        "/Babayola/airflow-dags/dags/finalassignment/tsv_data.csv "
        "/Babayola/airflow-dags/dags/finalassignment/fixed_width_data.csv > "
        "/Babayola/airflow-dags/dags/finalassignment/extracted_data.csv"
    ),
    dag=dag,
)

#defining transform data task
transform_data = BashOperator(
    task_id='transform_data',
    bash_command=(
        "mkdir -p /Babayola/airflow-dags/dags/finalassignment && "  # Ensure the directory exists
        "cut -d',' -f4 /Babayola/airflow-dags/dags/finalassignment/extracted_data.csv | "  # Extract the 4th column
        "tr '[a-z]' '[A-Z]' > /Babayola/airflow-dags/dags/finalassignment/transformed_data.csv"
    ),
    dag=dag,
)                           

# task pipeline

download >> unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data
