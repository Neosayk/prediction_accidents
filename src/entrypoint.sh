#!/bin/bash
airflow db init
airflow users create --username datascientest --email datascientest@example.com --firstname Datascientest --lastname Datascientest --role Admin --password datascientest
nohup airflow scheduler > /dev/null 2>&1 &
nohup airflow webserver -p 8080 > /dev/null 2>&1